from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from app.core.logging import logger
from app.models.medical import MedicalReport
from app.models.user import User, OnboardingStatus
from sqlalchemy import desc
from app.core.pagination import BasePaginator, PaginationResult
from app.agents.agetns import user_onboarding_agent, get_memory_test_agent
from fastapi import Depends
from app.schemas.qa import QaAns, QA
from app.utils.age_calculator import calculate_age
import json

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
    
    
  # Ensure this import exists and is correct

async def user_onboarding_qa(
    ans: QaAns,
    user_id: int,
    db: Session 
):
    try:
        agent = user_onboarding_agent()
        # logger.info(f"agnet info {agent}")
        user_message = ""
        
        if ans.count == 0:
            # Fetch user info
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Fetch 2 reports for the user
            medical_reports = get_user_medical_reports_paginated(
                db=db,
                user_id=user_id,
                page=1,
                limit=2
            )
            
            if medical_reports is None:
                raise HTTPException(status_code=500, detail="Failed to fetch medical reports.")
            
            # Create data structure with user info
            data_dict = {
                "reports": [{
                    "id": str(report.id),
                    "medical_report": report.medical_report,
                    "uploaded_at": str(report.created_at)
                } for report in medical_reports.items],
                "user_profile": {
                    "gender": user.gender,
                    "age": calculate_age(user.dob),
                    "profession": user.profession
                },
                "user_response": ans.answer,
                "qa_round": ans.count+1
            }
            
            # Convert to string
            
            user_message = json.dumps(data_dict)
        else:
            # Add completion instruction for round 3
            if ans.count == 2:
                completion_note = "This is the final question. After this response, provide a comprehensive assessment summary."
            else:
                completion_note = ""
            
            data = {
                "answer": ans.answer,
                "qa_round": ans.count+1,
                "completion_note": completion_note
            }
            user_message = json.dumps(data)
        
        # Process the user message
        response =  agent.run(message=user_message, user_id=str(user_id), session_id=str(user_id))
        qa_res = response.content
        logger.info(f"Agent response for user {user_id}: {response}")
        
        # Update onboarding status if completed (after 4 rounds)
        if qa_res.is_done:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.onboarding_status = "completed"
                db.add(user)
                db.commit()
        # if ans.count >= 3:
        #     user = db.query(User).filter(User.id == user_id).first()
        #     if user:
        #         user.onboarding_status = "completed"
        #         db.add(user)
        #         db.commit()
        
        chat_hist = {
            "question": qa_res.question,
        }
        prev_hist = ans.chat_history if ans.chat_history else []
        prev_hist.append(chat_hist)
            
        return QA(
            question=qa_res.question,
            is_done=qa_res.is_done,
            count=ans.count+1,
            chat_history=prev_hist
        )
        
    except Exception as e:
        logger.error(f"Error processing onboarding QA for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process onboarding QA. Please try again later.")
    
    
async def agent_mem_test(message: str, user_id: str, ):
        agent = get_memory_test_agent()
        response = agent.run(message=message, user_id=str(user_id))
        logger.info(f"Agent response for user {user_id}: {response}")
        return {"response": response.content}