from app.schemas.food_submission import (
    FoodSubmissionInput,
    FoodEntryResponse,
    FoodPreferenceResponse,
    FoodSubmissionResult,
)


def test_submission_input_defaults():
    inp = FoodSubmissionInput(text="Salmon with rice")
    assert inp.submission_type is None
    assert inp.text == "Salmon with rice"


def test_submission_input_with_type():
    inp = FoodSubmissionInput(text="cilantro, liver", submission_type="dislikes")
    assert inp.submission_type == "dislikes"


def test_food_entry_response():
    resp = FoodEntryResponse(
        id=1, user_id=1, description="Salmon dinner",
        dish_name="Salmon", detected_ingredients=["salmon"],
        created_at="2026-03-09T12:00:00",
    )
    assert resp.dish_name == "Salmon"


def test_food_preference_response():
    resp = FoodPreferenceResponse(
        id=1, user_id=1, type="like", value="avocado",
        category="ingredient", created_at="2026-03-09T12:00:00",
    )
    assert resp.type == "like"


def test_submission_result_recipe():
    result = FoodSubmissionResult(
        detected_type="recipe",
        recipes=[],
        entries=[],
        preferences=[],
    )
    assert result.detected_type == "recipe"


def test_submission_result_mixed():
    result = FoodSubmissionResult(
        detected_type="likes",
        recipes=[],
        entries=[],
        preferences=[],
    )
    assert result.detected_type == "likes"
