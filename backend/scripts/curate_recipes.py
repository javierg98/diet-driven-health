"""Curate enriched TheMealDB recipes into seed_recipes.json using quota-based selection.

Reads enriched_recipes.json (TheMealDB) and the raw data for area mapping,
then selects a balanced set based on cuisine and meal type quotas.

Output: ONLY curated TheMealDB recipes (manual recipes added by other scripts).
"""
import json
import os
from collections import defaultdict

# Total TheMealDB recipes to select (manual scripts add ~97 more)
TARGET_TOTAL = 170

# Cuisine quotas (fraction of TARGET_TOTAL)
CUISINE_QUOTAS = {
    "mexican": 0.15,       # ~25 (manual scripts add ~55 more Mexican)
    "mediterranean": 0.30, # ~51 (manual scripts add ~12 more Med)
    "american": 0.20,      # ~34
    "asian": 0.20,         # ~34
    "other": 0.15,         # ~26
}

# Meal type quotas (fraction of TARGET_TOTAL)
MEAL_QUOTAS = {
    "breakfast": 0.12,  # ~20 (breakfast/snack script adds ~15 more)
    "lunch": 0.28,      # ~48
    "dinner": 0.50,     # ~85
    "snack": 0.10,      # ~17 (breakfast/snack script adds ~15 more)
}

# Map TheMealDB areas to our cuisine categories
AREA_TO_CUISINE = {
    # Direct matches
    "Mexican": "mexican",
    "American": "american",
    "Chinese": "asian",
    "Japanese": "asian",
    "Thai": "asian",
    "Vietnamese": "asian",
    "Filipino": "asian",
    "Malaysian": "asian",
    "Indian": "asian",
    # Mediterranean basin
    "Italian": "mediterranean",
    "Greek": "mediterranean",
    "Spanish": "mediterranean",
    "Turkish": "mediterranean",
    "French": "mediterranean",
    "Moroccan": "mediterranean",
    "Egyptian": "mediterranean",
    "Tunisian": "mediterranean",
    "Portuguese": "mediterranean",
    # Anglo → american
    "British": "american",
    "Canadian": "american",
    "Irish": "american",
    # European other
    "Croatian": "other",
    "Dutch": "other",
    "Polish": "other",
    "Russian": "other",
    # Caribbean/African → other
    "Jamaican": "other",
    "Kenyan": "other",
}

# Categories/names to skip (desserts, pastries, unhealthy)
SKIP_WORDS = {
    "dessert", "cake", "pie", "pudding", "cookie", "cookies",
    "pastry", "ice cream", "tart", "brownie", "candy", "fudge",
    "nanaimo", "beavertails", "timbits", "sugar pie", "butter tarts",
    "jam jam", "figgy duff", "date squares", "flapper pie",
}

# Tags that indicate a dessert/treat
SKIP_TAGS = {"desert", "treat", "cake", "baking", "chocolate", "caramel", "sweet"}


def should_skip(recipe: dict) -> str | None:
    """Return skip reason or None if recipe should be kept."""
    name_lower = recipe["name"].lower()

    # Skip desserts by name
    for word in SKIP_WORDS:
        if word in name_lower:
            return f"dessert/pastry ({word})"

    # Skip if tagged as dessert/treat
    tags = set(t.lower() for t in recipe.get("tags", []))
    skip_matches = tags & SKIP_TAGS
    if skip_matches:
        return f"dessert tag ({', '.join(skip_matches)})"

    # Skip low-quality recipes (too few ingredients or instructions)
    if len(recipe.get("ingredients", [])) < 3:
        return "too few ingredients"
    if len(recipe.get("instructions", [])) < 2:
        return "too few instructions"

    # Skip alcoholic recipes
    if "alcoholic" in tags:
        return "alcoholic"

    return None


def get_cuisine_from_area(recipe_name: str, area_map: dict, tag_cuisine: str) -> str:
    """Determine cuisine using area mapping, falling back to tag-based."""
    # If enrichment already tagged a cuisine, trust it
    if tag_cuisine != "other":
        return tag_cuisine

    # Look up area from raw data
    area = area_map.get(recipe_name)
    if area and area in AREA_TO_CUISINE:
        return AREA_TO_CUISINE[area]

    return "other"


