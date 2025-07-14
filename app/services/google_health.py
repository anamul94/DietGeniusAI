import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.logging import logger
from app.models.google_health import GoogleHealthToken, GoogleHealthData
from app.schemas.google_health import (
    GoogleHealthTokenCreate,
    GoogleHealthDataCreate,
    GoogleHealthAuthResponse
)

class GoogleHealthServiceError(Exception):
    """Exception raised for errors in the Google Health service."""
    pass

async def exchange_code_for_token(
    db: Session,
    user_id: int,
    code: str,
    redirect_uri: str
) -> GoogleHealthToken:
    """
    Exchange authorization code for access and refresh tokens.
    
    Args:
        db: Database session
        user_id: User ID
        code: Authorization code from Google
        redirect_uri: Redirect URI used in the authorization request
        
    Returns:
        GoogleHealthToken: The created token object
    """
    try:
        # Prepare token request
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": settings.GOOGLE_HEALTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_HEALTH_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        # Make token request
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        token_data = response.json()
        
        # Calculate token expiration
        expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        
        # Create token object
        token_create = GoogleHealthTokenCreate(
            user_id=user_id,
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"],
            expires_at=expires_at,
            scope=token_data["scope"]
        )
        
        # Check if token already exists for user
        existing_token = db.query(GoogleHealthToken).filter(
            GoogleHealthToken.user_id == user_id
        ).first()
        
        if existing_token:
            # Update existing token
            existing_token.access_token = token_create.access_token
            existing_token.refresh_token = token_create.refresh_token
            existing_token.token_type = token_create.token_type
            existing_token.expires_at = token_create.expires_at
            existing_token.scope = token_create.scope
            existing_token.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing_token)
            return existing_token
        else:
            # Create new token
            db_token = GoogleHealthToken(**token_create.model_dump())
            db.add(db_token)
            db.commit()
            db.refresh(db_token)
            return db_token
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error exchanging code for token: {str(e)}")
        raise GoogleHealthServiceError(f"Error exchanging code for token: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in exchange_code_for_token: {str(e)}")
        raise GoogleHealthServiceError(f"Unexpected error: {str(e)}")

async def refresh_access_token(db: Session, token: GoogleHealthToken) -> GoogleHealthToken:
    """
    Refresh the access token using the refresh token.
    
    Args:
        db: Database session
        token: GoogleHealthToken object
        
    Returns:
        GoogleHealthToken: The updated token object
    """
    try:
        # Prepare refresh token request
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": settings.GOOGLE_HEALTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_HEALTH_CLIENT_SECRET,
            "refresh_token": token.refresh_token,
            "grant_type": "refresh_token"
        }
        
        # Make refresh token request
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        token_data = response.json()
        
        # Calculate token expiration
        expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        
        # Update token
        token.access_token = token_data["access_token"]
        token.token_type = token_data["token_type"]
        token.expires_at = expires_at
        if "refresh_token" in token_data:
            token.refresh_token = token_data["refresh_token"]
        token.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(token)
        return token
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise GoogleHealthServiceError(f"Error refreshing token: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in refresh_access_token: {str(e)}")
        raise GoogleHealthServiceError(f"Unexpected error: {str(e)}")

async def get_valid_token(db: Session, user_id: int) -> GoogleHealthToken:
    """
    Get a valid token for the user, refreshing if necessary.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        GoogleHealthToken: A valid token object
    """
    # Get token for user
    token = db.query(GoogleHealthToken).filter(
        GoogleHealthToken.user_id == user_id
    ).first()
    
    if not token:
        raise GoogleHealthServiceError("No Google Health token found for user")
    
    # Check if token is expired or about to expire (within 5 minutes)
    if token.expires_at <= datetime.now(timezone.utc) + timedelta(minutes=5):
        # Refresh token
        token = await refresh_access_token(db, token)
    
    return token

