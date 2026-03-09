from pydantic import BaseModel


class MealPlanGenerate(BaseModel):
    week_start: str
    meal_types: list[str] = ["breakfast", "lunch", "dinner"]
    cooking_sessions: int | None = None
    weekly_budget: float | None = None
    batch_cooking: bool = False


class DayPlan(BaseModel):
    breakfast: int | None = None
    lunch: int | None = None
    dinner: int | None = None


class MealPlanResponse(BaseModel):
    id: int
    user_id: int
    week_start: str
    days: list[DayPlan]

    class Config:
        from_attributes = True


class MealSwap(BaseModel):
    day_index: int
    meal_type: str
