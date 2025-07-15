from datetime import date, datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.daily_activity_summary import (
    DailyActivitySummary,
    DailyActivitySummaryList,
    DataObject
)
from app.services.daily_activity_summary import (
    process_daily_health_data_by_date,
    get_daily_activity_summaries,
    fetch_and_process_daily_health_data
)
from app.core.logging import logger

router = APIRouter()


@router.post("/process-daily-data/{target_date}", response_model=List[DailyActivitySummary])
async def process_daily_health_data(
    target_date: date = Path(
        ...,
        description="Target date to process health data for",
        example="2025-07-14"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process Google Health data for a specific date and save to daily activity summary.
    
    This endpoint:
    1. Fetches Google Health data for the specified date
    2. Groups data by data_type and aggregates values
    3. Saves/updates the daily activity summary table
    4. Ensures only one record per day per data type
    
    **Example Response:**
    ```json
    [
        {
            "id": 1,
            "user_id": 123,
            "date_value": "2025-07-14",
            "datatype": "steps",
            "source": "Google Fit",
            "total_value": {"total_steps_count": 10000.0},
            "created_at": "2025-07-14T10:30:00Z",
            "updated_at": null
        },
        {
            "id": 2,
            "user_id": 123,
            "date_value": "2025-07-14",
            "datatype": "heart_rate",
            "source": "Google Fit",
            "total_value": {"average_heart_rate_bpm": 72.5},
            "created_at": "2025-07-14T10:30:00Z",
            "updated_at": null
        }
    ]
    ```
    """
    try:
        logger.info(f"Processing daily health data for user {current_user.id} on {target_date}")
        
        summaries = await process_daily_health_data_by_date(
            db=db,
            user_id=current_user.id,
            target_date=target_date
        )
        
        if not summaries:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No health data found for date {target_date}"
            )
        
        return summaries
        
    except Exception as e:
        logger.error(f"Error processing daily health data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing daily health data: {str(e)}"
        )


@router.get("/preview-data/{target_date}", response_model=List[DataObject])
async def preview_daily_data_objects(
    target_date: date = Path(
        ...,
        description="Target date to preview health data for",
        example="2025-07-14"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Preview the processed DataObject format for a specific date without saving to database.
    
    This endpoint shows how the raw Google Health data will be processed and grouped
    before being saved to the daily activity summary table.
    
    **Example Response:**
    ```json
    [
        {
            "datatype": "steps",
            "source": "Google Fit",
            "total_value": {"total_steps_count": 10000.0},
            "date_value": "2025-07-14"
        },
        {
            "datatype": "heart_rate",
            "source": "Google Fit",
            "total_value": {"average_heart_rate_bpm": 72.5},
            "date_value": "2025-07-14"
        },
        {
            "datatype": "sleep",
            "source": "Google Fit",
            "total_value": {
                "total_sleep_duration_minutes": 480.0,
                "sleep_stage_light_sleep_duration_minutes": 240.0,
                "sleep_stage_deep_sleep_duration_minutes": 120.0,
                "sleep_stage_rem_sleep_duration_minutes": 120.0
            },
            "date_value": "2025-07-14"
        }
    ]
    ```
    """
    try:
        logger.info(f"Previewing data objects for user {current_user.id} on {target_date}")
        
        data_objects = await fetch_and_process_daily_health_data(
            db=db,
            user_id=current_user.id,
            target_date=target_date
        )
        
        if not data_objects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No health data found for date {target_date}"
            )
        
        return data_objects
        
    except Exception as e:
        logger.error(f"Error previewing daily data objects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error previewing daily data objects: {str(e)}"
        )


@router.get("/summaries", response_model=List[DailyActivitySummary])
async def get_user_daily_summaries(
    start_date: Optional[date] = Query(
        default=None,
        description="Filter summaries from this date onwards",
        example="2025-07-01"
    ),
    end_date: Optional[date] = Query(
        default=None,
        description="Filter summaries up to this date",
        example="2025-07-31"
    ),
    datatype: Optional[str] = Query(
        default=None,
        description="Filter by specific data type",
        example="steps",
        regex="^(steps|heart_rate|sleep|nutrition|weight)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get daily activity summaries for the current user with optional filters.
    
    **Query Parameters:**
    - `start_date`: Filter summaries from this date onwards (e.g., "2025-07-01")
    - `end_date`: Filter summaries up to this date (e.g., "2025-07-31")
    - `datatype`: Filter by specific data type ("steps", "heart_rate", "sleep", "nutrition", "weight")
    
    **Example Usage:**
    - Get all summaries: `/summaries`
    - Get steps data for July: `/summaries?start_date=2025-07-01&end_date=2025-07-31&datatype=steps`
    - Get recent week: `/summaries?start_date=2025-07-07`
    
    **Example Response:**
    ```json
    [
        {
            "id": 1,
            "user_id": 123,
            "date_value": "2025-07-14",
            "datatype": "steps",
            "source": "Google Fit",
            "total_value": {"total_steps_count": 10000.0},
            "created_at": "2025-07-14T10:30:00Z",
            "updated_at": null
        },
        {
            "id": 2,
            "user_id": 123,
            "date_value": "2025-07-13",
            "datatype": "steps",
            "source": "Google Fit",
            "total_value": {"total_steps_count": 8500.0},
            "created_at": "2025-07-13T09:15:00Z",
            "updated_at": "2025-07-13T18:30:00Z"
        }
    ]
    ```
    """
    try:
        summaries = await get_daily_activity_summaries(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            datatype=datatype
        )
        
        return summaries
        
    except Exception as e:
        logger.error(f"Error fetching daily summaries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching daily summaries: {str(e)}"
        )


@router.get("/summaries/{target_date}", response_model=List[DailyActivitySummary])
async def get_daily_summaries_by_date(
    target_date: date = Path(
        ...,
        description="Specific date to get summaries for",
        example="2025-07-14"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all daily activity summaries for a specific date.
    
    **Example Response:**
    ```json
    [
        {
            "id": 1,
            "user_id": 123,
            "date_value": "2025-07-14",
            "datatype": "steps",
            "source": "Google Fit",
            "total_value": {"total_steps_count": 10000.0},
            "created_at": "2025-07-14T10:30:00Z",
            "updated_at": null
        },
        {
            "id": 2,
            "user_id": 123,
            "date_value": "2025-07-14",
            "datatype": "heart_rate",
            "source": "Google Fit",
            "total_value": {"average_heart_rate_bpm": 72.5},
            "created_at": "2025-07-14T10:30:00Z",
            "updated_at": null
        },
        {
            "id": 3,
            "user_id": 123,
            "date_value": "2025-07-14",
            "datatype": "sleep",
            "source": "Google Fit",
            "total_value": {"total_sleep_duration_minutes": 480.0},
            "created_at": "2025-07-14T10:30:00Z",
            "updated_at": null
        }
    ]
    ```
    """
    try:
        summaries = await get_daily_activity_summaries(
            db=db,
            user_id=current_user.id,
            start_date=target_date,
            end_date=target_date
        )
        
        return summaries
        
    except Exception as e:
        logger.error(f"Error fetching daily summaries for {target_date}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching daily summaries: {str(e)}"
        )