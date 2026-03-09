from pydantic import BaseModel
from app.schemas.recipe import RecipeCreate


class RecipeTextInput(BaseModel):
    text: str


class ParsedRecipeResponse(RecipeCreate):
    pass
