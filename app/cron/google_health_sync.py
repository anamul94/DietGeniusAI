#!/usr/bin/env python3
"""
Cron job script to sync Google Health data daily.
This script should be scheduled to run at 12 AM every day.

Example crontab entry:
0 0 * * * /path/to/python /path/to/app/cron/google_health_sync.py
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import logging

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.base import SessionLocal
from app.models.google_health import GoogleHealthToken
from app.services.google_health import fetch_google_health_data, GoogleHealthServiceError
from app.core.logging import logger

# Configure logging for cron job
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/var/log/google_health_sync.log"),
        logging.StreamHandler()
    ]
)

async def sync_user_health_data(db: Session, user_id: int):
    """
    Sync health data for a specific user.
    
    Args:
        db: Database session
        user_id: User ID
    """
    try:
        # Calculate time range (last 24 hours)
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=24)
        
        # Define data types to fetch
        data_types = ["steps", "heart_rate", "sleep", "weight", "nutrition"]
        
        # Fetch data from Google Health API
        data = await fetch_google_health_data(
            db=db,
            user_id=user_id,
            data_types=data_types,
            start_time=start_time,
            end_time=end_time
        )
        
        logger.info(f"Synced {len(data)} health data points for user {user_id}")
        return data
    except GoogleHealthServiceError as e:
        logger.error(f"Error syncing health data for user {user_id}: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error syncing health data for user {user_id}: {str(e)}")
        return []

async def sync_all_users_health_data():
    """
    Sync health data for all users with Google Health tokens.
    """
    db = SessionLocal()
    try:
        # Get all users with Google Health tokens
        tokens = db.query(GoogleHealthToken).all()
        
        if not tokens:
            logger.info("No users with Google Health tokens found")
            return
        
        logger.info(f"Starting sync for {len(tokens)} users")
        
        # Sync data for each user
        for token in tokens:
            await sync_user_health_data(db, token.user_id)
        
        logger.info("Google Health sync completed successfully")
    except Exception as e:
        logger.error(f"Error in sync_all_users_health_data: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting Google Health sync cron job")
    asyncio.run(sync_all_users_health_data())