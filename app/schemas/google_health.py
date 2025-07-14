from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

class GoogleHealthTokenBase(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_at: datetime
    scope: str

class GoogleHealthTokenCreate(GoogleHealthTokenBase):
    user_id: int

class GoogleHealthToken(GoogleHealthTokenBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GoogleHealthDataBase(BaseModel):
    data_type: str
    start_time: datetime
    end_time: datetime
    value: Dict[str, Any]
    source: Optional[str] = None

class GoogleHealthDataCreate(GoogleHealthDataBase):
    user_id: int

class GoogleHealthData(GoogleHealthDataBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class GoogleHealthDataList(BaseModel):
    items: List[GoogleHealthData]
    total: int

class GoogleHealthAuthRequest(BaseModel):
    code: str
    redirect_uri: str

class GoogleHealthAuthResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str

class GoogleHealthDataRequest(BaseModel):
    data_types: List[str] = Field(
        default=["steps", "heart_rate", "sleep", "weight", "nutrition"],
        description="List of data types to fetch from Google Health"
    )
    start_date: Optional[datetime] = Field(
        default=None,
        description="Start date for data retrieval (defaults to 24 hours ago if not provided)"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="End date for data retrieval (defaults to current time if not provided)"
    )

class GoogleHealthDataResponse(BaseModel):
    data: List[GoogleHealthData]
    count: int