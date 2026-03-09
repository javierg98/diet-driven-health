from sqlalchemy.orm import Session

from app.models.meal_plan import MealPlan
from app.models.recipe import Recipe

STORE_SECTIONS = {
    "produce": ["lettuce", "spinach", "kale", "tomato", "onion", "garlic", "ginger",
                 "avocado", "lemon", "lime", "bell pepper", "cucumber", "carrot",
                 "celery", "broccoli", "cauliflower", "sweet potato", "zucchini",
                 "berries", "blueberries", "strawberries", "apple", "banana"],
    "protein": ["salmon", "chicken", "turkey", "beef", "shrimp", "tofu", "egg",
                "tuna", "cod", "tilapia"],
    "dairy": ["milk", "yogurt", "cheese", "butter", "cream"],
    "grains": ["rice", "oats", "quinoa", "bread", "pasta", "tortilla", "flour"],
    "pantry": ["olive oil", "coconut oil", "turmeric", "cumin", "paprika",
               "cinnamon", "honey", "maple syrup", "soy sauce", "vinegar",
               "salt", "pepper", "broth", "stock", "beans", "lentils",
               "chickpeas", "nuts", "almonds", "walnuts"],
    "frozen": ["frozen berries", "frozen vegetables"],
    "other": [],
}

COST_ESTIMATES = {
    "oz": 0.50, "lb": 5.00, "cup": 1.00, "tbsp": 0.15, "tsp": 0.05,
    "piece": 1.00, "clove": 0.10, "can": 1.50, "bunch": 2.00,
    "head": 2.50, "slice": 0.30,
}


# Purchase-unit costs: what you'd actually buy at the store
PURCHASE_UNITS = {
    # Produce
    "strawberries": {"unit": "1 pint", "cost": 4.00},
    "blueberries": {"unit": "1 pint", "cost": 4.50},
    "berries": {"unit": "1 pint", "cost": 4.00},
    "spinach": {"unit": "1 bag (5oz)", "cost": 3.50},
    "kale": {"unit": "1 bunch", "cost": 3.00},
    "arugula": {"unit": "1 bag (5oz)", "cost": 3.50},
    "lettuce": {"unit": "1 head", "cost": 2.00},
    "avocado": {"unit": "1 each", "cost": 1.50},
    "lemon": {"unit": "1 each", "cost": 0.75},
    "lime": {"unit": "1 each", "cost": 0.50},
    "tomato": {"unit": "1 lb", "cost": 2.00},
    "onion": {"unit": "1 each", "cost": 1.00},
    "garlic": {"unit": "1 head", "cost": 0.75},
    "ginger": {"unit": "1 piece", "cost": 1.50},
    "bell pepper": {"unit": "1 each", "cost": 1.25},
    "cucumber": {"unit": "1 each", "cost": 1.00},
    "carrot": {"unit": "1 bag (1lb)", "cost": 1.50},
    "celery": {"unit": "1 bunch", "cost": 2.00},
    "broccoli": {"unit": "1 head", "cost": 2.50},
    "cauliflower": {"unit": "1 head", "cost": 3.00},
    "sweet potato": {"unit": "1 each", "cost": 1.50},
    "zucchini": {"unit": "1 each", "cost": 1.25},
    "banana": {"unit": "1 bunch", "cost": 1.50},
    "apple": {"unit": "1 each", "cost": 1.00},
    # Protein
    "salmon": {"unit": "1 lb", "cost": 10.00},
    "chicken": {"unit": "1 lb", "cost": 5.00},
    "chicken breast": {"unit": "1 lb", "cost": 5.50},
    "turkey": {"unit": "1 lb", "cost": 6.00},
    "ground turkey": {"unit": "1 lb", "cost": 6.00},
    "beef": {"unit": "1 lb", "cost": 7.00},
    "shrimp": {"unit": "1 lb", "cost": 9.00},
    "tofu": {"unit": "1 block (14oz)", "cost": 2.50},
    "egg": {"unit": "1 dozen", "cost": 4.00},
    "eggs": {"unit": "1 dozen", "cost": 4.00},
    "tuna": {"unit": "1 can", "cost": 2.00},
    "cod": {"unit": "1 lb", "cost": 8.00},
    # Dairy
    "milk": {"unit": "1/2 gallon", "cost": 3.00},
    "yogurt": {"unit": "32oz container", "cost": 4.50},
    "cheese": {"unit": "8oz block", "cost": 4.00},
    "butter": {"unit": "1 stick", "cost": 2.00},
    # Grains
    "rice": {"unit": "2lb bag", "cost": 3.00},
    "oats": {"unit": "18oz canister", "cost": 3.50},
    "quinoa": {"unit": "1lb bag", "cost": 5.00},
    "bread": {"unit": "1 loaf", "cost": 3.50},
    "tortilla": {"unit": "1 pack (10ct)", "cost": 3.00},
    "flour": {"unit": "5lb bag", "cost": 4.00},
    "pasta": {"unit": "1lb box", "cost": 1.50},
    # Pantry
    "olive oil": {"unit": "16oz bottle", "cost": 6.00},
    "coconut oil": {"unit": "14oz jar", "cost": 7.00},
    "turmeric": {"unit": "1 jar", "cost": 4.00},
    "cumin": {"unit": "1 jar", "cost": 3.50},
    "cinnamon": {"unit": "1 jar", "cost": 3.50},
    "honey": {"unit": "12oz bottle", "cost": 5.00},
    "maple syrup": {"unit": "12oz bottle", "cost": 7.00},
    "soy sauce": {"unit": "10oz bottle", "cost": 3.00},
    "broth": {"unit": "32oz carton", "cost": 3.00},
    "stock": {"unit": "32oz carton", "cost": 3.00},
    "beans": {"unit": "1 can (15oz)", "cost": 1.25},
    "chickpeas": {"unit": "1 can (15oz)", "cost": 1.25},
    "lentils": {"unit": "1lb bag", "cost": 2.00},
    "almonds": {"unit": "8oz bag", "cost": 5.00},
    "walnuts": {"unit": "8oz bag", "cost": 6.00},
    "chia seeds": {"unit": "6oz bag", "cost": 5.00},
}

