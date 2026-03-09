import json
import os
import random

from sqlalchemy.orm import Session

from app.models.recipe import Recipe

DEFAULT_WEIGHTS = {
    "preference_match": 0.30,
    "ingredient_overlap": 0.20,
    "cost_efficiency": 0.15,
    "autoimmune_friendliness": 0.15,
    "cooking_time_fit": 0.10,
    "variety": 0.10,
}

WEIGHTS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "recommendation_weights.json")


def _load_weights() -> dict:
    """Read weights from JSON file, falling back to DEFAULT_WEIGHTS."""
    try:
        with open(WEIGHTS_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT_WEIGHTS)


def _get_ingredient_names(recipe: Recipe) -> list[str]:
    """Extract lowercase ingredient names from a recipe."""
    ingredients = recipe.ingredients or []
    return [ing.get("name", "").lower() for ing in ingredients if isinstance(ing, dict)]


def score_recipe(
    recipe: Recipe,
    likes: list[str],
    dislikes: list[str],
    planned_ingredients: set[str],
    weights: dict,
    max_cook_time: int | None = None,
    planned_tags: set[str] | None = None,
) -> float:
    """Score a recipe on a 0-100 scale using weighted criteria."""
    ingredient_names = _get_ingredient_names(recipe)

    # --- preference_match: baseline 50, +bonus for likes, -25 per dislike ---
    pref_score = 50.0
    for like in likes:
        like_lower = like.lower()
        if any(like_lower in name for name in ingredient_names):
            pref_score += 25.0
    for dislike in dislikes:
        dislike_lower = dislike.lower()
        if any(dislike_lower in name for name in ingredient_names):
            pref_score -= 25.0
    pref_score = max(0.0, min(100.0, pref_score))

    # --- ingredient_overlap: ratio of shared ingredients * 100, 50 if nothing planned ---
    if planned_ingredients:
        planned_lower = {p.lower() for p in planned_ingredients}
        if ingredient_names:
            overlap_count = sum(1 for name in ingredient_names if name in planned_lower)
            overlap_score = (overlap_count / len(ingredient_names)) * 100.0
        else:
            overlap_score = 50.0
    else:
        overlap_score = 50.0

    # --- cost_efficiency: 100 - unique_new_ingredients * 10 ---
    if planned_ingredients:
        planned_lower = {p.lower() for p in planned_ingredients}
        new_ingredients = sum(1 for name in ingredient_names if name not in planned_lower)
    else:
        new_ingredients = len(ingredient_names)
    cost_score = max(0.0, 100.0 - new_ingredients * 10.0)

    # --- autoimmune_friendliness: (autoimmune_score / 5) * 100 ---
    ai_score_val = recipe.autoimmune_score if recipe.autoimmune_score is not None else 3
    autoimmune_score = (ai_score_val / 5.0) * 100.0

    # --- cooking_time_fit: 100 if within limit, decreasing penalty beyond ---
    total_time = (recipe.prep_time_minutes or 0) + (recipe.cook_time_minutes or 0)
    if max_cook_time is None:
        cook_score = 80.0  # neutral if no constraint
    elif total_time <= max_cook_time:
        cook_score = 100.0
    else:
        overage = total_time - max_cook_time
        cook_score = max(0.0, 100.0 - overage * 5.0)

    # --- variety: 100 - overlap_with_planned_tags * 20 ---
    if planned_tags:
        recipe_tags = set(recipe.tags or [])
        tag_overlap = len(recipe_tags & planned_tags)
        variety_score = max(0.0, 100.0 - tag_overlap * 20.0)
    else:
        variety_score = 80.0  # neutral if nothing planned

    # --- weighted sum ---
    final = (
        weights.get("preference_match", 0.30) * pref_score
        + weights.get("ingredient_overlap", 0.20) * overlap_score
        + weights.get("cost_efficiency", 0.15) * cost_score
        + weights.get("autoimmune_friendliness", 0.15) * autoimmune_score
        + weights.get("cooking_time_fit", 0.10) * cook_score
        + weights.get("variety", 0.10) * variety_score
    )
    return final


