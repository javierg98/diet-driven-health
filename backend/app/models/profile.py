from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    skill_level = Column(String, nullable=False, default="intermediate")
    health_conditions = Column(JSON, default=list)
    health_goals = Column(JSON, default=list)
    dietary_restrictions = Column(JSON, default=list)

    user = relationship("User", backref="profile")
