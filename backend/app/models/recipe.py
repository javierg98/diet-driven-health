from sqlalchemy import Column, Integer, String, JSON, Float
from app.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, default="")
    ingredients = Column(JSON, nullable=False)
    instructions = Column(JSON, nullable=False)
    prep_time_minutes = Column(Integer, default=0)
    cook_time_minutes = Column(Integer, default=0)
    difficulty = Column(String, default="intermediate")
    servings = Column(Integer, default=2)
    tags = Column(JSON, default=list)
    autoimmune_score = Column(Integer, default=3)
    nutrition = Column(JSON, default=dict)
    source = Column(String, default="seeded")
