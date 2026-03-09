from tests.test_recipes import SAMPLE_RECIPE


def _setup(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    recipe = client.post("/api/recipes", json=SAMPLE_RECIPE, headers=headers).json()
    return headers, recipe["id"]


def test_log_dish(client):
    headers, recipe_id = _setup(client)
    response = client.post("/api/dish-log", json={
        "recipe_id": recipe_id,
        "rating": 5,
        "notes": "Delicious and easy!",
        "would_make_again": True,
    }, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["rating"] == 5
    assert data["would_make_again"] is True


def test_list_dish_logs(client):
    headers, recipe_id = _setup(client)
    client.post("/api/dish-log", json={
        "recipe_id": recipe_id,
        "rating": 4,
        "notes": "Good",
        "would_make_again": True,
    }, headers=headers)
    response = client.get("/api/dish-log", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_favorites(client):
    headers, recipe_id = _setup(client)
    client.post("/api/dish-log", json={
        "recipe_id": recipe_id,
        "rating": 5,
        "notes": "Love it",
        "would_make_again": True,
    }, headers=headers)
    response = client.get("/api/dish-log/favorites", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
