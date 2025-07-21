from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class QASessionSummaryCreate(BaseModel):
    user_id: int = Field(..., description="User ID associated with this session")
    session_type: str = Field(..., description="Type of session (e.g., 'base_condition', 'onboarding')")
    summary: str = Field(..., description="Generated summary text")
    conversation_data: Optional[Dict[str, Any]] = Field(None, description="Full conversation data")
    session_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional session metadata")

class QASessionSummaryResponse(BaseModel):
    id: int
    user_id: int
    session_type: str
    summary: str
    conversation_data: Optional[Dict[str, Any]]
    session_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True