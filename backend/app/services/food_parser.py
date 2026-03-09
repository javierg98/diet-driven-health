import re

from app.services.recipe_parser import parse_recipe_text


CUISINE_KEYWORDS = [
    "thai", "mexican", "italian", "japanese", "chinese", "indian", "korean",
    "mediterranean", "greek", "french", "vietnamese", "middle eastern",
    "curry", "tacos", "pasta", "sushi", "ramen", "stir fry",
]

FLAVOR_KEYWORDS = [
    "spicy", "sweet", "savory", "sour", "bitter", "umami", "smoky",
    "tangy", "mild", "rich", "creamy", "crispy", "herbal", "citrusy",
]

DISLIKE_PATTERNS = [
    r"(?:i\s+)?(?:don'?t|do\s+not)\s+(?:like|enjoy|eat|want)",
    r"(?:i\s+)?(?:hate|dislike|avoid|can'?t\s+stand)",
    r"no\s+(?:more\s+)?(?:thanks|thank)",
    r"not\s+a\s+fan",
]

PAST_MEAL_PATTERNS = [
    r"(?:i|we)\s+(?:made|had|ate|cooked|prepared)",
    r"(?:last\s+night|today|yesterday|this\s+(?:morning|week))",
    r"for\s+(?:breakfast|lunch|dinner|brunch)",
]


def detect_submission_type(text: str) -> str:
    """Auto-detect whether text is a recipe, likes, dislikes, or past meals."""
    lower = text.lower()
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]

    # Check for recipe structure: section headers like "Ingredients" or "Instructions"
    has_ingredient_header = any(
        line.lower().startswith(("ingredient", "instruction", "direction", "method", "steps"))
        for line in lines
    )
    if has_ingredient_header and len(lines) >= 4:
        return "recipe"

    # Check for dislike indicators
    for pattern in DISLIKE_PATTERNS:
        if re.search(pattern, lower):
            return "dislikes"

    # Check for past meal indicators
    for pattern in PAST_MEAL_PATTERNS:
        if re.search(pattern, lower):
            return "past_meals"

    # Check if it's a comma-separated list (likely preferences)
    if "," in text and len(lines) <= 3:
        return "likes"

    # Multi-line without structure -> past meals
    if len(lines) >= 2:
        return "past_meals"

    # Default to likes for short single-line input
    return "likes"


def _categorize_preference(value: str) -> str:
    """Categorize a food preference as ingredient, cuisine, dish, or flavor."""
    lower = value.lower()
    for keyword in CUISINE_KEYWORDS:
        if keyword in lower:
            return "cuisine"
    for keyword in FLAVOR_KEYWORDS:
        if keyword in lower:
            return "flavor"
    # Multi-word items with common dish patterns
    if any(word in lower for word in ["with", "and", "on", "over"]):
        return "dish"
    return "ingredient"


def _parse_comma_list(text: str) -> list[str]:
    """Split comma/newline-separated items, cleaning prefixes like 'I don't like:'."""
    cleaned = re.sub(
        r"^(?:i\s+(?:don'?t|do\s+not)\s+(?:like|enjoy|eat|want)\s*[:;]?\s*|"
        r"i\s+(?:like|enjoy|love|prefer)\s*[:;]?\s*|"
        r"(?:likes?|dislikes?|avoid)\s*[:;]?\s*)",
        "", text.strip(), flags=re.IGNORECASE,
    )
    items = re.split(r"[,\n]+", cleaned)
    return [item.strip().lower() for item in items if item.strip()]


def _extract_ingredients_from_description(text: str) -> list[str]:
    """Extract likely ingredient words from a meal description."""
    stop_words = {
        "with", "and", "the", "a", "an", "some", "of", "in", "on", "for",
        "made", "had", "ate", "cooked", "prepared", "steamed", "grilled",
        "baked", "fried", "roasted", "sauteed", "boiled", "fresh", "i", "we",
        "last", "night", "today", "yesterday", "lunch", "dinner", "breakfast",
    }
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [w for w in words if w not in stop_words and len(w) > 2]


def parse_food_submission(text: str, submission_type: str | None = None) -> dict:
    """Parse food submission text. Returns dict matching FoodSubmissionResult schema."""
    detected = submission_type or detect_submission_type(text)

    if detected == "recipe":
        parsed = parse_recipe_text(text)
        return {
            "detected_type": "recipe",
            "recipes": [parsed],
            "entries": [],
            "preferences": [],
        }

    if detected in ("likes", "dislikes"):
        pref_type = "like" if detected == "likes" else "dislike"
        items = _parse_comma_list(text)
        preferences = [
            {
                "type": pref_type,
                "value": item,
                "category": _categorize_preference(item),
            }
            for item in items
        ]
        return {
            "detected_type": detected,
            "recipes": [],
            "entries": [],
            "preferences": preferences,
        }

    if detected == "past_meals":
        lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
        entries = []
        for line in lines:
            dish = re.sub(
                r"^(?:(?:last\s+night|today|yesterday|this\s+\w+)\s+)?(?:i|we)\s+(?:made|had|ate|cooked|prepared)\s+",
                "", line, flags=re.IGNORECASE,
            ).strip().rstrip(".")
            if not dish:
                dish = line
            entries.append({
                "description": line,
                "dish_name": dish,
                "detected_ingredients": _extract_ingredients_from_description(dish),
            })
        return {
            "detected_type": "past_meals",
            "recipes": [],
            "entries": entries,
            "preferences": [],
        }

    return {"detected_type": detected, "recipes": [], "entries": [], "preferences": []}
