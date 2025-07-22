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

class QASummaryResponse(BaseModel):
    """Response model for QA summary endpoints returning summary text and date."""
    summary: str = Field(..., description="Generated summary text from QA session")
    date: datetime = Field(..., description="Creation date of the summary")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "summary": "Based on your responses, you have Type 2 diabetes with good glucose control...",
                "date": "2025-07-15T14:30:00Z"
            }
        }

class QASummaryListResponse(BaseModel):
    """Response model for list of QA summaries."""
    summaries: list[QASummaryResponse] = Field(..., description="List of QA summaries")

    class Config:
        json_schema_extra = {
            "example": [
                {
                    "summary": "Based on your responses, you have Type 2 diabetes with good glucose control...",
                    "date": "2025-07-15T14:30:00Z"
                },
                {
                    "summary": "Initial assessment shows mild hypertension and dietary concerns...",
                    "date": "2025-07-10T09:15:00Z"
                }
            ]
        }