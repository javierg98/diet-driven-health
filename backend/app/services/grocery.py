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
