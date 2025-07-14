from pydantic import BaseModel, Field
from typing import Optional


class NutrientValue(BaseModel):
    value: Optional[float] = Field(description="Numerical value of the nutrient")
    unit: str = Field(description="Unit of measurement (e.g., 'g', 'mg', 'mcg', 'IU', 'kcal')")


class Nutrition(BaseModel):
    calories: Optional[NutrientValue] = Field(description="Total calories consumed (kcal)")
    protein: Optional[NutrientValue] = Field(description="Total protein intake (g)")
    carbs: Optional[NutrientValue] = Field(description="Total carbohydrate intake (g)")
    fat: Optional[NutrientValue] = Field(description="Total fat intake (g)")
    fiber: Optional[NutrientValue] = Field(description="Total fiber intake (g)")
    sugar: Optional[NutrientValue] = Field(description="Total sugar intake (g)")
    cholesterol: Optional[NutrientValue] = Field(description="Total cholesterol intake (mg)")
    sodium: Optional[NutrientValue] = Field(description="Total sodium intake (mg)")
    potassium: Optional[NutrientValue] = Field(description="Total potassium intake (mg)")
    vitamin_a: Optional[NutrientValue] = Field(description="Total vitamin A intake (mcg RAE or IU)")
    vitamin_c: Optional[NutrientValue] = Field(description="Total vitamin C intake (mg)")
    vitamin_d: Optional[NutrientValue] = Field(description="Total vitamin D intake (mcg or IU)")
    vitamin_e: Optional[NutrientValue] = Field(description="Total vitamin E intake (mg)")
    vitamin_k: Optional[NutrientValue] = Field(description="Total vitamin K intake (mcg)")
    thiamin: Optional[NutrientValue] = Field(description="Total thiamin (B1) intake (mg)")
    riboflavin: Optional[NutrientValue] = Field(description="Total riboflavin (B2) intake (mg)")
    niacin: Optional[NutrientValue] = Field(description="Total niacin (B3) intake (mg)")
    vitamin_b6: Optional[NutrientValue] = Field(description="Total vitamin B6 intake (mg)")
    folate: Optional[NutrientValue] = Field(description="Total folate intake (mcg)")
    vitamin_b12: Optional[NutrientValue] = Field(description="Total vitamin B12 intake (mcg)")
    calcium: Optional[NutrientValue] = Field(description="Total calcium intake (mg)")
    iron: Optional[NutrientValue] = Field(description="Total iron intake (mg)")
    magnesium: Optional[NutrientValue] = Field(description="Total magnesium intake (mg)")
    phosphorus: Optional[NutrientValue] = Field(description="Total phosphorus intake (mg)")
    zinc: Optional[NutrientValue] = Field(description="Total zinc intake (mg)")
    selenium: Optional[NutrientValue] = Field(description="Total selenium intake (mcg)")
    copper: Optional[NutrientValue] = Field(description="Total copper intake (mg)")
    manganese: Optional[NutrientValue] = Field(description="Total manganese intake (mg)")
    saturated_fat: Optional[NutrientValue] = Field(description="Total saturated fat intake (g)")
    monounsaturated_fat: Optional[NutrientValue] = Field(description="Total monounsaturated fat intake (g)")
    polyunsaturated_fat: Optional[NutrientValue] = Field(description="Total polyunsaturated fat intake (g)")
    omega_3: Optional[NutrientValue] = Field(description="Total omega-3 fatty acids intake (g)")
    omega_6: Optional[NutrientValue] = Field(description="Total omega-6 fatty acids intake (g)")


class FoodNutrition(BaseModel):
    food_name: str = Field(description="Name of the food item")
    serving_size: str = Field(description="Serving size as specified by user (e.g., '2 chicken wings', '1 bowl')")
    nutrition: Nutrition = Field(description="Nutritional information for the specified serving size")
    
    
class FoodNutritionList(BaseModel):
    """Response model for multiple food items"""
    foods: list[FoodNutrition] = Field(description="List of all unique food items with their nutrition information")