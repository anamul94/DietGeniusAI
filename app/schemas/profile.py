from pydantic import BaseModel
from typing import Optional
from datetime import date

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