from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, UniqueConstraint, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base

class MealType(str, enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    BRUNCH = "brunch"
    SUPPER = "supper"
    OTHER = "other"

class MealEntry(Base):
    """
    Model for storing a meal entry with multiple food items
    """
    __tablename__ = "meal_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meal_type = Column(Enum(MealType), nullable=False)
    foods = Column(JSON, nullable=False)  # Store FoodNutritionList as JSON
    consumed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="meal_entries")

    # Unique constraint to prevent duplicate entries
    __table_args__ = (
        UniqueConstraint('user_id', 'meal_type', 'consumed_at',
                         name='uq_meal_entry'),
    )