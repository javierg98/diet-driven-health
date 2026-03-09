from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.grocery import GroceryListResponse
from app.services.grocery import generate_grocery_list
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/grocery", tags=["grocery"])


@router.get("/{plan_id}", response_model=GroceryListResponse)
def get_grocery_list(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = generate_grocery_list(db, plan_id, current_user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return result
