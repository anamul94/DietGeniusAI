# services/database.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.models.medical import MedicalReport
from app.db.base import get_db
from app.core.logging import logger

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db

    async def create_medical_report_record(
        self,
        processing_id: str,
        user_id: str,
        filename: str,
        file_type: str,
        report_type: str,
        user_notes: Optional[str] = None,
        status: str = "PROCESSING"
    ) -> bool:
        """Create initial medical report record"""
        try:
            report = MedicalReport(
                id=uuid.UUID(processing_id),
                user_id=int(user_id),
                original_filename=filename,
                report_type=report_type,
                processing_status=status,
                uploaded_at=datetime.utcnow()
            )
            
            self.db.add(report)
            self.db.commit()
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to create medical report record: {str(e)}")
            return False

    async def update_medical_report_results(
        self,
        processing_id: str,
        results: Dict[str, Any]
    ) -> bool:
        """Update medical report with processing results"""
        try:
            report = self.db.query(MedicalReport).filter(
                MedicalReport.id == uuid.UUID(processing_id)
            ).first()
            
            if not report:
                return False
                
            report.processing_status = results.get("processing_status", "COMPLETED")
            report.confidence_score = results.get("confidence_score", 0.0)
            report.raw_text = results.get("raw_text", "")
            report.structured_data = results.get("structured_data", {})
            report.ai_summary = results.get("ai_summary", "")
            report.key_findings = results.get("key_findings", [])
            report.recommendations = {
                "nutrition_recommendations": results.get("nutrition_recommendations", []),
                "health_insights": results.get("health_insights", []),
                "risk_assessment": results.get("risk_assessment", {})
            }
            
            self.db.commit()
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to update medical report results: {str(e)}")
            return False

    async def get_medical_report(self, processing_id: str, user_id: str) -> Optional[Dict]:
        """Get medical report by ID"""
        try:
            report = self.db.query(MedicalReport).filter(
                MedicalReport.id == uuid.UUID(processing_id),
                MedicalReport.user_id == int(user_id)
            ).first()
            
            if not report:
                return None
                
            return {
                "processing_id": str(report.id),
                "user_id": str(report.user_id),
                "filename": report.original_filename,
                "report_type": report.report_type,
                "processing_status": report.processing_status,
                "confidence_score": report.confidence_score or 0.0,
                "structured_data": report.structured_data or {},
                "ai_summary": report.ai_summary or "",
                "key_findings": report.key_findings or [],
                "nutrition_recommendations": report.recommendations.get("nutrition_recommendations", []) if report.recommendations else [],
                "health_insights": report.recommendations.get("health_insights", []) if report.recommendations else [],
                "risk_assessment": report.recommendations.get("risk_assessment", {}) if report.recommendations else {},
                "processed_at": report.uploaded_at,
                "created_at": report.uploaded_at
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to get medical report: {str(e)}")
            return None

    async def list_user_medical_reports(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        report_type: Optional[str] = None
    ) -> List[Dict]:
        """List user's medical reports"""
        try:
            query = self.db.query(MedicalReport).filter(
                MedicalReport.user_id == int(user_id)
            )
            
            if report_type:
                query = query.filter(MedicalReport.report_type == report_type)
                
            reports = query.offset(skip).limit(limit).all()
            
            result = []
            for report in reports:
                result.append({
                    "processing_id": str(report.id),
                    "user_id": str(report.user_id),
                    "filename": report.original_filename,
                    "report_type": report.report_type,
                    "processing_status": report.processing_status,
                    "confidence_score": report.confidence_score or 0.0,
                    "structured_data": report.structured_data or {},
                    "ai_summary": report.ai_summary or "",
                    "key_findings": report.key_findings or [],
                    "nutrition_recommendations": report.recommendations.get("nutrition_recommendations", []) if report.recommendations else [],
                    "health_insights": report.recommendations.get("health_insights", []) if report.recommendations else [],
                    "risk_assessment": report.recommendations.get("risk_assessment", {}) if report.recommendations else {},
                    "processed_at": report.uploaded_at,
                    "created_at": report.uploaded_at
                })
                
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Failed to list medical reports: {str(e)}")
            return []

    async def delete_medical_report(self, processing_id: str, user_id: str) -> bool:
        """Delete medical report"""
        try:
            report = self.db.query(MedicalReport).filter(
                MedicalReport.id == uuid.UUID(processing_id),
                MedicalReport.user_id == int(user_id)
            ).first()
            
            if not report:
                return False
                
            self.db.delete(report)
            self.db.commit()
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to delete medical report: {str(e)}")
            return False

    async def update_processing_status(
        self,
        processing_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update processing status"""
        try:
            report = self.db.query(MedicalReport).filter(
                MedicalReport.id == uuid.UUID(processing_id)
            ).first()
            
            if not report:
                return False
                
            report.processing_status = status
            if error_message:
                report.ai_summary = f"Processing failed: {error_message}"
                
            self.db.commit()
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Failed to update processing status: {str(e)}")
            return False