def generate_meal_plan(
    db: Session,
    skill_level: str = "intermediate",
    dietary_restrictions: list[str] | None = None,
    tags: list[str] | None = None,
    meal_types: list[str] | None = None,
    cooking_sessions: int | None = None,
    weekly_budget: float | None = None,
    batch_cooking: bool = False,
    likes: list[str] | None = None,
    dislikes: list[str] | None = None,
) -> list[dict]:
    """Generate a 7-day meal plan using weighted scoring. Returns list of dicts with meal_type: recipe_id."""
    difficulty_map = {
        "beginner": ["beginner"],
        "intermediate": ["beginner", "intermediate"],
        "advanced": ["beginner", "intermediate", "advanced"],
    }
    allowed_difficulties = difficulty_map.get(skill_level, ["beginner", "intermediate"])

    query = db.query(Recipe).filter(Recipe.difficulty.in_(allowed_difficulties))
    recipes = query.all()

    # Backward compat: filter by tags if provided
    if tags:
        recipes = [r for r in recipes if any(t in (r.tags or []) for t in tags)]

    if not recipes:
        # Fallback: return empty structure
        all_meals = meal_types or ["breakfast", "lunch", "dinner"]
        return [{mt: None for mt in all_meals} for _ in range(7)]

    weights = _load_weights()
    likes = likes or []
    dislikes = dislikes or []
    all_meals = meal_types or ["breakfast", "lunch", "dinner"]

    planned_ingredients: set[str] = set()
    planned_tags: set[str] = set()
    used_ids: set[int] = set()
    used_id_list: list[int] = []  # ordered list for cooking_sessions reuse
    plan: list[dict] = []

    for _day in range(7):
        day_meals: dict = {}
        for meal_type in ["breakfast", "lunch", "dinner"]:
            if meal_type not in all_meals:
                day_meals[meal_type] = None
                continue

            # If cooking_sessions limit is hit, reuse from already-used recipes
            if cooking_sessions is not None and len(used_ids) >= cooking_sessions:
                reuse_id = random.choice(used_id_list)
                day_meals[meal_type] = reuse_id
                continue

            # Score all candidates
            scored: list[tuple[float, Recipe]] = []
            for r in recipes:
                base_score = score_recipe(
                    r, likes, dislikes, planned_ingredients, weights,
                    planned_tags=planned_tags,
                )
                # Penalize already-used recipes
                if r.id in used_ids:
                    base_score *= 0.3
                # Add small random jitter
                jitter = random.uniform(0, 5)
                scored.append((base_score + jitter, r))

            scored.sort(key=lambda x: x[0], reverse=True)
            chosen = scored[0][1]

            used_ids.add(chosen.id)
            used_id_list.append(chosen.id)
            day_meals[meal_type] = chosen.id

            # Track ingredients and tags for future scoring
            for name in _get_ingredient_names(chosen):
                planned_ingredients.add(name)
            for tag in (chosen.tags or []):
                planned_tags.add(tag)

        # Only include selected meal types in output
        if meal_types:
            day_meals = {k: v for k, v in day_meals.items() if k in all_meals}
        plan.append(day_meals)

    return plan


def get_swap_recipe(
    db: Session,
    excluded_ids: list[int],
    skill_level: str = "intermediate",
    likes: list[str] | None = None,
    dislikes: list[str] | None = None,
) -> int | None:
    """Get a single recipe ID not in excluded_ids, chosen from top 3 by score."""
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

    weights = _load_weights()
    likes = likes or []
    dislikes = dislikes or []

    scored = []
    for r in recipes:
        s = score_recipe(r, likes, dislikes, set(), weights)
        scored.append((s, r))
    scored.sort(key=lambda x: x[0], reverse=True)

    top_n = scored[:3]
    chosen = random.choice(top_n)
    return chosen[1].id
