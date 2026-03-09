import random

from sqlalchemy.orm import Session

from app.models.recipe import Recipe


def generate_meal_plan(
    db: Session,
    skill_level: str = "intermediate",
    dietary_restrictions: list[str] | None = None,
    tags: list[str] | None = None,
) -> list[dict]:
    """Generate a 7-day meal plan. Returns list of dicts with breakfast/lunch/dinner recipe IDs."""
    difficulty_map = {
        "beginner": ["beginner"],
        "intermediate": ["beginner", "intermediate"],
        "advanced": ["beginner", "intermediate", "advanced"],
    }
    allowed_difficulties = difficulty_map.get(skill_level, ["beginner", "intermediate"])

    query = db.query(Recipe).filter(Recipe.difficulty.in_(allowed_difficulties))
    recipes = query.all()

    if tags:
        recipes = [r for r in recipes if any(t in (r.tags or []) for t in tags)]

    random.shuffle(recipes)
    plan = []
    used_ids = set()
    recipe_pool = list(recipes)

    for day in range(7):
        day_meals = {}
        for meal_type in ["breakfast", "lunch", "dinner"]:
            chosen = None
            for r in recipe_pool:
                if r.id not in used_ids:
                    chosen = r
                    break
            if chosen is None:
                chosen = random.choice(recipe_pool)
            used_ids.add(chosen.id)
            day_meals[meal_type] = chosen.id
        plan.append(day_meals)

    return plan


def get_swap_recipe(
    db: Session,
    excluded_ids: list[int],
    skill_level: str = "intermediate",
) -> int | None:
    """Get a single recipe ID not in excluded_ids."""
    difficulty_map = {
        "beginner": ["beginner"],
        "intermediate": ["beginner", "intermediate"],
        "advanced": ["beginner", "intermediate", "advanced"],
    }
    allowed = difficulty_map.get(skill_level, ["beginner", "intermediate"])
    recipes = (
        db.query(Recipe)
        .filter(Recipe.difficulty.in_(allowed), ~Recipe.id.in_(excluded_ids))
        .all()
    )
    if not recipes:
        recipes = db.query(Recipe).filter(~Recipe.id.in_(excluded_ids)).all()
    if not recipes:
        return None
    return random.choice(recipes).id
