from pydantic import BaseModel, Field
from typing import List


class MealTypeInfo(BaseModel):
    """Individual meal type information"""
    value: str = Field(description="The enum value (e.g., 'breakfast')")
    label: str = Field(description="The display label (e.g., 'Breakfast')")


class MealTypesResponse(BaseModel):
    """Response model for meal types endpoint"""
    meal_types: List[MealTypeInfo] = Field(description="List of available meal types")
    total_count: int = Field(description="Total number of meal types available")


class MealTypesSimpleResponse(BaseModel):
    """Simple response model for meal types endpoint"""
    values: List[str] = Field(description="List of meal type values")
    labels: List[str] = Field(description="List of meal type labels")