async def fetch_google_health_data(
    db: Session,
    user_id: int,
    data_types: List[str],
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[GoogleHealthData]:
    """
    Fetch health data from Google Health API.
    
    Args:
        db: Database session
        user_id: User ID
        data_types: List of data types to fetch
        start_time: Start time for data retrieval (defaults to 24 hours ago)
        end_time: End time for data retrieval (defaults to current time)
        
    Returns:
        List[GoogleHealthData]: List of health data objects
    """
    try:
        # Set default time range if not provided
        if not end_time:
            end_time = datetime.now(timezone.utc)
        if not start_time:
            start_time = end_time - timedelta(hours=24)
        
        # Get valid token
        token = await get_valid_token(db, user_id)
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json"
        }
        
        all_data = []
        
        # Process each data type
        for data_type in data_types:
            # Map data type to Google Fitness data source
            data_source = map_data_type_to_source(data_type)
            if not data_source:
                logger.warning(f"Unsupported data type: {data_type}")
                continue
            
            # Prepare request parameters
            start_time_millis = int(start_time.timestamp() * 1000)
            end_time_millis = int(end_time.timestamp() * 1000)
            
            # Build request URL and payload based on data type
            url, payload = build_data_request(data_type, data_source, start_time_millis, end_time_millis)
            
            # Make request to Google Fitness API
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            
            # Process response data
            processed_data = process_response_data(response_data, data_type, user_id)
            
            # Save data to database (avoiding duplicates)
            saved_data = save_health_data(db, processed_data)
            all_data.extend(saved_data)
        
        return all_data
        
    except GoogleHealthServiceError as e:
        # Re-raise service errors
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching health data: {str(e)}")
        raise GoogleHealthServiceError(f"Error fetching health data: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in fetch_google_health_data: {str(e)}")
        raise GoogleHealthServiceError(f"Unexpected error: {str(e)}")

def map_data_type_to_source(data_type: str) -> str:
    """Map data type to Google Fitness data source."""
    mapping = {
        "steps": "com.google.step_count.delta",
        "heart_rate": "com.google.heart_rate.bpm",
        "sleep": "com.google.sleep.segment",
        "weight": "com.google.weight",
        "nutrition": "com.google.nutrition"
    }
    return mapping.get(data_type)

def build_data_request(
    data_type: str, 
    data_source: str, 
    start_time_millis: int, 
    end_time_millis: int
) -> tuple:
    """Build the request URL and payload for the specific data type."""
    base_url = settings.GOOGLE_HEALTH_API_URL
    
    if data_type in ["steps", "heart_rate", "weight"]:
        url = f"{base_url}/users/me/dataset:aggregate"
        payload = {
            "aggregateBy": [{
                "dataTypeName": data_source
            }],
            "bucketByTime": {"durationMillis": 86400000},  # 1 day
            "startTimeMillis": start_time_millis,
            "endTimeMillis": end_time_millis
        }
    elif data_type == "sleep":
        url = f"{base_url}/users/me/sessions"
        payload = {
            "startTime": start_time_millis,
            "endTime": end_time_millis,
            "activityType": "72"  # Sleep activity type
        }
    elif data_type == "nutrition":
        url = f"{base_url}/users/me/dataSources/{data_source}/datasets/{start_time_millis}-{end_time_millis}"
        payload = {}
    else:
        raise GoogleHealthServiceError(f"Unsupported data type: {data_type}")
    
    return url, payload

