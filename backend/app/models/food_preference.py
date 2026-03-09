from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class FoodPreference(Base):
    __tablename__ = "food_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=False)  # "like" or "dislike"
    value = Column(String, nullable=False)  # the food/cuisine/ingredient
    category = Column(String, nullable=False)  # "ingredient", "cuisine", "dish", "flavor"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="food_preferences")
