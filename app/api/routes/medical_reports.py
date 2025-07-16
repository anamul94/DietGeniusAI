from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query, Form
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.services.medical_parser import MedicalReportParserService
from app.services.medical import get_user_medical_reports_paginated, user_onboarding_qa, agent_mem_test
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.medical import MedicalReport
from app.db.base import get_db
from app.utils.id_gen import generate_custom_id

from app.schemas.qa import QA, QaAns
from app.schemas.NutritionistQA import NutritionistQA


router = APIRouter()
allowed_mime_types = {
        'application/pdf',
        'application/msword',                  # .doc
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
        'text/plain',                          # .txt
        'text/markdown',                       # .md
        'text/x-markdown',                     # .md (alternative)
        'image/jpeg',                          # .jpg, .jpeg
        'image/png',                           # .png
        'image/webp',
    }

medicla_parser_service = MedicalReportParserService()

@router.post("/medical", status_code=status.HTTP_200_OK)
async def upload_file(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if not files:
        logger.warning("No files provided in medical report upload")
        raise HTTPException(status_code=400, detail="No files provided")
    if len(files) > 3:
        logger.warning(f"Too many files uploaded: {len(files)}")
        raise HTTPException(status_code=400, detail="Too many files. Maximum 3 files allowed.")    
    
    try:
        for file in files:
            logger.info(f"Processing file: {file.filename}, Content-Type: {file.content_type}")
            
            if file.content_type not in allowed_mime_types:
                file_extension = file.filename.lower().split('.')[-1] if file.filename else ''
                allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'webp'}
                
                if file_extension not in allowed_extensions:
                    logger.warning(f"Invalid file type: {file.filename} (Content-Type: {file.content_type})")
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Invalid file type: {file.filename} (Content-Type: {file.content_type})"
                    )
        
        result = await medicla_parser_service.process_medical_report(files)
        logger.info(f"Successfully processed medical report for user {current_user.id}")
        
        # Save to database
        medical_report = MedicalReport(
            user_id=current_user.id,
            medical_report=result.get("results", []),
        )
        db.add(medical_report)
        db.commit()
        db.refresh(medical_report)
        
        logger.info(f"Medical report saved to database with ID: {medical_report.id}")
        
        return {
            "id": medical_report.id,
            "processing_status": "completed",
            "data": result
        }
        
    except HTTPException as e:
        logger.error(f"HTTP exception during file processing for user {current_user.id}: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error processing medical report for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process medical report. Please try again later.")


@router.get("/medical", status_code=status.HTTP_200_OK)
async def get_medical_reports(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Get paginated medical reports for the current user, sorted by date (newest first)"""
    
    try:
        result = get_user_medical_reports_paginated(db, current_user.id, page, limit)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to fetch medical reports")
        
        return {
            "data": [
                {
                    "id": str(report.id),
                    "medical_report": report.medical_report,
                    "uploaded_at": report.created_at
                }
                for report in result.items
            ],
            "pagination": {
                "page": result.page,
                "limit": result.limit,
                "total": result.total,
                "pages": result.pages
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching medical reports for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch medical reports. Please try again later.")



@router.post("/onboarding-qa",response_model=NutritionistQA)
async def onoarding_qa(
    ans:QaAns,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
    ):
    try:
        # Generate next question based on count
       return await user_onboarding_qa(db=db, user_id=current_user.id, ans=ans)
    except Exception as e:
        logger.error(f"Error in onboarding QA for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process onboarding QA.")
    
@router.post("/memory-test")
async def memory_test(
    message: str,
    current_user: User = Depends(get_current_active_user),
    ):
    try:
        # Generate next question based on count
       return await agent_mem_test(message=message, user_id=current_user.id)
    except Exception as e:
        logger.error(f"Error in onboarding QA for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process onboarding QA.")
    
    
@router.get("/generate-session-id/", status_code=status.HTTP_200_OK)
async def generate_session_id(
    current_user: User = Depends(get_current_active_user),
):
    try:
        # Fetch the user from the database   
        return {"session_id": generate_custom_id(current_user)}
    
    except Exception as e:
        logger.error(f"Error generating session ID for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate session ID. Please try again later.")
    