from app.services.grocery import consolidate_ingredients, estimate_cost, STORE_SECTIONS, estimate_purchase_cost, PURCHASE_UNITS


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


def test_purchase_units_has_common_items():
    assert "strawberries" in PURCHASE_UNITS
    assert "rice" in PURCHASE_UNITS
    assert PURCHASE_UNITS["strawberries"]["cost"] > 0


def test_estimate_purchase_cost_known_item():
    items = [{"name": "strawberries", "quantity": 1, "unit": "cup"}]
    cost = estimate_purchase_cost(items)
    assert cost == PURCHASE_UNITS["strawberries"]["cost"]


def test_estimate_purchase_cost_shared_ingredient():
    items = [
        {"name": "rice", "quantity": 1, "unit": "cup"},
        {"name": "rice", "quantity": 2, "unit": "cup"},
    ]
    cost = estimate_purchase_cost(items)
    assert cost == PURCHASE_UNITS["rice"]["cost"]


def test_estimate_purchase_cost_unknown_item():
    items = [{"name": "exotic_spice_xyz", "quantity": 2, "unit": "tbsp"}]
    cost = estimate_purchase_cost(items)
    assert cost > 0


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
