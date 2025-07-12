from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from app.core.logging import logger
from app.models.medical import MedicalReport
from sqlalchemy import desc
from app.core.pagination import BasePaginator, PaginationResult


class MedicalReportPaginator(BasePaginator):
    def get_query(self, user_id: int):
        return (
            self.db.query(MedicalReport)
            .filter(MedicalReport.user_id == user_id)
            .order_by(desc(MedicalReport.created_at))
        )

def get_user_medical_reports_paginated(
    db: Session, 
    user_id: int, 
    page: int = 1,
    limit: int = 10
) -> Optional[PaginationResult]:
    """
    Retrieve paginated medical reports for a user.
    
    Args:
        db: Database session
        user_id: User ID to filter reports
        page: Page number (1-based)
        limit: Items per page
        
    Returns:
        PaginationResult with medical reports or None if error
    """
    try:
        paginator = MedicalReportPaginator(db)
        return paginator.paginate(page=page, limit=limit, user_id=user_id)
    except SQLAlchemyError as e:
        logger.error(f"Database error when fetching medical reports: {str(e)}")
        return None