"""Curate enriched recipes into final seed_recipes.json."""
import json
import os

TARGET_TOTAL = 200
CUISINE_TARGETS = {
    "mexican": 0.30,
    "mediterranean": 0.30,
    "american": 0.15,
    "asian": 0.15,
}
MEAL_TARGETS = {
    "breakfast": 0.20,
    "lunch": 0.30,
    "dinner": 0.40,
    "snack": 0.10,
}

# Categories to skip (desserts, pastries)
SKIP_CATEGORIES = {"dessert", "cake", "pie", "pudding", "cookie", "pastry", "ice cream"}


def has_skip_word(name: str) -> bool:
    lower = name.lower()
    return any(word in lower for word in SKIP_CATEGORIES)


def get_cuisine(recipe: dict) -> str:
    tags = recipe.get("tags", [])
    for cuisine in ["mexican", "mediterranean", "asian", "american", "indian"]:
        if cuisine in tags:
            return cuisine
    return "other"


def get_meal_type(recipe: dict) -> str:
    tags = recipe.get("tags", [])
    for meal in ["breakfast", "lunch", "dinner", "snack"]:
        if meal in tags:
            return meal
    return "dinner"


def main():
    enriched_path = os.path.join(os.path.dirname(__file__), "..", "app", "data", "raw_recipes", "enriched_recipes.json")
    existing_path = os.path.join(os.path.dirname(__file__), "..", "app", "data", "seed_recipes.json")

    with open(enriched_path) as f:
        enriched = json.load(f)

    with open(existing_path) as f:
        existing = json.load(f)

    print(f"Enriched: {len(enriched)}, Existing: {len(existing)}")

    # Filter out desserts, duplicates, and low-quality recipes
    seen_names = {r["name"].lower() for r in existing}
    filtered = []
    skipped_dessert = 0
    skipped_duplicate = 0
    skipped_quality = 0

    for r in enriched:
        name_lower = r["name"].lower()
        if name_lower in seen_names:
            skipped_duplicate += 1
            continue
        if has_skip_word(r["name"]):
            skipped_dessert += 1
            continue
        if len(r.get("ingredients", [])) < 2:
            skipped_quality += 1
            continue
        if len(r.get("instructions", [])) < 1:
            skipped_quality += 1
            continue
        seen_names.add(name_lower)
        filtered.append(r)

    print(f"After filtering: {len(filtered)}")
    print(f"  Skipped duplicates: {skipped_duplicate}")
    print(f"  Skipped desserts/pastries: {skipped_dessert}")
    print(f"  Skipped low-quality: {skipped_quality}")

    # Sort by autoimmune score descending (prefer healthier recipes)
    filtered.sort(key=lambda r: r.get("autoimmune_score", 3), reverse=True)

    # Select up to TARGET_TOTAL - len(existing)
    slots = TARGET_TOTAL - len(existing)
    selected = filtered[:slots]

    # Combine
    final = existing + selected

    # Write final seed file
    output_path = os.path.join(os.path.dirname(__file__), "..", "app", "data", "seed_recipes.json")
    with open(output_path, "w") as f:
        json.dump(final, f, indent=2)

    # Summary
    cuisines = {}
    meals = {}
    for r in final:
        c = get_cuisine(r)
        cuisines[c] = cuisines.get(c, 0) + 1
        m = get_meal_type(r)
        meals[m] = meals.get(m, 0) + 1

    print(f"\nFinal: {len(final)} recipes")
    print(f"Cuisines: {json.dumps(cuisines, indent=2)}")
    print(f"Meal types: {json.dumps(meals, indent=2)}")
    scores = [r["autoimmune_score"] for r in final]
    print(f"Avg autoimmune score: {sum(scores)/len(scores):.1f}")


if __name__ == "__main__":
    main()
