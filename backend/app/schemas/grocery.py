from pydantic import BaseModel


class GroceryItem(BaseModel):
    name: str
    quantity: float
    unit: str
    section: str
    estimated_cost: float
    checked: bool = False


class GroceryListResponse(BaseModel):
    meal_plan_id: int
    items: list[GroceryItem]
    total_estimated_cost: float
