from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.qa_summary import (
    get_latest_qa_summary_by_user_id,
    get_qa_summaries_by_user_id,
    QASummaryServiceError
)
from app.core.logging import logger
from app.schemas.qa_session_summary import QASummaryResponse

router = APIRouter()

@router.get("/latest", response_model=Optional[QASummaryResponse])
async def get_latest_qa_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the latest QA summary for the current user.
    
    This endpoint returns only the summary text and creation date of the most recent
    QA session summary for the authenticated user.
    
    **Example Response:**
    ```json
    {
        "summary": "Based on your responses, you have Type 2 diabetes with good glucose control...",
        "date": "2025-07-15T14:30:00Z"
    }
    ```
    
    **Example Response (when no summary exists):**
    ```json
    null
    ```
    """
    try:
        summary = get_latest_qa_summary_by_user_id(
            db=db,
            user_id=current_user.id
        )
        
        return summary
        
    except QASummaryServiceError as e:
        logger.error(f"QA summary service error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving QA summary: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving QA summary for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the QA summary"
        )

@router.get("/all", response_model=List[QASummaryResponse])
async def get_all_qa_summaries(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all QA summaries for the current user.
    
    This endpoint returns a list of QA summaries with summary text and creation date,
    ordered by creation date (newest first).
    
    **Query Parameters:**
    - `limit`: Maximum number of summaries to return (default: 10, max: 50)
    
    **Example Response:**
    ```json
    [
        {
            "summary": "Based on your responses, you have Type 2 diabetes with good glucose control...",
            "date": "2025-07-15T14:30:00Z"
        },
        {
            "summary": "Initial assessment shows mild hypertension and dietary concerns...",
            "date": "2025-07-10T09:15:00Z"
        }
    ]
    ```
    """
    try:
        # Validate limit parameter
        if limit < 1 or limit > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 50"
            )
            
        summaries = get_qa_summaries_by_user_id(
            db=db,
            user_id=current_user.id,
            limit=limit
        )
        
        return summaries
        
    except QASummaryServiceError as e:
        logger.error(f"QA summary service error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving QA summaries: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving QA summaries for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving QA summaries"
        )

@router.get("/user/{user_id}/latest", response_model=Optional[QASummaryResponse])
async def get_user_latest_qa_summary(
    user_id: int = Path(..., description="User ID to get QA summary for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the latest QA summary for a specific user (admin access).
    
    This endpoint allows retrieving the latest QA summary for any user.
    Typically used by healthcare providers or admin users.
    
    **Path Parameters:**
    - `user_id`: ID of the user whose QA summary to retrieve
    
    **Example Response:**
    ```json
    {
        "summary": "Based on your responses, you have Type 2 diabetes with good glucose control...",
        "date": "2025-07-15T14:30:00Z"
    }
    ```
    
    **Example Response (when no summary exists):**
    ```json
    null
    ```
    """
    try:
        # Note: In a production environment, you might want to add role-based access control
        # to ensure only authorized users (like healthcare providers) can access other users' data
        
        summary = get_latest_qa_summary_by_user_id(
            db=db,
            user_id=user_id
        )
        
        return summary
        
    except QASummaryServiceError as e:
        logger.error(f"QA summary service error for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving QA summary: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving QA summary for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the QA summary"
        )