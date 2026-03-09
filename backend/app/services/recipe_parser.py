import re


def parse_recipe_text(text: str) -> dict:
    """Parse unstructured recipe text into a structured format."""
    lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
    name = lines[0] if lines else "Untitled Recipe"
    ingredients = []
    instructions = []
    current_section = None

    for line in lines[1:]:
        lower = line.lower()
        if lower.startswith("ingredient"):
            current_section = "ingredients"
            continue
        elif lower.startswith("instruction") or lower.startswith("direction") or lower.startswith("method") or lower.startswith("steps"):
            current_section = "instructions"
            continue

        if current_section == "ingredients":
            ingredient = _parse_ingredient_line(line)
            if ingredient:
                ingredients.append(ingredient)
        elif current_section == "instructions":
            step = _parse_instruction_line(line)
            if step:
                instructions.append(step)
        else:
            ingredient = _parse_ingredient_line(line)
            if ingredient and _looks_like_ingredient(line):
                if not current_section:
                    current_section = "ingredients"
                ingredients.append(ingredient)
            elif _looks_like_instruction(line):
                current_section = "instructions"
                step = _parse_instruction_line(line)
                if step:
                    instructions.append(step)

    return {
        "name": name,
        "description": "",
        "ingredients": ingredients,
        "instructions": instructions,
        "prep_time_minutes": 0,
        "cook_time_minutes": 0,
        "difficulty": "intermediate",
        "servings": 2,
        "tags": [],
        "autoimmune_score": 3,
        "nutrition": {"calories": 0, "protein": 0, "sodium": 0, "potassium": 0, "phosphorus": 0},
        "source": "personal",
    }


def _parse_ingredient_line(line: str) -> dict | None:
    cleaned = re.sub(r"^[-•*]\s*", "", line)
    cleaned = re.sub(r"^\d+[\.\)]\s*", "", cleaned)
    match = re.match(
        r"(\d+(?:/\d+)?(?:\.\d+)?)\s*(cup|cups|tbsp|tsp|oz|lb|lbs|piece|pieces|clove|cloves|can|cans|bunch|head|slice|slices|g|kg|ml|l)s?\s+(.+)",
        cleaned,
        re.IGNORECASE,
    )
    if match:
        quantity_str = match.group(1)
        if "/" in quantity_str:
            parts = quantity_str.split("/")
            quantity = float(parts[0]) / float(parts[1])
        else:
            quantity = float(quantity_str)
        return {
            "name": match.group(3).strip().rstrip(","),
            "quantity": quantity,
            "unit": match.group(2).lower().rstrip("s"),
        }
    if cleaned and not _looks_like_instruction(cleaned):
        return {"name": cleaned, "quantity": 1, "unit": "piece"}
    return None


def _parse_instruction_line(line: str) -> str | None:
    cleaned = re.sub(r"^\d+[\.\)]\s*", "", line)
    cleaned = re.sub(r"^[-•*]\s*", "", cleaned)
    return cleaned.strip() if cleaned.strip() else None


def _looks_like_ingredient(line: str) -> bool:
    return bool(re.match(r"^[-•*]?\s*\d", line)) or line.startswith("-")


def _looks_like_instruction(line: str) -> bool:
    action_words = ["cook", "bake", "heat", "add", "mix", "stir", "pour", "place",
                    "bring", "simmer", "boil", "season", "serve", "cut", "dice",
                    "chop", "slice", "squeeze", "preheat", "combine", "whisk", "let"]
    lower = line.lower().lstrip("0123456789.-) ")
    return any(lower.startswith(word) for word in action_words)
