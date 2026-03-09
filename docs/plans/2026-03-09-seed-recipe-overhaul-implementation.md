# Seed Recipe Overhaul Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the 25-recipe seed database with 200+ research-backed recipes sourced from TheMealDB API and other external sources, enriched with nutrition data and AIP-based autoimmune scores, validated by a Claude Code skill.

**Architecture:** A Python fetch script pulls recipes from TheMealDB API, transforms them to our schema, and writes batches to JSON. A separate enrichment pass adds nutrition estimates, autoimmune scores, and tags. A validation skill checks data quality. The final output replaces `seed_recipes.json`.

**Tech Stack:** Python (requests, json), TheMealDB API, Claude Code skills

---

### Task 1: TheMealDB Fetch Script

**Files:**
- Create: `backend/scripts/fetch_recipes.py`
- Create: `backend/scripts/requirements-scripts.txt`

This script fetches recipes from TheMealDB, transforms them to our schema, and writes raw JSON batches.

**Step 1: Create the fetch script**

```python
"""Fetch recipes from TheMealDB API and transform to our schema."""
import json
import os
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

    # Try to extract number and unit
    import re
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
    import re
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
```

**Step 2: Run the fetch script**

```bash
cd backend && source venv/bin/activate && python scripts/fetch_recipes.py
```

Expected: Fetches ~250-300 recipes from TheMealDB, writes to `backend/app/data/raw_recipes/themealdb_raw.json`.

**Step 3: Commit**

```bash
git add backend/scripts/fetch_recipes.py backend/app/data/raw_recipes/
git commit -m "feat: add TheMealDB fetch script and raw recipe data"
```

---

### Task 2: Recipe Enrichment Script

**Files:**
- Create: `backend/scripts/enrich_recipes.py`

This script reads raw fetched recipes, adds nutrition estimates, autoimmune scores, tags, and cooking times.

**Step 1: Create the enrichment script**

```python
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

    # If few matches, add baseline (unmapped ingredients contribute ~50cal each)
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
```

**Step 2: Run enrichment**

```bash
cd backend && source venv/bin/activate && python scripts/enrich_recipes.py
```

**Step 3: Commit**

```bash
git add backend/scripts/enrich_recipes.py backend/app/data/raw_recipes/enriched_recipes.json
git commit -m "feat: add recipe enrichment script with nutrition and autoimmune scoring"
```

---

### Task 3: Recipe Curation Script

**Files:**
- Create: `backend/scripts/curate_recipes.py`

This script filters enriched recipes, removes duplicates, ensures cuisine balance, and produces the final seed file. It also merges in the existing 25 seed recipes.

**Step 1: Create the curation script**

```python
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

    # Filter out desserts and duplicates
    seen_names = {r["name"].lower() for r in existing}
    filtered = []
    for r in enriched:
        name_lower = r["name"].lower()
        if name_lower in seen_names:
            continue
        if has_skip_word(r["name"]):
            continue
        if len(r.get("ingredients", [])) < 2:
            continue
        if len(r.get("instructions", [])) < 1:
            continue
        seen_names.add(name_lower)
        filtered.append(r)

    print(f"After filtering: {len(filtered)}")

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
```

**Step 2: Run curation**

```bash
cd backend && source venv/bin/activate && python scripts/curate_recipes.py
```

**Step 3: Review the output**

Check `backend/app/data/seed_recipes.json` has 200+ recipes with good distribution.

**Step 4: Commit**

```bash
git add backend/scripts/curate_recipes.py backend/app/data/seed_recipes.json
git commit -m "feat: curate 200+ seed recipes from TheMealDB with enrichment"
```

---

### Task 4: Manual Mexican & Mediterranean Recipes

**Files:**
- Create: `backend/scripts/add_manual_recipes.py`

TheMealDB may not have enough Mexican recipes or Mediterranean variety. This script adds manually curated recipes to fill gaps.

**Step 1: Create a script that adds targeted recipes**

The script should:
1. Read the current `seed_recipes.json`
2. Count how many Mexican and Mediterranean recipes exist
3. Add manually defined recipes to reach the 30% targets
4. Include autoimmune-friendly Mexican staples: fish tacos, chicken tortilla soup, black bean bowls, carne asada salad, shrimp ceviche, enchiladas verdes (adapted), pozole verde, etc.
5. Include Mediterranean staples: shakshuka (adapted - no nightshades version too), falafel bowls, Greek lemon chicken, grilled fish with herbs, hummus bowls, lamb kofta, etc.
6. Each with full nutrition estimates, autoimmune scores, proper tags

**Step 2: Run it**

```bash
cd backend && source venv/bin/activate && python scripts/add_manual_recipes.py
```

