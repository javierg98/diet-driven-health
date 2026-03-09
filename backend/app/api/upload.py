from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.upload import RecipeTextInput, ParsedRecipeResponse
from app.services.recipe_parser import parse_recipe_text
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/parse", response_model=ParsedRecipeResponse)
def parse_recipe(
    input: RecipeTextInput,
    current_user: User = Depends(get_current_user),
):
    return parse_recipe_text(input.text)
