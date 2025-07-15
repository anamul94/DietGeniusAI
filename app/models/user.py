from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base
from app.models.water_intake import WaterIntake

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class OnboardingStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class DietaryPreference(str, enum.Enum):
    VEGETARIAN = "Vegetarian"
    VEGAN = "Vegan"
    PESCATARIAN = "Pescatarian"
    OMNIVORE = "Omnivore"
    FLEXITARIAN = "Flexitarian"
    KETO = "Keto"
    PALEO = "Paleo"
    LOW_CARB = "Low-Carb"
    HIGH_PROTEIN = "High-Protein"
    GLUTEN_FREE = "Gluten-Free"
    DAIRY_FREE = "Dairy-Free"
    HALAL = "Halal"
    KOSHER = "Kosher"
    DIABETIC_FRIENDLY = "Diabetic-Friendly"
    HEART_HEALTHY = "Heart-Healthy"
    LOW_SODIUM = "Low-Sodium"
    MEDITERRANEAN = "Mediterranean"
    FODMAP = "FODMAP"
    IBS_FRIENDLY = "IBS-Friendly"
    CARNIVORE = "Carnivore"

class JoiningPurpose(str, enum.Enum):
    WEIGHT_LOSS = "Weight Loss"
    WEIGHT_GAIN = "Weight Gain"
    MUSCLE_BUILDING = "Muscle Building"
    GENERAL_FITNESS = "General Fitness"
    IMPROVE_ENERGY = "Improve Energy"
    MANAGE_DIABETES = "Manage Diabetes"
    CONTROL_BLOOD_PRESSURE = "Control Blood Pressure"
    MANAGE_CHOLESTEROL = "Manage Cholesterol"
    DIGESTIVE_HEALTH = "Digestive Health"
    IBS_MANAGEMENT = "IBS Management"
    IMPROVE_SLEEP = "Improve Sleep"
    MENTAL_HEALTH = "Mental Health Support"
    HEART_HEALTH = "Heart Health"
    HORMONAL_BALANCE = "Hormonal Balance"
    IMPROVE_IMMUNITY = "Improve Immunity"
    PREGNANCY_NUTRITION = "Pregnancy Nutrition"
    POSTPARTUM_RECOVERY = "Postpartum Recovery"
    SPORTS_PERFORMANCE = "Sports Performance"
    HEALTHY_AGING = "Healthy Aging"
    MEDICAL_CONDITION = "Medical Condition Management"
    PCOS_MANAGEMENT = "PCOS Management"
    OVERALL_WELLNESS = "Overall Wellness"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=False, index=True)
    username = Column(String(50), index=True)
    avatar = Column(String)
    gender = Column(String(10))
    dob = Column(DateTime)
    phone = Column(String(20))
    address = Column(String)
    city = Column(String(50))
    country = Column(String(50))
    postal_code = Column(String(20))
    timezone = Column(String(50))
    profession = Column(String(100))
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    onboarding_status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # New fields
    height = Column(Float)  # in cm
    weight = Column(Float)  # in kg
    bmi = Column(Float)
    dietary_preference = Column(String)  # Store as string to allow multiple selections
    purpose_of_joining = Column(String)  # Store as string to allow multiple selections
    
    # Relationships
    medical_reports = relationship("MedicalReport", back_populates="user")
    google_health_tokens = relationship("GoogleHealthToken", back_populates="user")
    google_health_data = relationship("GoogleHealthData", back_populates="user")
    meal_entries = relationship("MealEntry", back_populates="user")
    meal_plans = relationship("MealPlan", back_populates="user")
    daily_activity_summaries = relationship("DailyActivitySummary", back_populates="user")
    ai_assessment_summaries = relationship("AIAssessmentSummary", back_populates="user")
    water_intakes = relationship("WaterIntake", back_populates="user")