def _register_and_login(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_parse_submission_likes(client):
    headers = _register_and_login(client)
    resp = client.post("/api/food/parse", json={
        "text": "Thai curry, avocado, lemon",
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["detected_type"] == "likes"
    assert len(data["preferences"]) == 3


def test_parse_submission_with_override(client):
    headers = _register_and_login(client)
    resp = client.post("/api/food/parse", json={
        "text": "avocado, salmon",
        "submission_type": "dislikes",
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["detected_type"] == "dislikes"


def test_save_preferences(client):
    headers = _register_and_login(client)
    resp = client.post("/api/food/save", json={
        "detected_type": "likes",
        "recipes": [],
        "entries": [],
        "preferences": [
            {"type": "like", "value": "avocado", "category": "ingredient"},
            {"type": "like", "value": "thai curry", "category": "cuisine"},
        ],
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["saved_preferences"] == 2


def test_save_food_entries(client):
    headers = _register_and_login(client)
    resp = client.post("/api/food/save", json={
        "detected_type": "past_meals",
        "recipes": [],
        "entries": [
            {"description": "Salmon with rice", "dish_name": "Salmon with rice", "detected_ingredients": ["salmon", "rice"]},
        ],
        "preferences": [],
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["saved_entries"] == 1


def test_get_preferences(client):
    headers = _register_and_login(client)
    client.post("/api/food/save", json={
        "detected_type": "likes",
        "recipes": [],
        "entries": [],
        "preferences": [
            {"type": "like", "value": "avocado", "category": "ingredient"},
        ],
    }, headers=headers)
    resp = client.get("/api/food/preferences", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["value"] == "avocado"


def test_get_food_entries(client):
    headers = _register_and_login(client)
    client.post("/api/food/save", json={
        "detected_type": "past_meals",
        "recipes": [],
        "entries": [
            {"description": "Salmon dinner", "dish_name": "Salmon", "detected_ingredients": ["salmon"]},
        ],
        "preferences": [],
    }, headers=headers)
    resp = client.get("/api/food/entries", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
