#!/usr/bin/env python3
"""Validate seed recipes for data quality, nutrition accuracy, and autoimmune score consistency."""

import json
import sys
from collections import Counter
from pathlib import Path

SEED_FILE = Path(__file__).parent.parent / "app" / "data" / "seed_recipes.json"

VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced"}
NUTRITION_FIELDS = {"calories", "protein", "sodium", "potassium", "phosphorus"}
NUTRITION_RANGES = {
    "calories": (50, 1200),
    "protein": (0, 80),
    "sodium": (0, 1500),
    "potassium": (0, 2000),
    "phosphorus": (0, 800),
}

NIGHTSHADES = ["tomato", "pepper", "potato", "eggplant", "paprika", "cayenne", "jalapeno", "chili"]
DAIRY = ["milk", "cream", "cheese", "butter", "yogurt"]
GLUTEN = ["flour", "bread", "pasta", "wheat"]
INFLAMMATORY = NIGHTSHADES + DAIRY + GLUTEN

# Exclusions: ingredient names that contain trigger substrings but are NOT inflammatory
INFLAMMATORY_EXCLUSIONS = {
    "almond milk", "coconut milk", "oat milk", "soy milk", "rice milk",
    "coconut cream", "coconut yogurt", "coconut butter",
    "butter lettuce", "peanut butter", "almond butter", "cashew butter", "sunflower seed butter",
    "sweet potato", "sweet potatoes",
    "black pepper", "black peppercorn", "white pepper", "cracked pepper",
    "almond flour", "coconut flour", "buckwheat flour", "cassava flour",
    "tapioca flour", "rice flour", "oat flour",
    "dairy-free cheese", "vegan cheese",
    "gluten-free bread", "gluten-free crackers", "gluten-free tortilla",
    "chili-lime seasoning",
}


def is_excluded(ingredient_name: str) -> bool:
    """Check if an ingredient name matches an exclusion pattern."""
    return any(excl in ingredient_name for excl in INFLAMMATORY_EXCLUSIONS)


def ingredient_contains(ingredient_name: str, keywords: list[str]) -> bool:
    name_lower = ingredient_name.lower()
    if is_excluded(name_lower):
        return False
    return any(kw in name_lower for kw in keywords)


def count_inflammatory(ingredients: list[dict]) -> int:
    count = 0
    for ing in ingredients:
        name = ing.get("name", "").lower()
        if is_excluded(name):
            continue
        if any(kw in name for kw in INFLAMMATORY):
            count += 1
    return count


