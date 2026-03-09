"""Enrich raw recipes with nutrition, autoimmune scores, and tags."""
import json
import os
import re

# AIP inflammatory ingredients (penalize autoimmune score)
INFLAMMATORY = {
    # Nightshades
    "tomato", "tomatoes", "pepper", "peppers", "bell pepper", "chili",
    "jalapeno", "paprika", "cayenne", "potato", "potatoes", "eggplant",
    # Gluten grains
    "flour", "bread", "pasta", "wheat", "breadcrumbs", "noodles",
    # Dairy
    "milk", "cream", "cheese", "butter", "yogurt", "sour cream",
    # Refined sugar
    "sugar", "brown sugar", "powdered sugar",
    # Seed oils
    "vegetable oil", "canola oil", "sunflower oil", "corn oil",
    # Other
    "soy sauce", "soy", "corn", "cornstarch",
}

# Anti-inflammatory ingredients (boost autoimmune score)
ANTI_INFLAMMATORY = {
    "turmeric", "ginger", "garlic", "olive oil", "salmon", "sardines",
    "mackerel", "spinach", "kale", "broccoli", "cauliflower", "blueberries",
    "strawberries", "sweet potato", "avocado", "coconut oil", "bone broth",
    "lemon", "lime", "apple cider vinegar", "cinnamon", "oregano",
    "rosemary", "thyme", "basil", "cilantro", "parsley", "green tea",
    "chia seeds", "flaxseed", "walnuts", "almonds",
}

# High potassium ingredients (flag for kidney-conscious)
HIGH_POTASSIUM = {
    "banana", "potato", "potatoes", "sweet potato", "tomato", "tomatoes",
    "spinach", "avocado", "beans", "lentils", "orange", "dried fruit",
}

# High sodium ingredients
HIGH_SODIUM = {
    "soy sauce", "salt", "fish sauce", "oyster sauce", "miso",
    "anchovy", "anchovies", "bacon", "ham", "salami", "pickles",
    "capers", "olives", "parmesan",
}

