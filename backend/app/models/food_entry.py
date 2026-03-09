from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class FoodEntry(Base):
    __tablename__ = "food_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String, nullable=False)
    dish_name = Column(String, nullable=False)
    detected_ingredients = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="food_entries")
