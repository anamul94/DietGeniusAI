from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.food_nutrition import MealType
from app.schemas.nutrition import FoodNutrition as NutritionFoodItem
from app.schemas.nutrition import Nutrition, FoodNutritionList

class UserFoodNutritionBase(BaseModel):
    food_name: str = Field(description="Name of the food item")
    serving_size: str = Field(description="Serving size as specified by user (e.g., '2 chicken wings', '1 bowl')")
    meal_type: MealType = Field(description="Type of meal (breakfast, lunch, dinner, snack, etc.)")
    nutrition: Nutrition = Field(description="Nutritional information for the specified serving size")
    consumed_at: datetime = Field(description="When the food was consumed")

class FoodNutritionCreate(UserFoodNutritionBase):
    pass

class FoodNutritionUpdate(BaseModel):
    food_names: Optional[str] = Field(None, description="Name of the food item")
    serving_size: Optional[str] = Field(None, description="Serving size as specified by user")
    meal_type: Optional[MealType] = Field(None, description="Type of meal")
    nutrition: Optional[Nutrition] = Field(None, description="Nutritional information")
    consumed_at: Optional[datetime] = Field(None, description="When the food was consumed")

class UserFoodNutrition(UserFoodNutritionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Use the existing FoodNutritionList for responses
class FoodNutrition(NutritionFoodItem):
    id: int
    user_id: int
    meal_type: MealType
    consumed_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FoodNutritionPagination(BaseModel):
    items: List[FoodNutritionList]
    total: int
    page: int
    limit: int
    pages: int

class FoodNutritionListResponse(FoodNutritionList):
    """Extended response model for multiple food items with pagination info"""
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    limit: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")