from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dish_log import DishLog
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.dish_log import DishLogCreate, DishLogResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/dish-log", tags=["dish-log"])


@router.post("", response_model=DishLogResponse, status_code=201)
def log_dish(
    log_in: DishLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe = db.query(Recipe).filter(Recipe.id == log_in.recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    log = DishLog(user_id=current_user.id, **log_in.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("", response_model=list[DishLogResponse])
def list_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(DishLog).filter(DishLog.user_id == current_user.id).order_by(DishLog.date_cooked.desc()).all()


@router.get("/favorites", response_model=list[DishLogResponse])
def get_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(DishLog)
        .filter(DishLog.user_id == current_user.id, DishLog.rating >= 4, DishLog.would_make_again == True)
        .order_by(DishLog.rating.desc())
        .all()
    )
