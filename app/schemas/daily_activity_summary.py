from typing import Dict, List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field


class DataObject(BaseModel):
    datatype: str = Field(..., example="steps", description="Type of health data (steps, heart_rate, sleep, nutrition, weight)")
    source: str = Field(..., example="Google Fit", description="Data source name")
    total_value: Dict[str, float] = Field(..., example={"total_steps_count": 10000.0}, description="Aggregated values with units as key-value pairs")
    date_value: date = Field(..., example="2025-07-14", description="Date for this data summary")


class DailyActivitySummaryBase(BaseModel):
    date_value: date = Field(..., example="2025-07-14", description="Date for this summary")
    datatype: str = Field(..., example="steps", description="Type of health data")
    source: str = Field(..., example="Google Fit", description="Data source name")
    total_value: Dict[str, float] = Field(..., example={"total_steps_count": 10000.0}, description="Aggregated values with units")


class DailyActivitySummaryCreate(DailyActivitySummaryBase):
    user_id: int = Field(..., example=123, description="User ID")


class DailyActivitySummaryUpdate(BaseModel):
    total_value: Dict[str, float] = Field(..., example={"total_steps_count": 12000.0}, description="Updated aggregated values with units")
    source: Optional[str] = Field(None, example="Google Fit", description="Updated data source name")


class DailyActivitySummary(DailyActivitySummaryBase):
    id: int = Field(..., example=1, description="Summary record ID")
    user_id: int = Field(..., example=123, description="User ID")
    created_at: datetime = Field(..., example="2025-07-14T10:30:00Z", description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(None, example="2025-07-14T18:45:00Z", description="Last update timestamp")

    class Config:
        from_attributes = True


class DailyActivitySummaryList(BaseModel):
    items: List[DailyActivitySummary]
    total: int