DEFAULT_PURCHASE_COST = 3.00


def estimate_purchase_cost(items: list[dict]) -> float:
    """Estimate grocery cost using purchase-unit prices.
    Each unique ingredient is counted once (buy the package, not per-unit)."""
    seen = set()
    total = 0.0
    for item in items:
        name_lower = item["name"].lower().strip()
        if name_lower in seen:
            continue
        seen.add(name_lower)
        if name_lower in PURCHASE_UNITS:
            total += PURCHASE_UNITS[name_lower]["cost"]
        else:
            matched = False
            for key, data in PURCHASE_UNITS.items():
                if key in name_lower or name_lower in key:
                    total += data["cost"]
                    matched = True
                    break
            if not matched:
                total += DEFAULT_PURCHASE_COST
    return round(total, 2)


def consolidate_ingredients(ingredients: list[dict]) -> list[dict]:
    consolidated = {}
    for item in ingredients:
        key = (item["name"].lower().strip(), item["unit"].lower().strip())
        if key in consolidated:
            consolidated[key]["quantity"] += item["quantity"]
        else:
            consolidated[key] = {
                "name": item["name"],
                "quantity": item["quantity"],
                "unit": item["unit"],
            }
    return list(consolidated.values())


def categorize_item(name: str) -> str:
    name_lower = name.lower()
    for section, keywords in STORE_SECTIONS.items():
        if section == "other":
            continue
        for keyword in keywords:
            if keyword in name_lower:
                return section
    return "other"


def estimate_cost(items: list[dict]) -> float:
    total = 0.0
    for item in items:
        unit = item["unit"].lower().strip()
        per_unit = COST_ESTIMATES.get(unit, 1.00)
        total += item["quantity"] * per_unit
    return round(total, 2)


def generate_grocery_list(db: Session, plan_id: int, user_id: int) -> dict:
    plan = db.query(MealPlan).filter(
        MealPlan.id == plan_id, MealPlan.user_id == user_id
    ).first()
    if not plan:
        return None

    all_ingredients = []
    recipe_ids = set()
    for day in plan.days:
        for meal_type in ["breakfast", "lunch", "dinner"]:
            recipe_ids.add(day[meal_type])

    recipes = db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
    for recipe in recipes:
        for ingredient in recipe.ingredients:
            all_ingredients.append(ingredient)

    consolidated = consolidate_ingredients(all_ingredients)

    items = []
    for item in consolidated:
        items.append({
            **item,
            "section": categorize_item(item["name"]),
            "estimated_cost": round(item["quantity"] * COST_ESTIMATES.get(item["unit"].lower().strip(), 1.00), 2),
            "checked": False,
        })

    items.sort(key=lambda x: x["section"])

    return {
        "meal_plan_id": plan_id,
        "items": items,
        "total_estimated_cost": estimate_cost(consolidated),
    }
