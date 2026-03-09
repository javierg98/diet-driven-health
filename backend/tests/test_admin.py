import json
from unittest.mock import patch

from app.models.dish_log import DishLog
from app.models.meal_plan import MealPlan
from app.models.recipe import Recipe


def _register_and_login(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_get_skill_results_empty(client):
    headers = _register_and_login(client)
    resp = client.get("/api/admin/skill-results", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "user_preferences" in data
    assert "user_memory" in data
    assert "recommendation_weights" in data
    assert data["user_preferences"] is None


def test_get_skill_results_with_data(client, tmp_path):
    headers = _register_and_login(client)
    prefs = {"generated_at": "2026-03-09", "top_ingredients": ["salmon"]}
    prefs_file = tmp_path / "user_preferences.json"
    prefs_file.write_text(json.dumps(prefs))

    with patch("app.api.admin.DATA_DIR", str(tmp_path)):
        resp = client.get("/api/admin/skill-results", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_preferences"]["top_ingredients"] == ["salmon"]


def test_get_health_trend(client, db):
    headers = _register_and_login(client)
    recipe = Recipe(
        name="Test", description="", ingredients=[], instructions=[],
        difficulty="intermediate", servings=2, tags=[], autoimmune_score=4,
        nutrition={}, source="seeded",
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    for i in range(3):
        log = DishLog(
            user_id=1, recipe_id=recipe.id, rating=4, notes="",
            would_make_again=True,
        )
        db.add(log)
    db.commit()

    resp = client.get("/api/admin/health-trend", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "weekly_scores" in data
    assert "overall_average" in data
    assert data["overall_average"] == 4.0
