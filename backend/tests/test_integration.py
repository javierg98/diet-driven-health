from tests.test_meal_plan import _seed_recipes


def test_full_workflow(client, db):
    """Test the complete user journey: register -> profile -> generate plan -> grocery -> log dish."""
    # Register and login
    client.post("/api/auth/register", json={"username": "javier", "password": "test123"})
    resp = client.post("/api/auth/login", data={"username": "javier", "password": "test123"})
    assert resp.status_code == 200
    headers = {"Authorization": f"Bearer " + resp.json()["access_token"]}

    # Create profile
    profile_resp = client.post("/api/profile", json={
        "skill_level": "intermediate",
        "health_conditions": ["lupus"],
        "health_goals": ["anti-inflammatory"],
        "dietary_restrictions": ["low-sodium"],
    }, headers=headers)
    assert profile_resp.status_code == 201

    # Seed recipes
    _seed_recipes(db)

    # Generate meal plan
    plan = client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-09",
    }, headers=headers)
    assert plan.status_code == 201
    plan_id = plan.json()["id"]
    assert len(plan.json()["days"]) == 7

    # Get grocery list
    grocery = client.get(f"/api/grocery/{plan_id}", headers=headers)
    assert grocery.status_code == 200
    assert len(grocery.json()["items"]) > 0

    # Log a dish
    recipe_id = plan.json()["days"][0]["breakfast"]
    log = client.post("/api/dish-log", json={
        "recipe_id": recipe_id,
        "rating": 5,
        "notes": "Great!",
        "would_make_again": True,
    }, headers=headers)
    assert log.status_code == 201

    # Parse a recipe
    parsed = client.post("/api/upload/parse", json={
        "text": "My Recipe\n\nIngredients:\n- 1 cup rice\n\nInstructions:\n1. Cook rice",
    }, headers=headers)
    assert parsed.status_code == 200
    assert parsed.json()["name"] == "My Recipe"


def _register_and_login(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_v2_full_workflow(client, db):
    """Test the v2 workflow: register, preferences, meal plan with goals, log dish, health trend."""
    _seed_recipes(db)
    headers = _register_and_login(client)

    # Submit likes
    resp = client.post("/api/food/save", json={
        "detected_type": "likes",
        "recipes": [],
        "entries": [],
        "preferences": [
            {"type": "like", "value": "salmon", "category": "ingredient"},
            {"type": "like", "value": "rice", "category": "ingredient"},
        ],
    }, headers=headers)
    assert resp.status_code == 201

    # Submit dislikes
    resp = client.post("/api/food/save", json={
        "detected_type": "dislikes",
        "recipes": [],
        "entries": [],
        "preferences": [
            {"type": "dislike", "value": "liver", "category": "ingredient"},
        ],
    }, headers=headers)
    assert resp.status_code == 201

    # Generate meal plan with goals
    resp = client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-16",
        "meal_types": ["lunch", "dinner"],
        "cooking_sessions": 5,
    }, headers=headers)
    assert resp.status_code == 201
    plan = resp.json()
    assert len(plan["days"]) == 7
    for day in plan["days"]:
        assert day["breakfast"] is None

    # Log a dish
    recipe_id = plan["days"][0]["lunch"]
    resp = client.post("/api/dish-log", json={
        "recipe_id": recipe_id,
        "rating": 4,
        "notes": "Great!",
        "would_make_again": True,
    }, headers=headers)
    assert resp.status_code == 201

    # Check health trend
    resp = client.get("/api/admin/health-trend", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total_logs"] == 1

    # Check preferences stored
    resp = client.get("/api/food/preferences", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 3