def validate_recipes(recipes: list[dict], auto_fix: bool = False) -> tuple[list, list, dict]:
    errors = []
    warnings = []
    fixed_count = 0
    name_seen = {}

    for i, recipe in enumerate(recipes):
        name = recipe.get("name", f"<unnamed #{i}>")
        prefix = f"Recipe '{name}'"

        # --- Duplicate check ---
        name_lower = name.lower()
        if name_lower in name_seen:
            errors.append(f"{prefix}: duplicate name (first at index {name_seen[name_lower]})")
        else:
            name_seen[name_lower] = i

        # --- Required fields ---
        for field in ["name", "description", "source"]:
            if not recipe.get(field):
                errors.append(f"{prefix}: missing or empty '{field}'")

        # ingredients
        ingredients = recipe.get("ingredients")
        if not ingredients or not isinstance(ingredients, list) or len(ingredients) == 0:
            errors.append(f"{prefix}: missing or empty 'ingredients'")
            ingredients = []

        # instructions
        instructions = recipe.get("instructions")
        if not instructions or not isinstance(instructions, list) or len(instructions) == 0:
            errors.append(f"{prefix}: missing or empty 'instructions'")

        # prep_time_minutes > 0
        prep = recipe.get("prep_time_minutes")
        if prep is None or not isinstance(prep, (int, float)) or prep <= 0:
            errors.append(f"{prefix}: prep_time_minutes must be > 0 (got {prep})")

        # cook_time_minutes >= 0
        cook = recipe.get("cook_time_minutes")
        if cook is None or not isinstance(cook, (int, float)) or cook < 0:
            errors.append(f"{prefix}: cook_time_minutes must be >= 0 (got {cook})")

        # difficulty
        diff = recipe.get("difficulty")
        if diff not in VALID_DIFFICULTIES:
            errors.append(f"{prefix}: invalid difficulty '{diff}' (must be one of {VALID_DIFFICULTIES})")

        # servings > 0
        servings = recipe.get("servings")
        if servings is None or not isinstance(servings, (int, float)) or servings <= 0:
            errors.append(f"{prefix}: servings must be > 0 (got {servings})")

        # tags
        tags = recipe.get("tags")
        if not tags or not isinstance(tags, list) or len(tags) == 0:
            errors.append(f"{prefix}: missing or empty 'tags'")
            tags = []

        # autoimmune_score 1-5
        score = recipe.get("autoimmune_score")
        if score is None or not isinstance(score, (int, float)) or score < 1 or score > 5:
            errors.append(f"{prefix}: autoimmune_score must be 1-5 (got {score})")

        # nutrition
        nutrition = recipe.get("nutrition")
        if not nutrition or not isinstance(nutrition, dict):
            errors.append(f"{prefix}: missing 'nutrition'")
            nutrition = {}
        else:
            missing_fields = NUTRITION_FIELDS - set(nutrition.keys())
            if missing_fields:
                errors.append(f"{prefix}: nutrition missing fields: {missing_fields}")

            for field, (lo, hi) in NUTRITION_RANGES.items():
                val = nutrition.get(field)
                if val is not None:
                    if not isinstance(val, (int, float)):
                        errors.append(f"{prefix}: nutrition.{field} must be a number (got {type(val).__name__})")
                    elif val < lo or val > hi:
                        if auto_fix:
                            old_val = val
                            if val < lo:
                                nutrition[field] = lo
                            else:
                                nutrition[field] = hi
                            fixed_count += 1
                        else:
                            errors.append(f"{prefix}: nutrition.{field}={val} out of range [{lo}-{hi}]")

        # --- Ingredient format ---
        for j, ing in enumerate(ingredients):
            ing_name = ing.get("name")
            if not ing_name or not isinstance(ing_name, str) or ing_name.strip() == "":
                errors.append(f"{prefix}: ingredient[{j}] missing or empty 'name'")
            qty = ing.get("quantity")
            if qty is None or not isinstance(qty, (int, float)) or qty <= 0:
                errors.append(f"{prefix}: ingredient[{j}] ({ing.get('name', '?')}) quantity must be > 0 (got {qty})")
            unit = ing.get("unit")
            if not unit or not isinstance(unit, str) or unit.strip() == "":
                errors.append(f"{prefix}: ingredient[{j}] ({ing.get('name', '?')}) missing or empty 'unit'")

        # --- Autoimmune score consistency ---
        if isinstance(score, (int, float)) and 1 <= score <= 5:
            inflammatory_count = count_inflammatory(ingredients)
            if score == 5:
                bad = []
                for ing in ingredients:
                    n = ing.get("name", "").lower()
                    if is_excluded(n):
                        continue
                    if any(kw in n for kw in NIGHTSHADES):
                        bad.append(f"{ing['name']} (nightshade)")
                    if any(kw in n for kw in DAIRY):
                        bad.append(f"{ing['name']} (dairy)")
                    if any(kw in n for kw in GLUTEN):
                        bad.append(f"{ing['name']} (gluten)")
                if bad:
                    warnings.append(f"{prefix}: score=5 but contains: {', '.join(bad)}")
            elif score == 4:
                if inflammatory_count > 1:
                    warnings.append(f"{prefix}: score=4 but has {inflammatory_count} inflammatory ingredients (expected at most 1)")
            elif score <= 2:
                if inflammatory_count < 2:
                    warnings.append(f"{prefix}: score={score} but only {inflammatory_count} inflammatory ingredients (expected multiple)")

        # --- Tag consistency ---
        tags_lower = [t.lower() for t in tags]
        if "kidney-friendly" in tags_lower and nutrition:
            k = nutrition.get("potassium", 0)
            p = nutrition.get("phosphorus", 0)
            if k >= 600:
                warnings.append(f"{prefix}: tagged 'kidney-friendly' but potassium={k}mg (>=600)")
            if p >= 300:
                warnings.append(f"{prefix}: tagged 'kidney-friendly' but phosphorus={p}mg (>=300)")
        if "low-sodium" in tags_lower and nutrition:
            s = nutrition.get("sodium", 0)
            if s >= 300:
                warnings.append(f"{prefix}: tagged 'low-sodium' but sodium={s}mg (>=300)")
        if "gluten-free" in tags_lower:
            for ing in ingredients:
                if ingredient_contains(ing.get("name", ""), GLUTEN):
                    warnings.append(f"{prefix}: tagged 'gluten-free' but contains '{ing['name']}'")
                    break
        if "dairy-free" in tags_lower:
            for ing in ingredients:
                if ingredient_contains(ing.get("name", ""), DAIRY):
                    warnings.append(f"{prefix}: tagged 'dairy-free' but contains '{ing['name']}'")
                    break

    return errors, warnings, {"fixed": fixed_count}


