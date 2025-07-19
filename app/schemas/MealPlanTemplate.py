from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class MealEntry(BaseModel):
    breakfast: Optional[str] = Field("", description="Breakfast items for the day.")
    snack_am: Optional[str] = Field("", description="Morning snack items.")
    lunch: Optional[str] = Field("", description="Lunch items for the day.")
    snack_pm: Optional[str] = Field("", description="Afternoon snack items.")
    dinner: Optional[str] = Field("", description="Dinner items for the day.")
    notes: Optional[str] = Field("", description="Notes on timing, hydration, or special instructions.")


class DailySampleMealPlan(BaseModel):
    breakfast: List[str] = Field(..., description="List of example breakfast items.")
    mid_morning_snack: List[str] = Field(..., description="List of example mid-morning snack items.")
    lunch: List[str] = Field(..., description="List of example lunch items.")
    afternoon_snack: List[str] = Field(..., description="List of example afternoon snack items.")
    dinner: List[str] = Field(..., description="List of example dinner items.")


class MacronutrientBreakdownEntry(BaseModel):
    daily_goal: Optional[str] = Field("", description="Target amount per day, e.g., '2000 kcal' or '80g'.")
    percent_total: Optional[str] = Field("", description="Percentage of total daily calories, e.g., '20-25%'.")


class MacronutrientCaloricBreakdown(BaseModel):
    calories: MacronutrientBreakdownEntry = Field(..., description="Daily calorie target.")
    carbohydrates: MacronutrientBreakdownEntry = Field(..., description="Daily carbohydrate intake target.")
    protein: MacronutrientBreakdownEntry = Field(..., description="Daily protein intake target.")
    fat: MacronutrientBreakdownEntry = Field(..., description="Daily fat intake target.")
    fiber: MacronutrientBreakdownEntry = Field(..., description="Daily fiber intake target.")
    water: MacronutrientBreakdownEntry = Field(..., description="Recommended daily water intake.")


class FoodRotationIdeas(BaseModel):
    grains: List[str] = Field(..., description="Examples of recommended grains.")
    proteins: List[str] = Field(..., description="Examples of recommended protein sources.")
    vegetables: List[str] = Field(..., description="Examples of recommended vegetables.")
    fruits: List[str] = Field(..., description="Examples of recommended fruits.")
    healthy_fats: List[str] = Field(..., description="Examples of recommended healthy fats.")


class BehaviorLifestyleRecommendations(BaseModel):
    sleep: Optional[str] = Field("", description="Recommended sleep duration and quality.")
    physical_activity: Optional[str] = Field("", description="Recommended physical activities and frequency.")
    stress_management: Optional[str] = Field("", description="Suggested stress management practices.")
    meal_timing: Optional[str] = Field("", description="Advice on optimal meal timing.")
    hydration: Optional[str] = Field("", description="Recommended daily hydration practices.")
    supplementation: Optional[str] = Field("", description="Guidance on supplements if applicable.")


class FollowUpMonitoringEntry(BaseModel):
    week: int = Field(..., description="Week number for monitoring progress.")
    goal_focus: Optional[str] = Field("", description="Primary focus or goal for this week.")
    plan: Optional[str] = Field("", description="Specific plan of action or adjustments for this week.")


class ClientInformation(BaseModel):
    full_name: Optional[str] = Field("", description="Client's full name.")
    age_gender: Optional[str] = Field("", description="Client's age and gender.")
    height_weight_bmi: Optional[str] = Field("", description="Height, weight, and BMI of the client.")
    occupation_lifestyle: Optional[str] = Field("", description="Work type and daily activity level.")
    location_food_access: Optional[str] = Field("", description="Location and cultural/seasonal food availability.")
    dietary_goals: Optional[str] = Field("", description="Client's dietary goals, e.g., weight loss, maintenance.")
    medical_history: Optional[str] = Field("", description="Relevant medical conditions.")
    food_allergies_intolerances: Optional[str] = Field("", description="Known allergies or intolerances.")
    dietary_preferences: Optional[str] = Field("", description="Preferences such as vegan, paleo, etc.")
    religious_cultural_factors: Optional[str] = Field("", description="Religious or cultural food considerations.")


class ClinicalNutritionalAssessment(BaseModel):
    blood_pressure: Optional[str] = Field("", description="Client's blood pressure readings.")
    fasting_blood_sugar_a1c: Optional[str] = Field("", description="Fasting glucose / A1C levels.")
    lipid_profile: Optional[str] = Field("", description="HDL, LDL, triglyceride levels.")
    hemoglobin_iron_levels: Optional[str] = Field("", description="Iron status including hemoglobin levels.")
    vitamin_d_b12: Optional[str] = Field("", description="Vitamin D and B12 levels.")
    digestive_symptoms: Optional[str] = Field("", description="Any digestive issues like bloating or GERD.")
    appetite_cravings: Optional[str] = Field("", description="General appetite and specific cravings.")
    menstrual_thyroid_status: Optional[str] = Field("", description="Menstrual cycle or thyroid condition status.")


class NutritionistMealPlanResponse(BaseModel):
    client_information: ClientInformation = Field(..., description="Detailed client profile with lifestyle and preferences.")
    clinical_nutritional_assessment: ClinicalNutritionalAssessment = Field(..., description="Relevant clinical data for nutrition planning.")
    weekly_meal_plan_overview: Dict[str, MealEntry] = Field(
        ..., 
        description=(
            "Weekly meal plan broken down by days. Each key is a day like 'Monday', "
            "with values listing meals and notes."
        )
    )
    daily_sample_meal_plan: DailySampleMealPlan = Field(..., description="Example structured daily meal plan for clarity.")
    macronutrient_caloric_breakdown: MacronutrientCaloricBreakdown = Field(..., description="Macro breakdown to guide energy and nutrient balance.")
    food_rotation_ideas: FoodRotationIdeas = Field(..., description="Rotation ideas to ensure diet variety and prevent monotony.")
    behavior_lifestyle_recommendations: BehaviorLifestyleRecommendations = Field(..., description="Behavioral and lifestyle guidance to support the meal plan.")
    follow_up_monitoring_schedule: List[FollowUpMonitoringEntry] = Field(..., description="Planned monitoring schedule to assess and adjust progress.")


class NutritionistMealPlanTemplate(BaseModel):
    meal_plan: NutritionistMealPlanResponse = Field(
        ..., 
        description=(
            "Complete personalized meal plan and recommendations for the client, "
            "including lifestyle, clinical assessment, meals, and follow-up."
        )
    )
    is_complete: bool = Field(
        False,
        description=(
            "Indicates whether the plan creation is finalized. "
            "If True, the system can proceed to delivery or next steps."
        )
    )
    message_on_completion: Optional[str] = Field(
        None,
        description=(
            "Optional message to display upon completion, e.g., 'Meal plan finalized. Ready for client review.'"
        )
    )
