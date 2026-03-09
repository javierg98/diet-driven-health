import json
import os
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dish_log import DishLog
from app.models.meal_plan import MealPlan
from app.models.recipe import Recipe
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["admin"])

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _load_json(filename: str) -> dict | None:
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


@router.get("/skill-results")
def get_skill_results(
    current_user: User = Depends(get_current_user),
):
    return {
        "user_preferences": _load_json("user_preferences.json"),
        "user_memory": _load_json("user_memory.json"),
        "recommendation_weights": _load_json("recommendation_weights.json"),
    }


@router.get("/health-trend")
def get_health_trend(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logs = (
        db.query(DishLog)
        .filter(DishLog.user_id == current_user.id)
        .order_by(DishLog.date_cooked.asc())
        .all()
    )

    if not logs:
        return {"weekly_scores": [], "overall_average": 0, "total_logs": 0, "adherence_percent": 0}

    recipe_ids = list({log.recipe_id for log in logs})
    recipes = db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()
    recipe_scores = {r.id: r.autoimmune_score for r in recipes}

    weekly = defaultdict(list)
    all_scores = []
    for log in logs:
        score = recipe_scores.get(log.recipe_id, 3)
        all_scores.append(score)
        week_key = log.date_cooked.strftime("%Y-W%W") if log.date_cooked else "unknown"
        weekly[week_key].append(score)

    weekly_scores = [
        {"week": week, "average": round(sum(scores) / len(scores), 1), "count": len(scores)}
        for week, scores in sorted(weekly.items())
    ]

    overall_average = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0

    plans = db.query(MealPlan).filter(MealPlan.user_id == current_user.id).all()
    planned_count = 0
    for plan in plans:
        for day in (plan.days or []):
            for meal_type in ["breakfast", "lunch", "dinner"]:
                if day.get(meal_type) is not None:
                    planned_count += 1

    adherence = round(len(logs) / max(planned_count, 1) * 100, 1)

    return {
        "weekly_scores": weekly_scores,
        "overall_average": overall_average,
        "total_logs": len(logs),
        "adherence_percent": adherence,
    }
