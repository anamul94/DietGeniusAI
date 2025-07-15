from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from app.models.user import DietaryPreference, JoiningPurpose

class ProfileUpdate(BaseModel):
    gender: Optional[str] = None
    dob: Optional[date] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    timezone: Optional[str] = None
    profession: Optional[str] = None
    height: Optional[float] = None  # in cm
    weight: Optional[float] = None  # in kg
    dietary_preference: Optional[str] = None
    purpose_of_joining: Optional[str] = None

class DietaryPreferenceList(BaseModel):
    preferences: List[str] = [p.value for p in DietaryPreference]

class JoiningPurposeList(BaseModel):
    purposes: List[str] = [p.value for p in JoiningPurpose]