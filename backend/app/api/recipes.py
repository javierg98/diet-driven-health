from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.recipe import RecipeCreate, RecipeResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.post("", response_model=RecipeResponse, status_code=201)
def create_recipe(
    recipe_in: RecipeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe_data = recipe_in.model_dump()
    recipe_data["ingredients"] = [i.model_dump() if hasattr(i, "model_dump") else i for i in recipe_in.ingredients]
    recipe_data["nutrition"] = recipe_in.nutrition.model_dump() if hasattr(recipe_in.nutrition, "model_dump") else recipe_in.nutrition
    recipe = Recipe(**recipe_data)
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


@router.get("", response_model=list[RecipeResponse])
def list_recipes(
    tag: str | None = Query(None),
    difficulty: str | None = Query(None),
    search: str | None = Query(None),
    max_time: int | None = Query(None),
    min_score: int | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Recipe)
    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)
    if search:
        query = query.filter(Recipe.name.ilike(f"%{search}%"))
    if max_time:
        query = query.filter(
            (Recipe.prep_time_minutes + Recipe.cook_time_minutes) <= max_time
        )
    if min_score:
        query = query.filter(Recipe.autoimmune_score >= min_score)
    recipes = query.all()
    if tag:
        recipes = [r for r in recipes if tag in (r.tags or [])]
    return recipes


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe
