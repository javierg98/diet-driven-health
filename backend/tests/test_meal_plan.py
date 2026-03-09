from app.models.recipe import Recipe
from app.schemas.meal_plan import MealPlanGenerate
from app.services.recommender import generate_meal_plan


def _register_login_and_profile(client):
    client.post("/api/auth/register", json={
        "username": "javier", "password": "testpass123",
    })
    resp = client.post("/api/auth/login", data={
        "username": "javier", "password": "testpass123",
    })
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/api/profile", json={
        "skill_level": "intermediate",
        "health_conditions": ["lupus"],
        "health_goals": ["anti-inflammatory"],
        "dietary_restrictions": ["low-sodium"],
    }, headers=headers)
    return headers


def _seed_recipes(db):
    for i in range(25):
        recipe = Recipe(
            name=f"Recipe {i}",
            description=f"Test recipe {i}",
            ingredients=[{"name": "ingredient", "quantity": 1, "unit": "cup"}],
            instructions=["Step 1"],
            prep_time_minutes=15,
            cook_time_minutes=20,
            difficulty="intermediate",
            servings=2,
            tags=["anti-inflammatory"],
            autoimmune_score=4,
            nutrition={"calories": 400, "protein": 30, "sodium": 300, "potassium": 350, "phosphorus": 250},
            source="seeded",
        )
        db.add(recipe)
    db.commit()


def test_generate_meal_plan_service(db):
    _seed_recipes(db)
    plan = generate_meal_plan(db, skill_level="intermediate", dietary_restrictions=["low-sodium"], tags=["anti-inflammatory"])
    assert len(plan) == 7
    for day in plan:
        assert "breakfast" in day
        assert "lunch" in day
        assert "dinner" in day


def test_generate_meal_plan_no_repeats(db):
    _seed_recipes(db)
    plan = generate_meal_plan(db, skill_level="intermediate", dietary_restrictions=[], tags=[])
    recipe_ids = []
    for day in plan:
        for meal in ["breakfast", "lunch", "dinner"]:
            recipe_ids.append(day[meal])
    assert len(recipe_ids) == len(set(recipe_ids))


def test_create_meal_plan_api(client, db):
    _seed_recipes(db)
    headers = _register_login_and_profile(client)
    response = client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-09",
    }, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert len(data["days"]) == 7


def test_list_meal_plans(client, db):
    _seed_recipes(db)
    headers = _register_login_and_profile(client)
    client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-09",
    }, headers=headers)
    response = client.get("/api/meal-plans", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_swap_meal(client, db):
    _seed_recipes(db)
    headers = _register_login_and_profile(client)
    created = client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-09",
    }, headers=headers)
    plan_id = created.json()["id"]
    original_recipe = created.json()["days"][0]["breakfast"]
    response = client.put(f"/api/meal-plans/{plan_id}/swap", json={
        "day_index": 0,
        "meal_type": "breakfast",
    }, headers=headers)
    assert response.status_code == 200
    new_recipe = response.json()["days"][0]["breakfast"]
    assert new_recipe != original_recipe


def test_meal_plan_generate_with_goals():
    req = MealPlanGenerate(
        week_start="2026-03-09",
        meal_types=["lunch", "dinner"],
        cooking_sessions=4,
        weekly_budget=75.0,
        batch_cooking=True,
    )
    assert req.meal_types == ["lunch", "dinner"]
    assert req.cooking_sessions == 4
    assert req.weekly_budget == 75.0
    assert req.batch_cooking is True


def test_meal_plan_generate_defaults():
    req = MealPlanGenerate(week_start="2026-03-09")
    assert req.meal_types == ["breakfast", "lunch", "dinner"]
    assert req.cooking_sessions is None
    assert req.weekly_budget is None
    assert req.batch_cooking is False