def get_cuisine_from_tags(recipe: dict) -> str:
    """Get cuisine from tags (enrichment-assigned)."""
    tags = set(t.lower() for t in recipe.get("tags", []))
    for cuisine in ["mexican", "mediterranean", "asian", "american", "indian"]:
        if cuisine in tags:
            if cuisine == "indian":
                return "asian"
            return cuisine
    return "other"


def get_meal_type(recipe: dict) -> str:
    """Get meal type from tags."""
    tags = set(t.lower() for t in recipe.get("tags", []))
    for meal in ["breakfast", "lunch", "snack", "dinner"]:
        if meal in tags:
            return meal
    # Check name-based hints
    name_lower = recipe["name"].lower()
    if any(w in name_lower for w in ["breakfast", "oat", "pancake", "smoothie", "porridge"]):
        return "breakfast"
    if any(w in name_lower for w in ["salad", "sandwich", "wrap", "soup"]):
        return "lunch"
    return "dinner"


def print_distribution(recipes: list, label: str = ""):
    """Print cuisine and meal type distribution."""
    total = len(recipes)
    if label:
        print(f"\n{'='*60}")
        print(f"  {label}: {total} recipes")
        print(f"{'='*60}")
    else:
        print(f"\nTotal: {total} recipes")

    cuisines = defaultdict(int)
    meals = defaultdict(int)
    for r in recipes:
        cuisines[r["_cuisine"]] += 1
        meals[r["_meal_type"]] += 1

    print("  Cuisine distribution:")
    for c in sorted(cuisines, key=lambda x: -cuisines[x]):
        pct = cuisines[c] / total * 100 if total else 0
        print(f"    {c:20s}: {cuisines[c]:3d} ({pct:5.1f}%)")

    print("  Meal type distribution:")
    for m in sorted(meals, key=lambda x: -meals[x]):
        pct = meals[m] / total * 100 if total else 0
        print(f"    {m:20s}: {meals[m]:3d} ({pct:5.1f}%)")

    scores = [r.get("autoimmune_score", 0) for r in recipes]
    if scores:
        print(f"  Avg autoimmune score: {sum(scores)/len(scores):.1f}")


def select_with_quotas(
    candidates: list,
    cuisine_slots: dict,
    meal_slots: dict,
    target: int,
) -> list:
    """Select recipes to fill cuisine and meal type quotas.

    Strategy:
    1. Group candidates by (cuisine, meal_type)
    2. For each combination, sort by autoimmune_score descending
    3. Fill slots greedily, preferring under-represented categories
    """
    # Group by (cuisine, meal_type)
    buckets = defaultdict(list)
    for r in candidates:
        key = (r["_cuisine"], r["_meal_type"])
        buckets[key].append(r)

    # Sort each bucket by score descending
    for key in buckets:
        buckets[key].sort(key=lambda r: r.get("autoimmune_score", 0), reverse=True)

    selected = []
    cuisine_count = defaultdict(int)
    meal_count = defaultdict(int)
    selected_names = set()

    # Pass 1: Fill each (cuisine, meal_type) combo proportionally
    for (cuisine, meal_type), recipes in sorted(buckets.items()):
        cuisine_target = cuisine_slots.get(cuisine, 0)
        meal_target = meal_slots.get(meal_type, 0)

        # How many from this combo? Proportional share
        combo_target = min(cuisine_target, meal_target) // max(1, len(
            [k for k in buckets if k[0] == cuisine or k[1] == meal_type]
        ) // 2)
        combo_target = max(1, min(combo_target, len(recipes)))

        for r in recipes[:combo_target]:
            name = r["name"].lower()
            if name in selected_names:
                continue
            selected.append(r)
            selected_names.add(name)
            cuisine_count[cuisine] += 1
            meal_count[meal_type] += 1

    # Pass 2: Fill remaining cuisine slots (prefer under-filled cuisines)
    for cuisine, target_count in sorted(cuisine_slots.items(), key=lambda x: -x[1]):
        needed = target_count - cuisine_count[cuisine]
        if needed <= 0:
            continue

        # Get all unused candidates for this cuisine, prefer under-filled meal types
        avail = [r for r in candidates
                 if r["_cuisine"] == cuisine and r["name"].lower() not in selected_names]
        # Sort: prefer meal types that are under-filled, then by score
        avail.sort(key=lambda r: (
            meal_count[r["_meal_type"]] >= meal_slots.get(r["_meal_type"], 0),
            -r.get("autoimmune_score", 0)
        ))

        for r in avail[:needed]:
            selected.append(r)
            selected_names.add(r["name"].lower())
            cuisine_count[r["_cuisine"]] += 1
            meal_count[r["_meal_type"]] += 1

    # Pass 3: Fill remaining meal type slots from any cuisine
    for meal_type, target_count in sorted(meal_slots.items(), key=lambda x: -x[1]):
        needed = target_count - meal_count[meal_type]
        if needed <= 0:
            continue

        avail = [r for r in candidates
                 if r["_meal_type"] == meal_type and r["name"].lower() not in selected_names]
        # Prefer under-filled cuisines
        avail.sort(key=lambda r: (
            cuisine_count[r["_cuisine"]] >= cuisine_slots.get(r["_cuisine"], 0),
            -r.get("autoimmune_score", 0)
        ))

        for r in avail[:needed]:
            selected.append(r)
            selected_names.add(r["name"].lower())
            cuisine_count[r["_cuisine"]] += 1
            meal_count[r["_meal_type"]] += 1

    # Pass 4: Fill remaining to reach target with highest-scored unused recipes
    if len(selected) < target:
        remaining = [r for r in candidates if r["name"].lower() not in selected_names]
        remaining.sort(key=lambda r: -r.get("autoimmune_score", 0))
        for r in remaining[:target - len(selected)]:
            selected.append(r)
            selected_names.add(r["name"].lower())

    return selected[:target]


