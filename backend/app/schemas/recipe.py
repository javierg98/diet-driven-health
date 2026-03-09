from pydantic import BaseModel


class Ingredient(BaseModel):
    name: str
    quantity: float
    unit: str


class Nutrition(BaseModel):
    calories: int = 0
    protein: int = 0
    sodium: int = 0
    potassium: int = 0
    phosphorus: int = 0


class RecipeCreate(BaseModel):
    name: str
    description: str = ""
    ingredients: list[Ingredient]
    instructions: list[str]
    prep_time_minutes: int = 0
    cook_time_minutes: int = 0
    difficulty: str = "intermediate"
    servings: int = 2
    tags: list[str] = []
    autoimmune_score: int = 3
    nutrition: Nutrition = Nutrition()
    source: str = "seeded"


class RecipeResponse(BaseModel):
    id: int
    name: str
    description: str
    ingredients: list[Ingredient]
    instructions: list[str]
    prep_time_minutes: int
    cook_time_minutes: int
    difficulty: str
    servings: int
    tags: list[str]
    autoimmune_score: int
    nutrition: Nutrition
    source: str

    class Config:
        from_attributes = True
