"""Fetch recipes from TheMealDB API and transform to our schema."""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

# Areas and categories to fetch
AREAS = ["Mexican", "Italian", "Greek", "French", "Moroccan", "Turkish",
         "Spanish", "American", "British", "Chinese", "Japanese", "Thai",
         "Vietnamese", "Indian", "Irish", "Canadian", "Croatian", "Dutch",
         "Egyptian", "Filipino", "Jamaican", "Kenyan", "Malaysian",
         "Polish", "Portuguese", "Russian", "Tunisian", "Unknown"]

# Map TheMealDB areas to our cuisine tags
CUISINE_MAP = {
    "Mexican": "mexican",
    "Italian": "mediterranean",
    "Greek": "mediterranean",
    "French": "mediterranean",
    "Moroccan": "mediterranean",
    "Turkish": "mediterranean",
    "Spanish": "mediterranean",
    "American": "american",
    "British": "american",
    "Chinese": "asian",
    "Japanese": "asian",
    "Thai": "asian",
    "Vietnamese": "asian",
    "Indian": "indian",
}

# Units we recognize
UNIT_PATTERNS = [
    "tbsp", "tsp", "cup", "cups", "oz", "lb", "lbs", "g", "kg", "ml", "l",
    "piece", "pieces", "clove", "cloves", "can", "cans", "bunch", "head",
    "slice", "slices", "pinch", "handful", "sprig", "sprigs",
]


def fetch_json(url: str) -> dict | None:
    """Fetch JSON from URL with retry."""
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except (urllib.error.URLError, TimeoutError):
            if attempt < 2:
                time.sleep(1)
    return None


def fetch_meals_by_area(area: str) -> list[dict]:
    """Fetch all meals for a given area."""
    data = fetch_json(f"{BASE_URL}/filter.php?a={area}")
    if not data or not data.get("meals"):
        return []
    return data["meals"]


def fetch_meal_detail(meal_id: str) -> dict | None:
    """Fetch full meal details by ID."""
    data = fetch_json(f"{BASE_URL}/lookup.php?i={meal_id}")
    if not data or not data.get("meals"):
        return None
    return data["meals"][0]


def parse_ingredient_measure(measure: str, ingredient: str) -> dict:
    """Parse a TheMealDB measure string into quantity + unit."""
    measure = (measure or "").strip()
    ingredient = (ingredient or "").strip().lower()

    if not measure:
        return {"name": ingredient, "quantity": 1, "unit": "piece"}

    # Handle fractions like "1/2"
    match = re.match(r"(\d+(?:/\d+)?(?:\.\d+)?)\s*(.*)", measure)
    if match:
        qty_str = match.group(1)
        unit_part = match.group(2).strip().lower()

        if "/" in qty_str:
            parts = qty_str.split("/")
            quantity = float(parts[0]) / float(parts[1])
        else:
            quantity = float(qty_str)

        # Find known unit
        unit = "piece"
        for u in UNIT_PATTERNS:
            if unit_part.startswith(u):
                unit = u.rstrip("s")  # normalize plural
                break

        return {"name": ingredient, "quantity": quantity, "unit": unit}

    return {"name": ingredient, "quantity": 1, "unit": "piece"}


def transform_meal(meal: dict, area: str) -> dict | None:
    """Transform a TheMealDB meal to our Recipe schema."""
    if not meal.get("strMeal"):
        return None

    # Extract ingredients
    ingredients = []
    for i in range(1, 21):
        ing = (meal.get(f"strIngredient{i}") or "").strip()
        measure = (meal.get(f"strMeasure{i}") or "").strip()
        if ing:
            ingredients.append(parse_ingredient_measure(measure, ing))

    if not ingredients:
        return None

    # Parse instructions
    raw_instructions = (meal.get("strInstructions") or "").strip()
    if not raw_instructions:
        return None

    # Split by newlines or numbered steps
    steps = re.split(r"\r?\n|\. (?=\d)", raw_instructions)
    instructions = []
    for step in steps:
        step = re.sub(r"^\d+[\.\)]\s*", "", step).strip()
        if step and len(step) > 10:
            instructions.append(step)

    if not instructions:
        instructions = [raw_instructions]

    # Estimate difficulty from ingredient count
    difficulty = "beginner"
    if len(ingredients) > 10:
        difficulty = "advanced"
    elif len(ingredients) > 5:
        difficulty = "intermediate"

    # Build cuisine tags
    tags = []
    cuisine = CUISINE_MAP.get(area, "other")
    if cuisine != "other":
        tags.append(cuisine)

    # Meal type tags from TheMealDB category/tags
    meal_tags = (meal.get("strTags") or "").lower().split(",")
    for tag in meal_tags:
        tag = tag.strip()
        if tag and tag not in tags:
            tags.append(tag)

    return {
        "name": meal["strMeal"],
        "description": f"{area} recipe sourced from TheMealDB.",
        "ingredients": ingredients,
        "instructions": instructions,
        "prep_time_minutes": 15,  # default, will be enriched
        "cook_time_minutes": 30,  # default, will be enriched
        "difficulty": difficulty,
        "servings": 4,
        "tags": tags,
        "autoimmune_score": 3,  # default, will be enriched
        "nutrition": {"calories": 0, "protein": 0, "sodium": 0, "potassium": 0, "phosphorus": 0},
        "source": "seeded",
        "_source_id": meal.get("idMeal"),
        "_source_area": area,
        "_source_category": meal.get("strCategory", ""),
    }


def main():
    output_dir = os.path.join(os.path.dirname(__file__), "..", "app", "data", "raw_recipes")
    os.makedirs(output_dir, exist_ok=True)

    all_recipes = []
    seen_ids = set()

    for area in AREAS:
        print(f"Fetching {area}...")
        meals = fetch_meals_by_area(area)
        print(f"  Found {len(meals)} meals")

        for meal_summary in meals:
            meal_id = meal_summary["idMeal"]
            if meal_id in seen_ids:
                continue
            seen_ids.add(meal_id)

            detail = fetch_meal_detail(meal_id)
            if not detail:
                continue

            recipe = transform_meal(detail, area)
            if recipe:
                all_recipes.append(recipe)

            # Rate limit: be polite to the free API
            time.sleep(0.3)

        print(f"  Total so far: {len(all_recipes)}")

    # Write raw fetched recipes
    output_path = os.path.join(output_dir, "themealdb_raw.json")
    with open(output_path, "w") as f:
        json.dump(all_recipes, f, indent=2)

    print(f"\nDone! Fetched {len(all_recipes)} recipes to {output_path}")


if __name__ == "__main__":
    main()
