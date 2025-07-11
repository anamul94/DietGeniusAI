from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Request
from fastapi.responses import JSONResponse
import shutil
import os
from typing import List
from app.core.logging import logger
from app.services.medical_parser import MedicalReportParserService


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
async def upload_file(files: List[UploadFile] = File(...)):
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
        logger.info("Successfully processed medical report")
        return result
        
    except HTTPException as e:
        logger.error(f"HTTP exception during file processing: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Error processing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