# Average nutrition per ingredient category (rough USDA-based estimates per serving)
NUTRITION_ESTIMATES = {
    # Proteins (per ~4oz serving)
    "chicken": {"calories": 165, "protein": 31, "sodium": 74, "potassium": 256, "phosphorus": 196},
    "beef": {"calories": 250, "protein": 26, "sodium": 66, "potassium": 318, "phosphorus": 175},
    "salmon": {"calories": 208, "protein": 20, "sodium": 59, "potassium": 363, "phosphorus": 252},
    "shrimp": {"calories": 85, "protein": 20, "sodium": 292, "potassium": 182, "phosphorus": 201},
    "tuna": {"calories": 130, "protein": 29, "sodium": 40, "potassium": 237, "phosphorus": 254},
    "cod": {"calories": 82, "protein": 18, "sodium": 54, "potassium": 413, "phosphorus": 203},
    "pork": {"calories": 242, "protein": 27, "sodium": 62, "potassium": 362, "phosphorus": 220},
    "lamb": {"calories": 258, "protein": 25, "sodium": 72, "potassium": 310, "phosphorus": 188},
    "turkey": {"calories": 135, "protein": 30, "sodium": 60, "potassium": 249, "phosphorus": 196},
    "egg": {"calories": 78, "protein": 6, "sodium": 62, "potassium": 63, "phosphorus": 86},
    "tofu": {"calories": 80, "protein": 9, "sodium": 8, "potassium": 150, "phosphorus": 120},
    # Grains (per ~1 cup cooked)
    "rice": {"calories": 206, "protein": 4, "sodium": 1, "potassium": 55, "phosphorus": 68},
    "pasta": {"calories": 220, "protein": 8, "sodium": 1, "potassium": 44, "phosphorus": 58},
    "oats": {"calories": 150, "protein": 5, "sodium": 2, "potassium": 164, "phosphorus": 180},
    "quinoa": {"calories": 222, "protein": 8, "sodium": 13, "potassium": 318, "phosphorus": 281},
    "bread": {"calories": 75, "protein": 3, "sodium": 132, "potassium": 37, "phosphorus": 33},
    "tortilla": {"calories": 120, "protein": 3, "sodium": 200, "potassium": 50, "phosphorus": 60},
    # Vegetables (per ~1 cup)
    "broccoli": {"calories": 55, "protein": 4, "sodium": 64, "potassium": 457, "phosphorus": 105},
    "spinach": {"calories": 41, "protein": 5, "sodium": 126, "potassium": 839, "phosphorus": 100},
    "carrot": {"calories": 52, "protein": 1, "sodium": 88, "potassium": 410, "phosphorus": 45},
    "onion": {"calories": 46, "protein": 1, "sodium": 5, "potassium": 190, "phosphorus": 36},
    "garlic": {"calories": 5, "protein": 0, "sodium": 1, "potassium": 12, "phosphorus": 5},
    "tomato": {"calories": 32, "protein": 2, "sodium": 9, "potassium": 427, "phosphorus": 43},
    "pepper": {"calories": 30, "protein": 1, "sodium": 4, "potassium": 210, "phosphorus": 26},
    "potato": {"calories": 163, "protein": 4, "sodium": 13, "potassium": 897, "phosphorus": 121},
    "sweet potato": {"calories": 114, "protein": 2, "sodium": 73, "potassium": 448, "phosphorus": 63},
    "zucchini": {"calories": 20, "protein": 2, "sodium": 12, "potassium": 324, "phosphorus": 48},
    "avocado": {"calories": 160, "protein": 2, "sodium": 7, "potassium": 485, "phosphorus": 52},
    "cucumber": {"calories": 16, "protein": 1, "sodium": 2, "potassium": 152, "phosphorus": 24},
    "lettuce": {"calories": 10, "protein": 1, "sodium": 10, "potassium": 141, "phosphorus": 20},
    # Legumes (per ~1 cup cooked)
    "beans": {"calories": 225, "protein": 15, "sodium": 2, "potassium": 655, "phosphorus": 251},
    "lentils": {"calories": 230, "protein": 18, "sodium": 4, "potassium": 731, "phosphorus": 356},
    "chickpeas": {"calories": 269, "protein": 15, "sodium": 11, "potassium": 474, "phosphorus": 276},
    # Fats (per tbsp)
    "olive oil": {"calories": 119, "protein": 0, "sodium": 0, "potassium": 0, "phosphorus": 0},
    "butter": {"calories": 102, "protein": 0, "sodium": 91, "potassium": 3, "phosphorus": 3},
    "coconut oil": {"calories": 121, "protein": 0, "sodium": 0, "potassium": 0, "phosphorus": 0},
}


def get_ingredient_names(recipe: dict) -> list[str]:
    """Extract lowercase ingredient names."""
    return [ing["name"].lower().strip() for ing in recipe.get("ingredients", [])]


def score_autoimmune(ingredient_names: list[str]) -> int:
    """Score 1-5 based on AIP criteria."""
    inflammatory_count = sum(1 for name in ingredient_names
                             for trigger in INFLAMMATORY if trigger in name)
    anti_count = sum(1 for name in ingredient_names
                     for boost in ANTI_INFLAMMATORY if boost in name)

    # Start at 3, adjust
    score = 3.0
    score -= inflammatory_count * 0.4
    score += anti_count * 0.3

    return max(1, min(5, round(score)))


def estimate_nutrition(ingredient_names: list[str]) -> dict:
    """Estimate per-serving nutrition from ingredient composition."""
    total = {"calories": 0, "protein": 0, "sodium": 0, "potassium": 0, "phosphorus": 0}
    matched = 0

    for name in ingredient_names:
        for key, values in NUTRITION_ESTIMATES.items():
            if key in name:
                for nutrient in total:
                    total[nutrient] += values[nutrient]
                matched += 1
                break

    # If few matches, add baseline (unmapped ingredients contribute ~30cal each)
    unmatched = len(ingredient_names) - matched
    total["calories"] += unmatched * 30
    total["sodium"] += unmatched * 20

    # Divide by ~4 servings to get per-serving
    servings = 4
    return {k: round(v / servings) for k, v in total.items()}


