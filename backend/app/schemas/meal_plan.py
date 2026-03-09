from pydantic import BaseModel


class MealPlanGenerate(BaseModel):
    week_start: str


class DayPlan(BaseModel):
    breakfast: int
    lunch: int
    dinner: int


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
