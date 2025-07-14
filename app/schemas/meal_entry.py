from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from app.models.food_nutrition import MealType
from app.schemas.nutrition import FoodNutritionList

class MealEntryBase(BaseModel):
    meal_type: MealType = Field(description="Type of meal (breakfast, lunch, dinner, snack, etc.)")
    foods: FoodNutritionList = Field(description="List of food items with nutrition information")
    consumed_at: datetime = Field(description="When the meal was consumed")

class MealEntryCreate(MealEntryBase):
    pass

class MealEntryUpdate(BaseModel):
    meal_type: Optional[MealType] = Field(None, description="Type of meal")
    foods: Optional[FoodNutritionList] = Field(None, description="List of food items with nutrition information")
    consumed_at: Optional[datetime] = Field(None, description="When the meal was consumed")

class MealEntry(MealEntryBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MealEntryPagination(BaseModel):
    items: list[MealEntry]
    total: int
    page: int
    limit: int
    pages: int

class MealTypeCheck(BaseModel):
    exists: bool = Field(description="Whether the meal type exists for the given date")
    meal_entry: Optional[MealEntry] = Field(None, description="The meal entry if it exists")