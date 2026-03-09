from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.food_entry import FoodEntry
from app.models.food_preference import FoodPreference
from app.models.user import User
from app.schemas.food_submission import (
    FoodSubmissionInput,
    FoodSubmissionResult,
    FoodEntryResponse,
    FoodPreferenceResponse,
)
from app.services.food_parser import parse_food_submission
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/food", tags=["food"])


@router.post("/parse", response_model=FoodSubmissionResult)
def parse_submission(
    req: FoodSubmissionInput,
    current_user: User = Depends(get_current_user),
):
    result = parse_food_submission(req.text, submission_type=req.submission_type)
    return result


@router.post("/save", status_code=201)
def save_submission(
    req: FoodSubmissionResult,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    saved_recipes = 0
    saved_entries = 0
    saved_preferences = 0

    for entry_data in req.entries:
        entry = FoodEntry(
            user_id=current_user.id,
            description=entry_data["description"],
            dish_name=entry_data["dish_name"],
            detected_ingredients=entry_data.get("detected_ingredients", []),
        )
        db.add(entry)
        saved_entries += 1

    for pref_data in req.preferences:
        pref = FoodPreference(
            user_id=current_user.id,
            type=pref_data["type"],
            value=pref_data["value"],
            category=pref_data.get("category", "ingredient"),
        )
        db.add(pref)
        saved_preferences += 1

    saved_recipes = len(req.recipes)
    db.commit()
    return {
        "saved_recipes": saved_recipes,
        "saved_entries": saved_entries,
        "saved_preferences": saved_preferences,
    }


@router.get("/preferences", response_model=list[FoodPreferenceResponse])
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(FoodPreference).filter(
        FoodPreference.user_id == current_user.id
    ).order_by(FoodPreference.created_at.desc()).all()


@router.get("/entries", response_model=list[FoodEntryResponse])
def get_food_entries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(FoodEntry).filter(
        FoodEntry.user_id == current_user.id
    ).order_by(FoodEntry.created_at.desc()).all()
