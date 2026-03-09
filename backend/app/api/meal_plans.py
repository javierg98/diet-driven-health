from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.meal_plan import MealPlan
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.meal_plan import MealPlanGenerate, MealPlanResponse, MealSwap
from app.services.recommender import generate_meal_plan, get_swap_recipe
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/meal-plans", tags=["meal-plans"])


@router.post("/generate", response_model=MealPlanResponse, status_code=201)
def create_meal_plan(
    req: MealPlanGenerate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    skill_level = profile.skill_level if profile else "intermediate"
    restrictions = profile.dietary_restrictions if profile else []
    goals = profile.health_goals if profile else []

    days = generate_meal_plan(db, skill_level=skill_level, dietary_restrictions=restrictions, tags=goals)
    plan = MealPlan(user_id=current_user.id, week_start=req.week_start, days=days)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("", response_model=list[MealPlanResponse])
def list_meal_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(MealPlan).filter(MealPlan.user_id == current_user.id).order_by(MealPlan.week_start.desc()).all()


@router.get("/{plan_id}", response_model=MealPlanResponse)
def get_meal_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = db.query(MealPlan).filter(MealPlan.id == plan_id, MealPlan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return plan


@router.put("/{plan_id}/swap", response_model=MealPlanResponse)
def swap_meal(
    plan_id: int,
    swap: MealSwap,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = db.query(MealPlan).filter(MealPlan.id == plan_id, MealPlan.user_id == current_user.id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    days = list(plan.days)
    all_ids = [days[d][m] for d in range(7) for m in ["breakfast", "lunch", "dinner"]]

    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    skill_level = profile.skill_level if profile else "intermediate"

    new_id = get_swap_recipe(db, excluded_ids=all_ids, skill_level=skill_level)
    if new_id is None:
        raise HTTPException(status_code=400, detail="No alternative recipes available")

    days[swap.day_index] = dict(days[swap.day_index])
    days[swap.day_index][swap.meal_type] = new_id
    plan.days = days
    db.commit()
    db.refresh(plan)
    return plan
