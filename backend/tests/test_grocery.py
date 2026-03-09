from app.services.grocery import consolidate_ingredients, estimate_cost, STORE_SECTIONS


def test_consolidate_ingredients():
    ingredients = [
        {"name": "salmon fillet", "quantity": 6, "unit": "oz"},
        {"name": "salmon fillet", "quantity": 6, "unit": "oz"},
        {"name": "brown rice", "quantity": 1, "unit": "cup"},
        {"name": "brown rice", "quantity": 2, "unit": "cup"},
    ]
    result = consolidate_ingredients(ingredients)
    assert len(result) == 2
    salmon = next(i for i in result if i["name"] == "salmon fillet")
    assert salmon["quantity"] == 12
    rice = next(i for i in result if i["name"] == "brown rice")
    assert rice["quantity"] == 3


def test_estimate_cost():
    items = [
        {"name": "salmon fillet", "quantity": 12, "unit": "oz"},
        {"name": "brown rice", "quantity": 3, "unit": "cup"},
    ]
    total = estimate_cost(items)
    assert total > 0


def test_store_sections():
    assert "produce" in STORE_SECTIONS
    assert "protein" in STORE_SECTIONS


def test_grocery_api(client, db):
    from tests.test_meal_plan import _seed_recipes, _register_login_and_profile
    _seed_recipes(db)
    headers = _register_login_and_profile(client)
    created = client.post("/api/meal-plans/generate", json={
        "week_start": "2026-03-09",
    }, headers=headers)
    plan_id = created.json()["id"]
    response = client.get(f"/api/grocery/{plan_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_estimated_cost" in data
