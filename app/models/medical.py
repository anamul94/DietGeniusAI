# models/medical.py
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.db.base import Base

class UserMedicalProfile(Base):
    __tablename__ = "user_medical_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Basic Info
    height_cm = Column(Float)
    weight_kg = Column(Float)
    bmi = Column(Float)
    blood_type = Column(String(5))

    # Medical History
    chronic_conditions = Column(JSON)
    allergies = Column(JSON)
    family_history = Column(JSON)
    current_medications = Column(JSON)
    supplements = Column(JSON)

    # Lifestyle
    occupation = Column(String(100))
    activity_level = Column(String(20))  # sedentary, light, moderate, active, very_active
    smoking_status = Column(String(20))
    alcohol_consumption = Column(String(20))

    # Diet Preferences
    diet_type = Column(String(30))  # omnivore, vegetarian, vegan, keto, etc.
    food_allergies = Column(JSON)
    food_preferences = Column(JSON)
    cultural_restrictions = Column(JSON)

    # Health Goals
    primary_goals = Column(JSON)
    target_weight_kg = Column(Float)
    target_date = Column(DateTime)

    # Risk Assessment
    health_risk_score = Column(Integer)
    nutritional_risk_factors = Column(JSON)

    # Onboarding Status
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=1)

class MedicalReport(Base):
    __tablename__ = "medical_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # BLOOD_TEST, PRESCRIPTION, ECG, RADIOLOGY
    report_date = Column(DateTime)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # File Information
    original_filename = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)

    # Parsed Data
    raw_text = Column(Text)
    structured_data = Column(JSON)
    ai_summary = Column(Text)
    key_findings = Column(JSON)
    recommendations = Column(JSON)

    # Processing Status
    processing_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    confidence_score = Column(Float)

class BloodTestResult(Base):
    __tablename__ = "blood_test_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_report_id = Column(UUID(as_uuid=True), ForeignKey("medical_reports.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_date = Column(DateTime)
    lab_name = Column(String(100))

    # CBC Values
    hemoglobin = Column(Float)
    hematocrit = Column(Float)
    rbc_count = Column(Float)
    wbc_count = Column(Float)
    platelet_count = Column(Float)

    # Lipid Profile
    total_cholesterol = Column(Float)
    ldl_cholesterol = Column(Float)
    hdl_cholesterol = Column(Float)
    triglycerides = Column(Float)

    # Liver Function
    alt = Column(Float)
    ast = Column(Float)
    bilirubin_total = Column(Float)
    albumin = Column(Float)

    # Kidney Function
    creatinine = Column(Float)
    bun = Column(Float)
    egfr = Column(Float)

    # Diabetes Markers
    glucose_fasting = Column(Float)
    glucose_random = Column(Float)
    hba1c = Column(Float)
    insulin = Column(Float)

    # Thyroid
    tsh = Column(Float)
    t3 = Column(Float)
    t4 = Column(Float)

    # Vitamins & Minerals
    vitamin_d = Column(Float)
    vitamin_b12 = Column(Float)
    folate = Column(Float)
    iron = Column(Float)
    ferritin = Column(Float)

    # Status indicators
    abnormal_flags = Column(JSON)
    nutritional_deficiencies = Column(JSON)