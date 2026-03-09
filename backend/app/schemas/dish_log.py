from datetime import datetime
from pydantic import BaseModel


class DishLogCreate(BaseModel):
    recipe_id: int
    rating: int  # 1-5
    notes: str = ""
    would_make_again: bool = True


class DishLogResponse(BaseModel):
    id: int
    user_id: int
    recipe_id: int
    date_cooked: datetime
    rating: int
    notes: str
    would_make_again: bool

    class Config:
        from_attributes = True
