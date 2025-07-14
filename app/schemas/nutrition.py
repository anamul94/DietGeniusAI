from pydantic import BaseModel, Field
from typing import Optional, List


class NutrientValue(BaseModel):
    value: Optional[float] = Field(description="Numerical value of the nutrient", default=0.0)
    unit: str = Field(description="Unit of measurement (e.g., 'g', 'mg', 'mcg', 'IU', 'kcal')", default="")


class Nutrition(BaseModel):
    calories: NutrientValue = Field(description="Total calories consumed (kcal)", default_factory=lambda: NutrientValue(value=0.0, unit="kcal"))
    protein: Optional[NutrientValue] = Field(description="Total protein intake (g)", default_factory=lambda: NutrientValue(value=0.0, unit="g"))
    carbs: NutrientValue = Field(description="Total carbohydrate intake (g)", default_factory=lambda: NutrientValue(value=0.0, unit="g"))
    fat: NutrientValue = Field(description="Total fat intake (g)", default_factory=lambda: NutrientValue(value=0.0, unit="g"))
    fiber: NutrientValue = Field(description="Total fiber intake (g)", default_factory=lambda: NutrientValue(value=0.0, unit="g"))
    sugar: Optional[NutrientValue] = Field(description="Total sugar intake (g)", default_factory=lambda: NutrientValue(value=0.0, unit="g"))
    cholesterol: Optional[NutrientValue] = Field(description="Total cholesterol intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    sodium: Optional[NutrientValue] = Field(description="Total sodium intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    potassium: Optional[NutrientValue] = Field(description="Total potassium intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    vitamin_a: Optional[NutrientValue] = Field(description="Total vitamin A intake (mcg RAE or IU)", default_factory=lambda: NutrientValue(value=0.0, unit="mcg"))
    vitamin_c: Optional[NutrientValue] = Field(description="Total vitamin C intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    vitamin_d: Optional[NutrientValue] = Field(description="Total vitamin D intake (mcg or IU)", default_factory=lambda: NutrientValue(value=0.0, unit="mcg"))
    vitamin_e: Optional[NutrientValue] = Field(description="Total vitamin E intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    vitamin_k: Optional[NutrientValue] = Field(description="Total vitamin K intake (mcg)", default_factory=lambda: NutrientValue(value=0.0, unit="mcg"))
    thiamin: Optional[NutrientValue] = Field(description="Total thiamin (B1) intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    riboflavin: Optional[NutrientValue] = Field(description="Total riboflavin (B2) intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    niacin: Optional[NutrientValue] = Field(description="Total niacin (B3) intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    vitamin_b6: Optional[NutrientValue] = Field(description="Total vitamin B6 intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    folate: Optional[NutrientValue] = Field(description="Total folate intake (mcg)", default_factory=lambda: NutrientValue(value=0.0, unit="mcg"))
    vitamin_b12: Optional[NutrientValue] = Field(description="Total vitamin B12 intake (mcg)", default_factory=lambda: NutrientValue(value=0.0, unit="mcg"))
    calcium: Optional[NutrientValue] = Field(description="Total calcium intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    iron: Optional[NutrientValue] = Field(description="Total iron intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    magnesium: Optional[NutrientValue] = Field(description="Total magnesium intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    phosphorus: Optional[NutrientValue] = Field(description="Total phosphorus intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    zinc: Optional[NutrientValue] = Field(description="Total zinc intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    selenium: Optional[NutrientValue] = Field(description="Total selenium intake (mcg)", default_factory=lambda: NutrientValue(value=0.0, unit="mcg"))
    copper: Optional[NutrientValue] = Field(description="Total copper intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    manganese: Optional[NutrientValue] = Field(description="Total manganese intake (mg)", default_factory=lambda: NutrientValue(value=0.0, unit="mg"))
    saturated_fat: Optional[NutrientValue] = Field(description="Total saturated fat intake (g)", default_factory=lambda: NutrientValue(value=0.0, unit="g"))
    monounsaturated_fat: Optional[NutrientValue] = Field(description="Total monounsaturated fat intake (g)", default_factory=lambda: NutrientValue(value=0.0, unit="g"))
    polyunsaturated_fat: Optional[NutrientValue] = Field(description="Total polyunsaturated fat intake (g)", default_factory=lambda: NutrientValue(value=0.0, unit="g"))
    omega_3: Optional[NutrientValue] = Field(description="Total omega-3 fatty acids intake (g)", default_factory=lambda: NutrientValue(value=0.0, unit="g"))
    omega_6: Optional[NutrientValue] = Field(description="Total omega-6 fatty acids intake (g)", default_factory=lambda: NutrientValue(value=0.0, unit="g"))


class FoodNutrition(BaseModel):
    food_name: str = Field(description="Name of the food item present in image, eg Pasta, Rice", default="")
    serving_size: str = Field(description="Serving size as specified by user (e.g., '2 chicken wings', '1 bowl')", default="1 serving")
    nutrition: Nutrition = Field(description="Nutritional information for the specified serving size", default_factory=Nutrition)
    
    
class FoodNutritionList(BaseModel):
    """Response model for multiple food items"""
    foods: List[FoodNutrition] = Field(description="List of all unique food items with their nutrition information", default_factory=list)
    
    
class FoodNutritionResponse(BaseModel):
    """Response model for food nutrition information"""
    message: str = Field(description="Message any insight, warning or any other information", default="")
    data: List[FoodNutrition] = Field(description="Food item with its nutrition information", default_factory=FoodNutrition)
    
    # @classmethod
    # def from_list(cls, food_list, message="Successfully parsed nutrition information"):
    #     """
    #     Create a FoodNutritionResponse from a list of food items
    #     Takes the first item if multiple items are provided
    #     """
    #     if isinstance(food_list, list) and len(food_list) > 0:
    #         return cls(message=message, data=food_list[0])
    #     elif isinstance(food_list, dict):
    #         return cls(message=message, data=food_list)
    #     else:
    #         return cls(message="No food data provided", data=FoodNutrition())


# Example usage - this will now work without errors:
# empty_response = FoodNutritionResponse()
# print(empty_response.model_dump())

# print(FoodNutritionResponse.model_json_schema())
# print(json.dumps(FoodNutritionResponse.model_json_schema(), indent=2))