**Step 3: Commit**

```bash
git add backend/scripts/add_manual_recipes.py backend/app/data/seed_recipes.json
git commit -m "feat: add manual Mexican and Mediterranean recipes to reach targets"
```

---

### Task 5: Recipe Validation Skill

**Files:**
- Create: `.claude/skills/recipe-validator.md`

**Step 1: Create the validation skill**

```markdown
# Recipe Validator Skill

Validate seed recipes for data quality, nutrition accuracy, and autoimmune score consistency.

## When to Use

Run after generating or modifying seed_recipes.json to catch data quality issues.

## Instructions

1. **Load the seed recipes** from `backend/app/data/seed_recipes.json`.

2. **Validate each recipe** against these rules:

   **Required fields:** name, description, ingredients (non-empty list), instructions (non-empty list), prep_time_minutes (>0), cook_time_minutes (>=0), difficulty (beginner|intermediate|advanced), servings (>0), tags (non-empty list), autoimmune_score (1-5), nutrition (all 5 fields present), source.

   **Ingredient format:** Each must have name (non-empty string), quantity (number > 0), unit (non-empty string).

   **Nutrition ranges:**
   - calories: 50-1200 per serving
   - protein: 0-80g
   - sodium: 0-1500mg
   - potassium: 0-2000mg
   - phosphorus: 0-800mg

   **Autoimmune score consistency:**
   - Score 5: Should NOT contain nightshades (tomato, pepper, potato, eggplant), dairy, or gluten
   - Score 4: At most 1 borderline ingredient
   - Score 1-2: Should contain multiple inflammatory ingredients

   **Tag consistency:**
   - "kidney-friendly" recipes should have potassium < 600mg and phosphorus < 300mg
   - "low-sodium" recipes should have sodium < 300mg
   - "gluten-free" should not contain flour, bread, pasta, wheat
   - "dairy-free" should not contain milk, cream, cheese, butter, yogurt

   **No duplicates:** No two recipes should have the same name (case-insensitive).

3. **Print results** grouped by severity:
   - ERRORS: Must fix (missing fields, out-of-range values)
   - WARNINGS: Should review (score inconsistencies, tag mismatches)
   - INFO: Statistics (total count, distribution by cuisine/meal type/score)

4. **Fix any errors** found by updating the recipe data directly.
```

**Step 2: Commit**

```bash
git add .claude/skills/recipe-validator.md
git commit -m "feat: add recipe validator skill for data quality checks"
```

---

### Task 6: Run Validation & Fix Issues

**Step 1: Run the recipe-validator skill**

Invoke `/recipe-validator` from Claude Code CLI.

**Step 2: Fix any errors or warnings**

Directly edit `backend/app/data/seed_recipes.json` to fix:
- Missing or invalid fields
- Nutrition values out of range
- Autoimmune score inconsistencies
- Tag mismatches

**Step 3: Re-run validation to confirm clean**

**Step 4: Commit**

```bash
git add backend/app/data/seed_recipes.json
git commit -m "fix: resolve recipe validation errors and inconsistencies"
```

---

### Task 7: Update Seed Service & Tests

**Files:**
- Modify: `backend/app/services/seed.py`
- Modify: `backend/tests/test_seed.py`

The seed service loads `seed_recipes.json` on startup. With 200+ recipes, ensure it still works and the tests reflect the new count.

**Step 1: Update test expectations**

In `backend/tests/test_seed.py`, update the test that checks recipe count. The exact number depends on final curation, but change from checking for 25 to checking for >= 200.

```python
def test_seed_file_has_recipes():
    recipes = load_seed_recipes()
    assert len(recipes) >= 200
```

**Step 2: Run tests**

```bash
cd backend && source venv/bin/activate && python -m pytest tests/test_seed.py -v
```

**Step 3: Run full test suite**

```bash
cd backend && source venv/bin/activate && python -m pytest tests/ -v
```

**Step 4: Commit**

```bash
git add backend/tests/test_seed.py
git commit -m "test: update seed tests for 200+ recipe database"
```

---

### Task 8: Clean Up Raw Data & Final Verification

**Step 1: Remove raw intermediate files**

The `raw_recipes/` directory was for intermediate processing. Add it to `.gitignore` or delete it.

```bash
echo "raw_recipes/" >> backend/app/data/.gitignore
```

**Step 2: Run full test suite one more time**

```bash
cd backend && source venv/bin/activate && python -m pytest tests/ -v
```

**Step 3: Verify frontend build**

```bash
cd frontend && npm run build
```

**Step 4: Final commit**

```bash
git add backend/app/data/.gitignore
git commit -m "chore: add .gitignore for raw recipe data"
```