def assign_tags(recipe: dict, ingredient_names: list[str]) -> list[str]:
    """Assign tags based on ingredients and properties."""
    tags = list(recipe.get("tags", []))

    # Meal type from category or name
    name_lower = recipe["name"].lower()
    category = recipe.get("_source_category", "").lower()

    if any(word in name_lower for word in ["breakfast", "oat", "pancake", "egg", "smoothie"]):
        if "breakfast" not in tags:
            tags.append("breakfast")
    elif any(word in name_lower for word in ["salad", "sandwich", "wrap", "soup"]):
        if "lunch" not in tags:
            tags.append("lunch")
    else:
        if "dinner" not in tags:
            tags.append("dinner")

    # Dietary tags
    has_gluten = any(g in name for name in ingredient_names for g in ["flour", "bread", "pasta", "wheat", "noodle"])
    has_dairy = any(d in name for name in ingredient_names for d in ["milk", "cream", "cheese", "butter", "yogurt"])
    has_meat = any(m in name for name in ingredient_names for m in ["chicken", "beef", "pork", "lamb", "turkey", "bacon", "ham"])

    if not has_gluten:
        tags.append("gluten-free")
    if not has_dairy:
        tags.append("dairy-free")
    if not has_meat:
        tags.append("vegetarian")

    # Health tags
    inflammatory_count = sum(1 for name in ingredient_names for t in INFLAMMATORY if t in name)
    if inflammatory_count == 0:
        tags.append("anti-inflammatory")

    high_k = sum(1 for name in ingredient_names for k in HIGH_POTASSIUM if k in name)
    if high_k <= 1:
        tags.append("kidney-friendly")

    high_na = sum(1 for name in ingredient_names for s in HIGH_SODIUM if s in name)
    if high_na == 0:
        tags.append("low-sodium")

    return list(set(tags))


def estimate_cook_times(recipe: dict, ingredient_names: list[str]) -> tuple[int, int]:
    """Estimate prep and cook times based on complexity."""
    n_ingredients = len(ingredient_names)
    n_steps = len(recipe.get("instructions", []))

    # Proteins that need significant cooking
    slow_cook = any(s in " ".join(ingredient_names) for s in ["lamb", "pork", "beef", "stew"])

    if slow_cook:
        prep, cook = 20, 60
    elif n_ingredients > 10:
        prep, cook = 20, 40
    elif n_ingredients > 6:
        prep, cook = 15, 25
    else:
        prep, cook = 10, 15

    # More steps = more time
    if n_steps > 8:
        cook += 15
    elif n_steps > 5:
        cook += 5

    return prep, cook


def enrich_recipe(recipe: dict) -> dict:
    """Enrich a single recipe with nutrition, scores, tags, times."""
    names = get_ingredient_names(recipe)

    recipe["autoimmune_score"] = score_autoimmune(names)
    recipe["nutrition"] = estimate_nutrition(names)
    recipe["tags"] = assign_tags(recipe, names)

    prep, cook = estimate_cook_times(recipe, names)
    recipe["prep_time_minutes"] = prep
    recipe["cook_time_minutes"] = cook

    # Clean up internal fields
    recipe.pop("_source_id", None)
    recipe.pop("_source_area", None)
    recipe.pop("_source_category", None)

    return recipe


def main():
    raw_path = os.path.join(os.path.dirname(__file__), "..", "app", "data", "raw_recipes", "themealdb_raw.json")

    if not os.path.exists(raw_path):
        print(f"Raw recipes not found at {raw_path}. Run fetch_recipes.py first.")
        return

    with open(raw_path) as f:
        recipes = json.load(f)

    print(f"Enriching {len(recipes)} recipes...")

    enriched = []
    for recipe in recipes:
        enriched.append(enrich_recipe(recipe))

    # Write enriched recipes
    output_path = os.path.join(os.path.dirname(__file__), "..", "app", "data", "raw_recipes", "enriched_recipes.json")
    with open(output_path, "w") as f:
        json.dump(enriched, f, indent=2)

    # Print summary
    scores = [r["autoimmune_score"] for r in enriched]
    avg_score = sum(scores) / len(scores) if scores else 0
    tags_all = [t for r in enriched for t in r["tags"]]
    print(f"\nEnriched {len(enriched)} recipes")
    print(f"Average autoimmune score: {avg_score:.1f}")
    print(f"Score distribution: {', '.join(f'{s}:{scores.count(s)}' for s in range(1, 6))}")
    print(f"Anti-inflammatory: {sum(1 for r in enriched if 'anti-inflammatory' in r['tags'])}")
    print(f"Kidney-friendly: {sum(1 for r in enriched if 'kidney-friendly' in r['tags'])}")

    print(f"\nOutput: {output_path}")


if __name__ == "__main__":
    main()
