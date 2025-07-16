from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date, Text, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.inspection import inspect
from app.db.base import Base

class MealPlan(Base):
    """
    Model for storing daily meal plans for users
    """
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meal_plan = Column(Text, nullable=False)  # Store the generated meal plan as text
    plan_date = Column(Date, nullable=False)  # Date for which the meal plan is created
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="meal_plans")

    # Unique constraint to ensure one meal plan per user per day
    __table_args__ = (
        UniqueConstraint('user_id', 'plan_date', name='uq_user_meal_plan_date'),
    )
    def to_dict(self):
        data = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
        # Convert datetime/date fields to isoformat for JSON compatibility
        if data.get("plan_date"):
            data["plan_date"] = data["plan_date"].isoformat()
        if data.get("created_at"):
            data["created_at"] = data["created_at"].isoformat() if data["created_at"] else None
        if data.get("updated_at"):
            data["updated_at"] = data["updated_at"].isoformat() if data["updated_at"] else None
        return data