def process_response_data(
    response_data: Dict[str, Any], 
    data_type: str, 
    user_id: int
) -> List[GoogleHealthDataCreate]:
    """Process response data from Google Fitness API."""
    processed_data = []
    
    if data_type in ["steps", "heart_rate", "weight"]:
        # Process aggregate data
        if "bucket" in response_data:
            for bucket in response_data["bucket"]:
                if "dataset" in bucket:
                    for dataset in bucket["dataset"]:
                        if "point" in dataset:
                            for point in dataset["point"]:
                                start_time = datetime.fromtimestamp(
                                    int(point["startTimeNanos"]) / 1_000_000_000,
                                    tz=timezone.utc
                                )
                                end_time = datetime.fromtimestamp(
                                    int(point["endTimeNanos"]) / 1_000_000_000,
                                    tz=timezone.utc
                                )
                                
                                value = {}
                                if "value" in point:
                                    for val in point["value"]:
                                        if data_type == "steps":
                                            value["steps"] = val.get("intVal", 0)
                                        elif data_type == "heart_rate":
                                            value["bpm"] = val.get("fpVal", 0)
                                        elif data_type == "weight":
                                            value["weight_kg"] = val.get("fpVal", 0)
                                
                                processed_data.append(
                                    GoogleHealthDataCreate(
                                        user_id=user_id,
                                        data_type=data_type,
                                        start_time=start_time,
                                        end_time=end_time,
                                        value=value,
                                        source="Google Fit"
                                    )
                                )
    elif data_type == "sleep":
        # Process sleep data
        if "session" in response_data:
            for session in response_data["session"]:
                start_time = datetime.fromtimestamp(
                    int(session["startTimeMillis"]) / 1000,
                    tz=timezone.utc
                )
                end_time = datetime.fromtimestamp(
                    int(session["endTimeMillis"]) / 1000,
                    tz=timezone.utc
                )
                
                value = {
                    "sleep_duration_minutes": (end_time - start_time).total_seconds() / 60,
                    "sleep_type": session.get("name", "Unknown")
                }
                
                processed_data.append(
                    GoogleHealthDataCreate(
                        user_id=user_id,
                        data_type=data_type,
                        start_time=start_time,
                        end_time=end_time,
                        value=value,
                        source="Google Fit"
                    )
                )
    elif data_type == "nutrition":
        # Process nutrition data
        if "point" in response_data:
            for point in response_data["point"]:
                start_time = datetime.fromtimestamp(
                    int(point["startTimeNanos"]) / 1_000_000_000,
                    tz=timezone.utc
                )
                end_time = datetime.fromtimestamp(
                    int(point["endTimeNanos"]) / 1_000_000_000,
                    tz=timezone.utc
                )
                
                value = {}
                if "value" in point:
                    for val in point["value"]:
                        if "mapVal" in val:
                            for map_val in val["mapVal"]:
                                value[map_val["key"]] = map_val["value"]["fpVal"]
                
                processed_data.append(
                    GoogleHealthDataCreate(
                        user_id=user_id,
                        data_type=data_type,
                        start_time=start_time,
                        end_time=end_time,
                        value=value,
                        source="Google Fit"
                    )
                )
    
    return processed_data

def save_health_data(
    db: Session, 
    data_list: List[GoogleHealthDataCreate]
) -> List[GoogleHealthData]:
    """
    Save health data to database, avoiding duplicates.
    
    Args:
        db: Database session
        data_list: List of health data to save
        
    Returns:
        List[GoogleHealthData]: List of saved health data objects
    """
    saved_data = []
    
    for data in data_list:
        # Check if data already exists
        existing_data = db.query(GoogleHealthData).filter(
            and_(
                GoogleHealthData.user_id == data.user_id,
                GoogleHealthData.data_type == data.data_type,
                GoogleHealthData.start_time == data.start_time,
                GoogleHealthData.end_time == data.end_time
            )
        ).first()
        
        if not existing_data:
            # Create new data entry
            db_data = GoogleHealthData(**data.model_dump())
            db.add(db_data)
            db.commit()
            db.refresh(db_data)
            saved_data.append(db_data)
    
    return saved_data

async def get_user_health_data(
    db: Session,
    user_id: int,
    data_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[GoogleHealthData]:
    """
    Get health data for a user from the database.
    
    Args:
        db: Database session
        user_id: User ID
        data_type: Data type to filter by
        start_time: Start time to filter by
        end_time: End time to filter by
        
    Returns:
        List[GoogleHealthData]: List of health data objects
    """
    query = db.query(GoogleHealthData).filter(GoogleHealthData.user_id == user_id)
    
    if data_type:
        query = query.filter(GoogleHealthData.data_type == data_type)
    
    if start_time:
        query = query.filter(GoogleHealthData.start_time >= start_time)
    
    if end_time:
        query = query.filter(GoogleHealthData.end_time <= end_time)
    
    return query.order_by(GoogleHealthData.start_time.desc()).all()