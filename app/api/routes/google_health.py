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
    revoke_access_token,
    list_available_data_sources,
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
        # Log the client ID and redirect URI for debugging
        logger.info(f"Using client ID: {settings.GOOGLE_HEALTH_CLIENT_ID[:10]}... (truncated)")
        logger.info(f"Using redirect URI: {settings.GOOGLE_HEALTH_REDIRECT_URI}")
        logger.info(f"Using scopes: {settings.GOOGLE_HEALTH_SCOPES}")
        
        # Build the authorization URL
        auth_url = (
            "https://accounts.google.com/o/oauth2/auth"
            f"?client_id={settings.GOOGLE_HEALTH_CLIENT_ID}"
            f"&redirect_uri={settings.GOOGLE_HEALTH_REDIRECT_URI}"
            f"&scope={settings.GOOGLE_HEALTH_SCOPES}"
            "&access_type=offline"
            "&response_type=code"
            "&prompt=consent"
            "&include_granted_scopes=true"  # Include previously granted scopes
        )
        
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Error generating Google Health auth URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating Google Health auth URL: {str(e)}"
        )

@router.get("/auth/callback",
    summary="Handle Google Health Authorization Callback (GET)",
    description="Handles the redirect from Google OAuth. This endpoint receives the authorization code as a query parameter and redirects to the frontend with the code.",
    response_description="Redirect to frontend with code"
)
async def google_health_auth_callback_get(
    code: str,
    state: Optional[str] = None,
    error: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Handle Google Health authorization callback via GET request.
    This endpoint is called by Google OAuth after user authorization.
    """
    from fastapi.responses import RedirectResponse
    
    try:
        # Log the full request URL and details
        logger.info(f"Google OAuth callback received - Full URL: {request.url}")
        logger.info(f"Google OAuth callback - Code: {code[:10]}... (truncated)")
        logger.info(f"Google OAuth callback - State: {state}")
        logger.info(f"Google OAuth callback - Configured redirect URI: {settings.GOOGLE_HEALTH_REDIRECT_URI}")
        
        if error:
            logger.error(f"Google OAuth error: {error}")
            # Redirect to frontend with error
            error_url = f"{settings.FRONTEND_URL}/google-health/callback?error={error}"
            return RedirectResponse(url=error_url)
        
        if not code:
            logger.error("No authorization code provided")
            error_url = f"{settings.FRONTEND_URL}/google-health/callback?error=no_code"
            return RedirectResponse(url=error_url)
        
        # Store the code in a temporary session or cache with a short expiration
        # This is a critical step to prevent the "invalid_grant" error
        # In a real implementation, you would use Redis or a similar cache
        # For now, we'll just log a warning
        logger.warning("IMPORTANT: Authorization codes are one-time use only. If you're testing repeatedly, you need to start the OAuth flow from the beginning each time.")
        
        # Build the frontend callback URL with the code
        frontend_callback_url = f"{settings.FRONTEND_URL}/google-health/callback?code={code}"
        if state:
            frontend_callback_url += f"&state={state}"
        
        # Perform an actual HTTP redirect to the frontend
        logger.info(f"Redirecting to frontend: {frontend_callback_url}")
        return RedirectResponse(url=frontend_callback_url)
        
    except Exception as e:
        logger.error(f"Unexpected error in Google Health auth callback (GET): {str(e)}")
        return {"error": "server_error", "message": f"Unexpected error: {str(e)}"}

@router.post("/auth/callback",
    response_model=GoogleHealthToken,
    summary="Handle Google Health Authorization Callback (POST)",
    description="Exchanges the authorization code for access and refresh tokens. This endpoint should be called by the frontend after receiving the code from the GET callback.",
    response_description="Google Health token information"
)
async def google_health_auth_callback_post(
    auth_request: GoogleHealthAuthRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Handle Google Health authorization callback via POST request.
    This endpoint is called by the frontend after receiving the code.
    """
    try:
        # Log received data for debugging
        logger.info(f"Received auth request - Code: {auth_request.code[:10]}... (truncated)")
        logger.info(f"Received auth request - Redirect URI: {auth_request.redirect_uri}")
        
        # IMPORTANT: Use the same redirect URI that was used in the authorization request
        # This should match the one registered in Google Cloud Console
        redirect_uri = settings.GOOGLE_HEALTH_REDIRECT_URI
        logger.info(f"Using redirect URI from settings: {redirect_uri}")
        
        # Exchange code for token
        token = await exchange_code_for_token(
            db=db,
            user_id=current_user.id,
            code=auth_request.code,
            redirect_uri=redirect_uri  # Use the URI from settings instead of the request
        )
        
        return token
    except GoogleHealthServiceError as e:
        logger.error(f"Google Health auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google Health auth error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in Google Health auth callback (POST): {str(e)}")
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
        
        result = {
            "connected": token is not None,
            "expires_at": token.expires_at if token else None
        }
        
        # Add scopes information if token exists
        if token:
            result["scopes"] = token.scope.split()
            
        return result
    except Exception as e:
        logger.error(f"Error checking Google Health status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking Google Health status: {str(e)}"
        )

@router.post("/revoke",
    summary="Revoke Google Health Access",
    description="Revokes the Google Health access token and removes it from the database.",
    response_description="Revocation status"
)
async def revoke_google_health_access(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revoke Google Health access for the current user.
    """
    try:
        # Get token for user
        token = db.query(GoogleHealthTokenModel).filter(
            GoogleHealthTokenModel.user_id == current_user.id
        ).first()
        
        if not token:
            return {"success": True, "message": "No Google Health connection found"}
        
        # Revoke token
        success = await revoke_access_token(db, token)
        
        if success:
            return {"success": True, "message": "Google Health access successfully revoked"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke Google Health access"
            )
    except Exception as e:
        logger.error(f"Error revoking Google Health access: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error revoking Google Health access: {str(e)}"
        )

@router.get("/data-sources",
    summary="List Available Data Sources",
    description="Lists all available data sources from Google Fitness API for debugging and development purposes.",
    response_description="List of available data sources"
)
async def list_data_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List available data sources from Google Fitness API.
    """
    try:
        data_sources = await list_available_data_sources(db, current_user.id)
        return {"data_sources": data_sources, "total": len(data_sources)}
    except Exception as e:
        logger.error(f"Error listing data sources: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing data sources: {str(e)}"
        )

@router.post("/data/fetch-and-save",
    response_model=GoogleHealthDataList,
    summary="Fetch and Save Health Data from Google Health API",
    description="Fetches health data from Google Health API for the specified data types and time range. Checks if the service exists before saving data to the database to avoid duplicates.",
    response_description="List of health data fetched and saved from Google Health API"
)
async def fetch_and_save_health_data(
    data_request: GoogleHealthDataRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _: None = Depends(rate_limit_auth)
):
    """
    Fetch health data from Google Health API and save it to the database.
    First checks if the service exists before saving to avoid duplicates.
    """
    try:
        # First check if the user has a valid Google Health token
        token = db.query(GoogleHealthTokenModel).filter(
            GoogleHealthTokenModel.user_id == current_user.id
        ).first()
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Google Health connection found for this user"
            )
            
        # Fetch data from Google Health API
        data = await fetch_google_health_data(
            db=db,
            user_id=current_user.id,
            data_types=data_request.data_types,
            start_time=data_request.start_date,
            end_time=data_request.end_date
        )
        
        # Note: The fetch_google_health_data function already handles duplicate data
        # by checking if data exists before saving in the save_health_data function
        
        return {"items": data, "total": len(data)}
    except GoogleHealthServiceError as e:
        logger.error(f"Google Health data fetch-and-save error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google Health data fetch-and-save error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in fetch_and_save_health_data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )