from pydantic import BaseModel


class ProfileCreate(BaseModel):
    skill_level: str = "intermediate"
    health_conditions: list[str] = []
    health_goals: list[str] = []
    dietary_restrictions: list[str] = []


class ProfileResponse(ProfileCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True
