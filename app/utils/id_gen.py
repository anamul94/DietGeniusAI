import uuid
from datetime import datetime

def generate_unique_id():
    return str(uuid.uuid4())

def generate_custom_id(user_id: str) -> str:
    # Generate UUID4
    unique_id = generate_unique_id()
    
    # Current UTC datetime in YYYYMMDDHHMMSS format
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    
    # Combine all parts
    custom_id = f"{unique_id}-{timestamp}-{user_id}"
    
    return custom_id