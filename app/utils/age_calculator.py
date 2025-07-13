from datetime import date
from typing import Optional

def calculate_age(dob: Optional[date]) -> Optional[int]:
    """Calculate age from date of birth"""
    if not dob:
        return None
    
    today = date.today()
    age = today.year - dob.year
    
    # Adjust if birthday hasn't occurred this year
    if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
        age -= 1
    
    return age