from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status

from app.models.qa_session_summary import QASessionSummary
from app.core.logging import logger

class QASummaryServiceError(Exception):
    """Custom exception for QA summary service errors"""
    pass

def get_latest_qa_summary_by_user_id(
    db: Session,
    user_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get the latest QA summary for a user by user ID
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Dictionary containing the latest QA summary with summary text and date,
        or None if no summary found
        
    Raises:
        QASummaryServiceError: If error occurs during retrieval
    """
    try:
        # Query the latest QA summary for the user
        latest_summary = db.query(QASessionSummary).filter(
            QASessionSummary.user_id == user_id
        ).order_by(QASessionSummary.created_at.desc()).first()
        
        if not latest_summary:
            logger.info(
                f"No QA summary found for user {user_id}",
                extra={"user_id": user_id}
            )
            return None
            
        # Return only the summary text and date as requested
        result = {
            "summary": latest_summary.summary,
            "date": latest_summary.created_at.isoformat()
        }
        
        logger.info(
            f"Retrieved latest QA summary for user {user_id}",
            extra={
                "user_id": user_id,
                "summary_id": latest_summary.id,
                "session_type": latest_summary.session_type,
                "created_at": latest_summary.created_at.isoformat()
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(
            f"Error retrieving QA summary for user {user_id}: {str(e)}",
            extra={"user_id": user_id, "error": str(e)}
        )
        raise QASummaryServiceError(f"Error retrieving QA summary: {str(e)}")

def get_qa_summaries_by_user_id(
    db: Session,
    user_id: int,
    limit: int = 10
) -> list[Dict[str, Any]]:
    """
    Get all QA summaries for a user with optional limit
    
    Args:
        db: Database session
        user_id: ID of the user
        limit: Maximum number of summaries to return (default: 10)
        
    Returns:
        List of dictionaries containing summary text and date
        
    Raises:
        QASummaryServiceError: If error occurs during retrieval
    """
    try:
        summaries = db.query(QASessionSummary).filter(
            QASessionSummary.user_id == user_id
        ).order_by(QASessionSummary.created_at.desc()).limit(limit).all()
        
        result = [
            {
                "summary": summary.summary,
                "date": summary.created_at.isoformat()
            }
            for summary in summaries
        ]
        
        logger.info(
            f"Retrieved {len(result)} QA summaries for user {user_id}",
            extra={
                "user_id": user_id,
                "count": len(result),
                "limit": limit
            }
        )
        
        return result
        
    except Exception as e:
        logger.error(
            f"Error retrieving QA summaries for user {user_id}: {str(e)}",
            extra={"user_id": user_id, "error": str(e)}
        )
        raise QASummaryServiceError(f"Error retrieving QA summaries: {str(e)}")

def get_qa_summary_by_id(
    db: Session,
    summary_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get a specific QA summary by ID
    
    Args:
        db: Database session
        summary_id: ID of the QA summary
        
    Returns:
        Dictionary containing full QA summary details, or None if not found
        
    Raises:
        QASummaryServiceError: If error occurs during retrieval
    """
    try:
        summary = db.query(QASessionSummary).filter(
            QASessionSummary.id == summary_id
        ).first()
        
        if not summary:
            return None
            
        result = {
            "id": summary.id,
            "user_id": summary.user_id,
            "session_type": summary.session_type,
            "summary": summary.summary,
            "date": summary.created_at.isoformat(),
            "conversation_data": summary.conversation_data,
            "session_metadata": summary.session_metadata
        }
        
        logger.info(
            f"Retrieved QA summary by ID: {summary_id}",
            extra={"summary_id": summary_id, "user_id": summary.user_id}
        )
        
        return result
        
    except Exception as e:
        logger.error(
            f"Error retrieving QA summary by ID {summary_id}: {str(e)}",
            extra={"summary_id": summary_id, "error": str(e)}
        )
        raise QASummaryServiceError(f"Error retrieving QA summary: {str(e)}")