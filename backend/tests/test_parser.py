from app.services.recipe_parser import parse_recipe_text


def test_parse_basic_recipe():
    text = """
    Turmeric Chicken

    Ingredients:
    - 1 lb chicken breast
    - 2 tsp turmeric
    - 1 tbsp olive oil
    - 1/2 tsp salt

    Instructions:
    1. Season chicken with turmeric and salt
    2. Heat olive oil in a pan
    3. Cook chicken for 6 minutes per side
    """
    result = parse_recipe_text(text)
    assert result["name"] == "Turmeric Chicken"
    assert len(result["ingredients"]) >= 3
    assert len(result["instructions"]) >= 3


def test_parse_recipe_without_headers():
    text = """
    Simple Salmon

    6 oz salmon fillet
    1 tsp lemon juice
    salt and pepper

    Bake at 400F for 12 minutes.
    Squeeze lemon on top.
    """
    result = parse_recipe_text(text)
    assert result["name"] != ""
    assert len(result["ingredients"]) >= 1


def test_parse_returns_all_fields():
    text = """
    Test Recipe

    Ingredients:
    - 1 cup rice

    Instructions:
    1. Cook rice
    """
    result = parse_recipe_text(text)
    assert "name" in result
    assert "ingredients" in result
    assert "instructions" in result
    assert "source" in result
    assert result["source"] == "personal"


def test_upload_api(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/upload/parse", json={
        "text": """
        My Favorite Soup

        Ingredients:
        - 2 cups chicken broth
        - 1 cup carrots, diced
        - 1/2 cup celery

        Instructions:
        1. Bring broth to boil
        2. Add vegetables
        3. Simmer for 20 minutes
        """,
    }, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Favorite Soup"
