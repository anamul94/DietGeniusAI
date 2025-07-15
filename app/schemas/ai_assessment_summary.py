from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


class AIAssessmentSummaryBase(BaseModel):
    date_value: date = Field(..., example="2025-07-15", description="Date for this assessment summary")
    summary: str = Field(..., description="AI-generated assessment summary in markdown format")


class AIAssessmentSummaryCreate(AIAssessmentSummaryBase):
    user_id: int = Field(..., example=123, description="User ID")


class AIAssessmentSummaryUpdate(BaseModel):
    summary: str = Field(..., description="Updated AI-generated assessment summary in markdown format")


class AIAssessmentSummary(AIAssessmentSummaryBase):
    id: int = Field(..., example=1, description="Summary record ID")
    user_id: int = Field(..., example=123, description="User ID")
    created_at: datetime = Field(..., example="2025-07-15T10:30:00Z", description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(None, example="2025-07-15T18:45:00Z", description="Last update timestamp")

    class Config:
        from_attributes = True


class AIAssessmentSummaryResponse(BaseModel):
    date_value: date = Field(..., example="2025-07-15", description="Assessment date")
    summary: str = Field(..., description="AI-generated assessment summary")