def _register_and_login(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


SAMPLE_RECIPE = {
    "name": "Anti-Inflammatory Salmon Bowl",
    "description": "A kidney-friendly salmon bowl with turmeric rice",
    "ingredients": [
        {"name": "salmon fillet", "quantity": 6, "unit": "oz"},
        {"name": "brown rice", "quantity": 1, "unit": "cup"},
        {"name": "turmeric", "quantity": 1, "unit": "tsp"},
    ],
    "instructions": ["Cook rice with turmeric", "Bake salmon at 400F for 12 min", "Assemble bowl"],
    "prep_time_minutes": 10,
    "cook_time_minutes": 25,
    "difficulty": "intermediate",
    "servings": 2,
    "tags": ["anti-inflammatory", "kidney-friendly"],
    "autoimmune_score": 5,
    "nutrition": {
        "calories": 450,
        "protein": 35,
        "sodium": 200,
        "potassium": 400,
        "phosphorus": 300,
    },
    "source": "seeded",
}


def test_create_recipe(client):
    token = _register_and_login(client)
    response = client.post("/api/recipes", json=SAMPLE_RECIPE, headers=_auth(token))
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Anti-Inflammatory Salmon Bowl"
    assert data["autoimmune_score"] == 5
    assert len(data["ingredients"]) == 3


def test_list_recipes(client):
    token = _register_and_login(client)
    client.post("/api/recipes", json=SAMPLE_RECIPE, headers=_auth(token))
    response = client.get("/api/recipes", headers=_auth(token))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_recipe(client):
    token = _register_and_login(client)
    created = client.post("/api/recipes", json=SAMPLE_RECIPE, headers=_auth(token))
    recipe_id = created.json()["id"]
    response = client.get(f"/api/recipes/{recipe_id}", headers=_auth(token))
    assert response.status_code == 200
    assert response.json()["name"] == "Anti-Inflammatory Salmon Bowl"


def test_filter_recipes_by_tag(client):
    token = _register_and_login(client)
    client.post("/api/recipes", json=SAMPLE_RECIPE, headers=_auth(token))
    recipe2 = SAMPLE_RECIPE.copy()
    recipe2["name"] = "Simple Oatmeal"
    recipe2["tags"] = ["anti-inflammatory"]
    client.post("/api/recipes", json=recipe2, headers=_auth(token))
    response = client.get("/api/recipes?tag=kidney-friendly", headers=_auth(token))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_recipes_by_difficulty(client):
    token = _register_and_login(client)
    client.post("/api/recipes", json=SAMPLE_RECIPE, headers=_auth(token))
    response = client.get("/api/recipes?difficulty=beginner", headers=_auth(token))
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_search_recipes_by_name(client):
    token = _register_and_login(client)
    client.post("/api/recipes", json=SAMPLE_RECIPE, headers=_auth(token))
    response = client.get("/api/recipes?search=salmon", headers=_auth(token))
    assert response.status_code == 200
    assert len(response.json()) == 1
