from pydantic import BaseModel
from app.schemas.recipe import RecipeCreate


class FoodSubmissionInput(BaseModel):
    text: str
    submission_type: str | None = None  # "recipe", "past_meals", "likes", "dislikes", or None for auto-detect


class FoodEntryResponse(BaseModel):
    id: int
    user_id: int
    description: str
    dish_name: str
    detected_ingredients: list[str]
    created_at: str

    class Config:
        from_attributes = True


class FoodPreferenceResponse(BaseModel):
    id: int
    user_id: int
    type: str
    value: str
    category: str
    created_at: str

    class Config:
        from_attributes = True


class FoodSubmissionResult(BaseModel):
    """Result of parsing food submission. One of the lists will be populated based on detected_type."""
    detected_type: str  # "recipe", "past_meals", "likes", "dislikes"
    recipes: list[RecipeCreate] = []
    entries: list[dict] = []  # parsed FoodEntry dicts (before DB save)
    preferences: list[dict] = []  # parsed FoodPreference dicts (before DB save)
