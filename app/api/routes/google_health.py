from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.logging import logger
from app.core.rate_limiter import rate_limit_auth
from app.models.user import User
from app.models.google_health import GoogleHealthToken as GoogleHealthTokenModel
from app.services.google_health import (
    exchange_code_for_token,
    fetch_google_health_data,
    get_user_health_data,
    GoogleHealthServiceError
)
from app.schemas.google_health import (
    GoogleHealthToken,
    GoogleHealthData,
    GoogleHealthDataList,
    GoogleHealthAuthRequest,
    GoogleHealthDataRequest
)

router = APIRouter()

@router.get("/auth-url",
    summary="Get Google Health Authorization URL",
    description="Returns the URL that the user should be redirected to in order to authorize the application to access their Google Health data.",
    response_description="Authorization URL for Google Health API"
)
async def get_google_health_auth_url(request: Request):
    """
    Get the Google Health authorization URL.
    """
    try:
        # Build the authorization URL
        auth_url = (
            "https://accounts.google.com/o/oauth2/auth"
            f"?client_id={settings.GOOGLE_HEALTH_CLIENT_ID}"
            f"&redirect_uri={settings.GOOGLE_HEALTH_REDIRECT_URI}"
            f"&scope={settings.GOOGLE_HEALTH_SCOPES}"
            "&access_type=offline"
            "&response_type=code"
            "&prompt=consent"
        )
        
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Error generating Google Health auth URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating Google Health auth URL: {str(e)}"
        )

@router.post("/auth/callback",
    response_model=GoogleHealthToken,
    summary="Handle Google Health Authorization Callback",
    description="Exchanges the authorization code for access and refresh tokens. This endpoint should be called after the user has authorized the application.",
    response_description="Google Health token information"
)
async def google_health_auth_callback(
    auth_request: GoogleHealthAuthRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Handle Google Health authorization callback.
    """
    try:
        # Exchange code for token
        token = await exchange_code_for_token(
            db=db,
            user_id=current_user.id,
            code=auth_request.code,
            redirect_uri=auth_request.redirect_uri
        )
        
        return token
    except GoogleHealthServiceError as e:
        logger.error(f"Google Health auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google Health auth error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in Google Health auth callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

@router.post("/data/fetch",
    response_model=GoogleHealthDataList,
    summary="Fetch Health Data from Google Health API",
    description="Fetches health data from Google Health API for the specified data types and time range. The data is saved to the database and returned in the response.",
    response_description="List of health data fetched from Google Health API"
)
async def fetch_health_data(
    data_request: GoogleHealthDataRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(rate_limit_auth)
):
    """
    Fetch health data from Google Health API.
    """
    try:
        # Fetch data from Google Health API
        data = await fetch_google_health_data(
            db=db,
            user_id=current_user.id,
            data_types=data_request.data_types,
            start_time=data_request.start_date,
            end_time=data_request.end_date
        )
        
        return {"items": data, "total": len(data)}
    except GoogleHealthServiceError as e:
        logger.error(f"Google Health data fetch error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google Health data fetch error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in fetch_health_data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

@router.get("/data",
    response_model=GoogleHealthDataList,
    summary="Get Health Data from Database",
    description="Retrieves health data from the database for the specified data type and time range. This endpoint returns data that has already been fetched and stored.",
    response_description="List of health data from the database"
)
async def get_health_data(
    data_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(rate_limit_auth)
):
    """
    Get health data from the database.
    """
    try:
        # Get data from database
        data = await get_user_health_data(
            db=db,
            user_id=current_user.id,
            data_type=data_type,
            start_time=start_date,
            end_time=end_date
        )
        
        return {"items": data, "total": len(data)}
    except Exception as e:
        logger.error(f"Error getting health data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting health data: {str(e)}"
        )

@router.get("/status",
    summary="Check Google Health Connection Status",
    description="Checks if the user has connected their Google Health account and returns the connection status along with token expiration information.",
    response_description="Connection status and token expiration"
)
async def get_google_health_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if the user has connected their Google Health account.
    """
    try:
        # Check if user has a token
        token = db.query(GoogleHealthTokenModel).filter(
            GoogleHealthTokenModel.user_id == current_user.id
        ).first()
        
        return {
            "connected": token is not None,
            "expires_at": token.expires_at if token else None
        }
    except Exception as e:
        logger.error(f"Error checking Google Health status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking Google Health status: {str(e)}"
        )