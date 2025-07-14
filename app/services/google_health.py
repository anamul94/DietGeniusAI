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
        
        # Log request details for debugging
        logger.info(f"Token exchange request - Code: {code[:10]}... (truncated)")
        logger.info(f"Token exchange request - Redirect URI: {redirect_uri}")
        logger.info(f"Token exchange request - Client ID: {settings.GOOGLE_HEALTH_CLIENT_ID[:10]}... (truncated)")
        
        # Make token request
        response = requests.post(token_url, data=payload)
        
        # Log response for debugging
        if response.status_code != 200:
            logger.error(f"Token exchange failed with status {response.status_code}")
            logger.error(f"Response content: {response.text}")
        
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

async def revoke_access_token(db: Session, token: GoogleHealthToken) -> bool:
    """
    Revoke the access token and remove it from the database.
    
    Args:
        db: Database session
        token: GoogleHealthToken object
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Prepare revoke token request
        revoke_url = "https://oauth2.googleapis.com/revoke"
        payload = {
            "token": token.access_token
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Make revoke token request
        response = requests.post(revoke_url, data=payload, headers=headers)
        
        # Log response for debugging
        if response.status_code != 200:
            logger.error(f"Token revocation failed with status {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return False
        
        # Delete token from database
        db.delete(token)
        db.commit()
        
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error revoking token: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in revoke_access_token: {str(e)}")
        return False

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
            try:
                # Check if token has required scope for this data type
                if not check_required_scope(data_type, token.scope):
                    logger.error(f"Missing required scope for data type {data_type}. Token scopes: {token.scope}")
                    continue
                    
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
                
                # Log request details
                logger.info(f"Fetching data for type: {data_type}")
                logger.info(f"Request URL: {url}")
                logger.info(f"Request payload: {payload}")
                logger.info(f"Request headers: Authorization: Bearer [TOKEN_HIDDEN], Content-Type: {headers['Content-Type']}")
                
                # Make request to Google Fitness API
                response = requests.post(url, headers=headers, json=payload)
                
                # Log response for debugging
                if response.status_code != 200:
                    logger.error(f"Google Fitness API error for {data_type}: Status {response.status_code}")
                    logger.error(f"Response content: {response.text}")
                    logger.error(f"Scopes in token: {token.scope}")
                    
                    # For nutrition data, this might be expected if no data is available
                    if data_type == "nutrition" and response.status_code == 404:
                        logger.warning(f"No nutrition data available for the specified time range")
                        continue
                    else:
                        # For other data types, continue to next data type instead of failing completely
                        logger.warning(f"Skipping {data_type} due to API error")
                        continue
                
                response.raise_for_status()
                response_data = response.json()
                
                # Process response data
                processed_data = process_response_data(response_data, data_type, user_id)
                
                # Save data to database (avoiding duplicates)
                saved_data = save_health_data(db, processed_data)
                all_data.extend(saved_data)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching {data_type} data: {str(e)}")
                # Continue with other data types instead of failing completely
                continue
            except Exception as e:
                logger.error(f"Unexpected error processing {data_type}: {str(e)}")
                # Continue with other data types instead of failing completely
                continue
        
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
        "nutrition": "com.google.calories.expended"  # Use calories as a proxy for nutrition data
    }
    return mapping.get(data_type)

def check_required_scope(data_type: str, token_scope: str) -> bool:
    """
    Check if the token has the required scope for the data type.
    
    Args:
        data_type: The type of data to check
        token_scope: The scope string from the token
        
    Returns:
        bool: True if the required scope is present, False otherwise
    """
    scope_mapping = {
        "steps": "https://www.googleapis.com/auth/fitness.activity.read",
        "heart_rate": "https://www.googleapis.com/auth/fitness.heart_rate.read",
        "sleep": "https://www.googleapis.com/auth/fitness.sleep.read",
        "weight": "https://www.googleapis.com/auth/fitness.body.read",
        "nutrition": "https://www.googleapis.com/auth/fitness.nutrition.read"
    }
    
    required_scope = scope_mapping.get(data_type)
    if not required_scope:
        return False
        
    return required_scope in token_scope

def build_data_request(
    data_type: str,
    data_source: str,
    start_time_millis: int,
    end_time_millis: int
) -> tuple:
    """Build the request URL and payload for the specific data type."""
    base_url = settings.GOOGLE_HEALTH_API_URL
    
    # Log the base URL for debugging
    logger.info(f"Google Health API base URL: {base_url}")
    
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
        
        # For steps, add additional fields required by the API
        if data_type == "steps":
            payload["aggregateBy"][0]["dataSourceId"] = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
    elif data_type == "sleep":
        # For sleep data, use the dataset:aggregate endpoint instead of sessions
        # The sessions endpoint is returning 404 Not Found
        url = f"{base_url}/users/me/dataset:aggregate"
        payload = {
            "aggregateBy": [{
                "dataTypeName": data_source
            }],
            "bucketByTime": {"durationMillis": 86400000},  # 1 day
            "startTimeMillis": start_time_millis,
            "endTimeMillis": end_time_millis
        }
    elif data_type == "nutrition":
        # For nutrition data, use the dataset:aggregate endpoint like other data types
        # Nutrition data should be aggregated, not fetched from a specific data source
        url = f"{base_url}/users/me/dataset:aggregate"
        payload = {
            "aggregateBy": [{
                "dataTypeName": data_source
            }],
            "bucketByTime": {"durationMillis": 86400000},  # 1 day
            "startTimeMillis": start_time_millis,
            "endTimeMillis": end_time_millis
        }
    else:
        raise GoogleHealthServiceError(f"Unsupported data type: {data_type}")
    
    # Log the constructed URL and payload
    logger.info(f"Built URL for {data_type}: {url}")
    logger.info(f"Built payload for {data_type}: {payload}")
    
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
        # Process sleep data from dataset:aggregate endpoint
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
                                
                                value = {
                                    "sleep_duration_minutes": (end_time - start_time).total_seconds() / 60
                                }
                                
                                # Extract sleep stage if available
                                if "value" in point:
                                    for val in point["value"]:
                                        if "intVal" in val:
                                            # Sleep stage values:
                                            # 1: Awake (during sleep)
                                            # 2: Sleep
                                            # 3: Out-of-bed
                                            # 4: Light sleep
                                            # 5: Deep sleep
                                            # 6: REM sleep
                                            sleep_stage_map = {
                                                1: "Awake",
                                                2: "Sleep",
                                                3: "Out-of-bed",
                                                4: "Light sleep",
                                                5: "Deep sleep",
                                                6: "REM sleep"
                                            }
                                            sleep_stage = val.get("intVal", 0)
                                            value["sleep_stage"] = sleep_stage
                                            value["sleep_stage_name"] = sleep_stage_map.get(sleep_stage, "Unknown")
                                
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
        # Process nutrition data (calories expended) from aggregate endpoint
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
                                        if "fpVal" in val:
                                            # Handle calories expended as float value
                                            value["calories_expended"] = val["fpVal"]
                                        elif "intVal" in val:
                                            # Handle calories expended as integer value
                                            value["calories_expended"] = val["intVal"]
                                
                                # Only add data if we have actual values
                                if value:
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

async def list_available_data_sources(
    db: Session,
    user_id: int
) -> List[Dict[str, Any]]:
    """
    List available data sources from Google Fitness API for debugging.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List[Dict[str, Any]]: List of available data sources
    """
    try:
        # Get valid token
        token = await get_valid_token(db, user_id)
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json"
        }
        
        # Request available data sources
        base_url = settings.GOOGLE_HEALTH_API_URL
        url = f"{base_url}/users/me/dataSources"
        
        logger.info(f"Fetching available data sources from: {url}")
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Error fetching data sources: Status {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return []
        
        response_data = response.json()
        
        # Extract data source information
        data_sources = []
        if "dataSource" in response_data:
            for source in response_data["dataSource"]:
                data_sources.append({
                    "dataStreamId": source.get("dataStreamId", ""),
                    "dataType": source.get("dataType", {}).get("name", ""),
                    "name": source.get("name", ""),
                    "type": source.get("type", ""),
                    "application": source.get("application", {}).get("name", "")
                })
        
        logger.info(f"Found {len(data_sources)} data sources")
        for source in data_sources:
            logger.info(f"Data source: {source}")
        
        return data_sources
        
    except Exception as e:
        logger.error(f"Error listing data sources: {str(e)}")
        return []