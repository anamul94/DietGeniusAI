# schemas/medical.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"

class DietType(str, Enum):
    OMNIVORE = "omnivore"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    KETO = "keto"
    PALEO = "paleo"
    MEDITERRANEAN = "mediterranean"
    LOW_CARB = "low_carb"
    DIABETIC = "diabetic"

class OnboardingStep1(BaseModel):
    """Basic Demographics & Lifestyle"""
    height_cm: float = Field(..., gt=0, le=300)
    weight_kg: float = Field(..., gt=0, le=500)
    blood_type: Optional[str] = Field(None, pattern=r'^(A|B|AB|O)[+-]?$')
    occupation: str = Field(..., min_length=2, max_length=100)
    activity_level: ActivityLevel
    smoking_status: str = Field(..., pattern=r'^(never|former|current)$')
    alcohol_consumption: str = Field(..., pattern=r'^(never|rarely|moderate|heavy)$')

    @validator('height_cm')
    def validate_height(cls, v):
        if v < 50 or v > 300:
            raise ValueError('Height must be between 50-300 cm')
        return v

class OnboardingStep2(BaseModel):
    """Diet Preferences & Restrictions"""
    diet_type: DietType
    food_allergies: List[str] = []
    food_preferences: List[str] = []
    cultural_restrictions: List[str] = []
    cooking_frequency: str = Field(..., pattern=r'^(never|rarely|sometimes|often|daily)$')
    budget_range: str = Field(..., pattern=r'^(low|medium|high)$')

class OnboardingStep3(BaseModel):
    """Health Goals & Targets"""
    primary_goals: List[str] = Field(..., min_items=1)
    target_weight_kg: Optional[float] = Field(None, gt=0, le=500)
    target_timeline_months: Optional[int] = Field(None, gt=0, le=60)
    health_conditions: List[str] = []
    family_history: Dict[str, List[str]] = {}

class OnboardingStep4(BaseModel):
    """Medical History Questionnaire"""
    chronic_conditions: List[str] = []
    current_medications: List[Dict[str, str]] = []
    supplements: List[Dict[str, str]] = []
    allergies: List[str] = []
    last_checkup_date: Optional[date] = None
    has_medical_reports: bool = False

class MedicalReportUpload(BaseModel):
    report_type: str = Field(..., pattern=r'^(BLOOD_TEST|PRESCRIPTION|ECG|RADIOLOGY|GENERAL_CHECKUP)$')
    report_date: Optional[date] = None
    doctor_name: Optional[str] = None
    lab_name: Optional[str] = None

class OnboardingComplete(BaseModel):
    """Final step - complete profile"""
    emergency_contact_name: str
    emergency_contact_phone: str
    preferred_consultation_time: str
    data_sharing_consent: bool = True
    newsletter_subscription: bool = False
    
    
class ReportType(str, Enum):
    BLOOD_TEST = "BLOOD_TEST"
    PRESCRIPTION = "PRESCRIPTION"
    ECG = "ECG"
    RADIOLOGY = "RADIOLOGY"
    GENERAL_CHECKUP = "GENERAL_CHECKUP"

class ProcessingStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class MedicalReportResponse(BaseModel):
    processing_id: str
    user_id: str
    filename: str
    report_type: str
    processing_status: str
    confidence_score: float
    structured_data: Dict[str, Any] = {}
    ai_summary: str = ""
    key_findings: List[str] = []
    nutrition_recommendations: List[Dict[str, Any]] = []
    health_insights: List[Dict[str, Any]] = []
    risk_assessment: Dict[str, Any] = {}
    processed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True