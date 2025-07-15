from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date

class MealPlanBase(BaseModel):
    meal_plan: str = Field(description="The generated meal plan content")
    plan_date: date = Field(description="Date for which the meal plan is created")

class MealPlanCreate(MealPlanBase):
    pass

class MealPlanUpdate(BaseModel):
    meal_plan: Optional[str] = Field(None, description="The updated meal plan content")

class MealPlan(MealPlanBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MealPlanPagination(BaseModel):
    items: list[MealPlan]
    total: int
    page: int
    limit: int
    pages: int

class MealPlanResponse(BaseModel):
    success: bool = Field(description="Whether the meal plan was created successfully")
    message: str = Field(description="Response message")
    meal_plan: Optional[MealPlan] = Field(None, description="The created meal plan")

class GenerateMealPlanRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="Session ID for tracking")