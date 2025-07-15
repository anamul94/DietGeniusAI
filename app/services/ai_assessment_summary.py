from typing import List, Optional
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.logging import logger
from app.models.ai_assessment_summary import AIAssessmentSummary
from app.schemas.ai_assessment_summary import (
    AIAssessmentSummaryCreate,
    AIAssessmentSummaryUpdate
)


class AIAssessmentSummaryServiceError(Exception):
    """Custom exception for AI assessment summary service errors"""
    pass


def create_or_update_ai_assessment_summary(
    db: Session,
    user_id: int,
    target_date: date,
    summary: str
) -> AIAssessmentSummary:
    """
    Create or update an AI assessment summary for a user and date.
    Ensures only one summary per user per date.
    
    Args:
        db: Database session
        user_id: User ID
        target_date: Date for the summary
        summary: AI-generated summary in markdown format
        
    Returns:
        AIAssessmentSummary: Created or updated summary record
        
    Raises:
        AIAssessmentSummaryServiceError: If an error occurs
    """
    try:
        # Check if a summary already exists for this user and date
        existing_summary = db.query(AIAssessmentSummary).filter(
            and_(
                AIAssessmentSummary.user_id == user_id,
                AIAssessmentSummary.date_value == target_date
            )
        ).first()
        
        if existing_summary:
            # Update existing record
            logger.info(f"Updating existing AI assessment summary for user {user_id} on {target_date}")
            existing_summary.summary = summary
            existing_summary.updated_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(existing_summary)
            return existing_summary
            
        else:
            # Create new record
            logger.info(f"Creating new AI assessment summary for user {user_id} on {target_date}")
            summary_create = AIAssessmentSummaryCreate(
                user_id=user_id,
                date_value=target_date,
                summary=summary
            )
            
            db_summary = AIAssessmentSummary(**summary_create.model_dump())
            db.add(db_summary)
            db.commit()
            db.refresh(db_summary)
            return db_summary
            
    except Exception as e:
        logger.error(f"Error creating/updating AI assessment summary: {str(e)}")
        db.rollback()
        raise AIAssessmentSummaryServiceError(f"Error creating/updating AI assessment summary: {str(e)}")


def get_ai_assessment_summary_by_date(
    db: Session,
    user_id: int,
    user_name: str,
    target_date: date
) -> Optional[AIAssessmentSummary]:
    """
    Get AI assessment summary for a specific user and date
    
    Args:
        db: Database session
        user_id: User ID
        target_date: Target date
        
    Returns:
        AIAssessmentSummary: Summary record if found, None otherwise
    """
    try:
        return db.query(AIAssessmentSummary).filter(
            and_(
                AIAssessmentSummary.user_id == user_id,
                AIAssessmentSummary.date_value == target_date
            )
        ).first()
        
    except Exception as e:
        logger.error(f"Error getting AI assessment summary by date: {str(e)}")
        raise AIAssessmentSummaryServiceError(f"Error getting AI assessment summary by date: {str(e)}")


def get_ai_assessment_summaries_by_date_range(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date
) -> List[AIAssessmentSummary]:
    """
    Get AI assessment summaries for a user within a date range
    
    Args:
        db: Database session
        user_id: User ID
        start_date: Start date of the range
        end_date: End date of the range
        
    Returns:
        List[AIAssessmentSummary]: List of summary records
    """
    try:
        return db.query(AIAssessmentSummary).filter(
            and_(
                AIAssessmentSummary.user_id == user_id,
                AIAssessmentSummary.date_value >= start_date,
                AIAssessmentSummary.date_value <= end_date
            )
        ).order_by(AIAssessmentSummary.date_value.desc()).all()
        
    except Exception as e:
        logger.error(f"Error getting AI assessment summaries by date range: {str(e)}")
        raise AIAssessmentSummaryServiceError(f"Error getting AI assessment summaries by date range: {str(e)}")


def get_today_ai_assessment_summary(
    db: Session,
    user_id: int
) -> Optional[AIAssessmentSummary]:
    """
    Get today's AI assessment summary for a user
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        AIAssessmentSummary: Today's summary record if found, None otherwise
    """
    today = datetime.now().date()
    return get_ai_assessment_summary_by_date(db, user_id, today)