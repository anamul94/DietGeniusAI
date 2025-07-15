from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class OnboardingStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=False, index=True)
    username = Column(String(50),  index=True)
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
    
    # Relationships
    medical_reports = relationship("MedicalReport", back_populates="user")
    google_health_tokens = relationship("GoogleHealthToken", back_populates="user")
    google_health_data = relationship("GoogleHealthData", back_populates="user")
    meal_entries = relationship("MealEntry", back_populates="user")
    meal_plans = relationship("MealPlan", back_populates="user")
    daily_activity_summaries = relationship("DailyActivitySummary", back_populates="user")
    ai_assessment_summaries = relationship("AIAssessmentSummary", back_populates="user")