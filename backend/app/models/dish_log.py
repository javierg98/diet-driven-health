from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class DishLog(Base):
    __tablename__ = "dish_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    date_cooked = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    rating = Column(Integer, nullable=False)  # 1-5
    notes = Column(String, default="")
    would_make_again = Column(Boolean, default=True)

    user = relationship("User", backref="dish_logs")
    recipe = relationship("Recipe", backref="dish_logs")
