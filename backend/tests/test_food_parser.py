from app.services.food_parser import detect_submission_type, parse_food_submission


def test_detect_recipe():
    text = """Garlic Salmon
Ingredients
- 2 lb salmon fillet
- 3 clove garlic
Instructions
1. Preheat oven to 400F
2. Season salmon with garlic
3. Bake for 20 minutes"""
    assert detect_submission_type(text) == "recipe"


def test_detect_likes():
    text = "Thai curry, avocado, lemon, grilled fish, spicy food"
    assert detect_submission_type(text) == "likes"


def test_detect_dislikes():
    text = "I don't like: cilantro, liver, eggplant"
    assert detect_submission_type(text) == "dislikes"


def test_detect_past_meals():
    text = """Last night I made salmon with rice and steamed broccoli.
Today for lunch I had chicken tacos with guacamole."""
    assert detect_submission_type(text) == "past_meals"


def test_parse_recipe():
    text = """Garlic Salmon
Ingredients
- 2 lb salmon fillet
- 3 clove garlic
Instructions
1. Preheat oven to 400F
2. Bake for 20 minutes"""
    result = parse_food_submission(text)
    assert result["detected_type"] == "recipe"
    assert len(result["recipes"]) == 1
    assert result["recipes"][0]["name"] == "Garlic Salmon"


def test_parse_likes():
    text = "Thai curry, avocado, lemon, grilled fish"
    result = parse_food_submission(text)
    assert result["detected_type"] == "likes"
    assert len(result["preferences"]) == 4
    assert result["preferences"][0]["type"] == "like"
    assert result["preferences"][0]["value"] == "thai curry"


def test_parse_dislikes():
    text = "I don't like: cilantro, liver, eggplant"
    result = parse_food_submission(text)
    assert result["detected_type"] == "dislikes"
    assert len(result["preferences"]) == 3
    assert result["preferences"][0]["type"] == "dislike"


def test_parse_past_meals():
    text = """Salmon with rice and steamed broccoli
Chicken tacos with guacamole"""
    result = parse_food_submission(text, submission_type="past_meals")
    assert result["detected_type"] == "past_meals"
    assert len(result["entries"]) == 2
    assert result["entries"][0]["dish_name"] == "Salmon with rice and steamed broccoli"


def test_override_type():
    text = "avocado, salmon, rice"
    result = parse_food_submission(text, submission_type="dislikes")
    assert result["detected_type"] == "dislikes"
    assert all(p["type"] == "dislike" for p in result["preferences"])


def test_categorize_ingredient():
    from app.services.food_parser import _categorize_preference
    assert _categorize_preference("avocado") == "ingredient"
    assert _categorize_preference("thai curry") == "cuisine"
    assert _categorize_preference("spicy food") == "flavor"