def print_info(recipes: list[dict]):
    print(f"\n{'='*60}")
    print("INFO SUMMARY")
    print(f"{'='*60}")
    print(f"Total recipes: {len(recipes)}")

    scores = Counter(r.get("autoimmune_score") for r in recipes)
    print(f"\nAutoimmune score distribution:")
    for s in sorted(scores):
        print(f"  Score {s}: {scores[s]}")

    difficulties = Counter(r.get("difficulty") for r in recipes)
    print(f"\nDifficulty distribution:")
    for d in sorted(difficulties):
        print(f"  {d}: {difficulties[d]}")

    all_tags = Counter()
    for r in recipes:
        for t in r.get("tags", []):
            all_tags[t.lower()] += 1
    print(f"\nTop 15 tags:")
    for tag, cnt in all_tags.most_common(15):
        print(f"  {tag}: {cnt}")

    sources = Counter(r.get("source") for r in recipes)
    print(f"\nSource distribution:")
    for s, cnt in sources.most_common():
        print(f"  {s}: {cnt}")


def main():
    auto_fix = "--fix" in sys.argv

    with open(SEED_FILE) as f:
        recipes = json.load(f)

    print(f"Loaded {len(recipes)} recipes from {SEED_FILE}")

    if auto_fix:
        print("Running in AUTO-FIX mode (will clamp out-of-range nutrition values)")

    errors, warnings, stats = validate_recipes(recipes, auto_fix=auto_fix)

    if auto_fix and stats["fixed"] > 0:
        with open(SEED_FILE, "w") as f:
            json.dump(recipes, f, indent=2)
            f.write("\n")
        print(f"\nAuto-fixed {stats['fixed']} nutrition values (clamped to valid ranges)")
        # Re-validate after fix
        errors, warnings, _ = validate_recipes(recipes, auto_fix=False)

    print(f"\n{'='*60}")
    print(f"ERRORS: {len(errors)}")
    print(f"{'='*60}")
    for e in errors:
        print(f"  ERROR: {e}")

    print(f"\n{'='*60}")
    print(f"WARNINGS: {len(warnings)}")
    print(f"{'='*60}")
    for w in warnings:
        print(f"  WARN: {w}")

    print_info(recipes)

    if errors:
        print(f"\n*** {len(errors)} ERRORS found — must fix ***")
        sys.exit(1)
    else:
        print(f"\n*** Validation passed (0 errors, {len(warnings)} warnings) ***")


if __name__ == "__main__":
    main()