def main():
    script_dir = os.path.dirname(__file__)
    enriched_path = os.path.join(script_dir, "..", "app", "data", "raw_recipes", "enriched_recipes.json")
    raw_path = os.path.join(script_dir, "..", "app", "data", "raw_recipes", "themealdb_raw.json")
    output_path = os.path.join(script_dir, "..", "app", "data", "seed_recipes.json")

    # Load enriched recipes
    with open(enriched_path) as f:
        enriched = json.load(f)
    print(f"Loaded {len(enriched)} enriched recipes")

    # Load raw for area mapping
    area_map = {}
    if os.path.exists(raw_path):
        with open(raw_path) as f:
            raw = json.load(f)
        for r in raw:
            area_map[r["name"]] = r.get("_source_area", "unknown")
        print(f"Loaded area mapping for {len(area_map)} recipes")

    # Filter and annotate
    candidates = []
    skip_reasons = defaultdict(int)

    for r in enriched:
        reason = should_skip(r)
        if reason:
            skip_reasons[reason] += 1
            continue

        tag_cuisine = get_cuisine_from_tags(r)
        r["_cuisine"] = get_cuisine_from_area(r["name"], area_map, tag_cuisine)
        r["_meal_type"] = get_meal_type(r)
        candidates.append(r)

    print(f"\nAfter filtering: {len(candidates)} candidates")
    print(f"Skipped {sum(skip_reasons.values())} recipes:")
    for reason, count in sorted(skip_reasons.items(), key=lambda x: -x[1]):
        print(f"  {reason}: {count}")

    # Show candidate distribution
    print_distribution(candidates, "Available candidates")

    # Calculate absolute quotas
    cuisine_slots = {c: round(TARGET_TOTAL * pct) for c, pct in CUISINE_QUOTAS.items()}
    meal_slots = {m: round(TARGET_TOTAL * pct) for m, pct in MEAL_QUOTAS.items()}

    print(f"\nTarget cuisine slots: {dict(cuisine_slots)}")
    print(f"Target meal slots: {dict(meal_slots)}")

    # Select with quotas
    selected = select_with_quotas(candidates, cuisine_slots, meal_slots, TARGET_TOTAL)

    # Remove internal fields before writing
    for r in selected:
        r.pop("_cuisine", None)
        r.pop("_meal_type", None)

    # Write output (ONLY TheMealDB curated recipes)
    with open(output_path, "w") as f:
        json.dump(selected, f, indent=2)
        f.write("\n")

    # Re-annotate for distribution printing
    for r in selected:
        tag_cuisine = get_cuisine_from_tags(r)
        r["_cuisine"] = get_cuisine_from_area(r["name"], area_map, tag_cuisine)
        r["_meal_type"] = get_meal_type(r)

    print_distribution(selected, "SELECTED (written to seed_recipes.json)")

    # Clean up internal fields again
    for r in selected:
        r.pop("_cuisine", None)
        r.pop("_meal_type", None)


if __name__ == "__main__":
    main()
