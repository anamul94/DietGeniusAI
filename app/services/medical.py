from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional
from app.core.logging import logger
from app.schemas.NutritionistQA import NutritionistQA
from app.models.medical import MedicalReport
from app.models.user import User
from app.models.qa_session_summary import QASessionSummary
from sqlalchemy import desc
from app.core.pagination import BasePaginator, PaginationResult
from app.agents.agetns import user_onboarding_agent, get_memory_test_agent
from app.agents.onboarding_agent import graph, generate_summary
from app.schemas.qa import QAAnsReq, QA, QAState
from app.schemas.qa_session_summary import QASessionSummaryCreate
from app.utils.age_calculator import calculate_age
import json
from datetime import datetime
from app.services.redis_storage import RedisQuestionStorage
from app.constants.prompts import qa
from app.agents.memory.pg_store import store_manager

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

async def user_onboarding_qa(
    ans: QAAnsReq,
    user_id: int,
    db: Session
):
    try:
        # Validate that all questions have answers
        if ans.has_unanswered_questions():
            raise HTTPException(
                status_code=400,
                detail="Please answer all questions before proceeding."
            )
        # qa_state = QAState(
        #     qa=ans.qa,
        #     count=ans.count,
        # )
        # qa_state.qa = ans.qa
        # qa_state.count = ans.count
        
        config = {"configurable": {"thread_id": str(user_id)+"09", "user_id": str(user_id)} }
        
        today = datetime.now().date()
        
        # Increment count for tracking
        current_count = ans.count + 1
        
        # Fetch user info first since we need it in multiple places
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Validate required profile data
        missing_fields = []
        if not user.height:
            missing_fields.append("height")
        if not user.weight:
            missing_fields.append("weight")
        if not user.dietary_preference:
            missing_fields.append("dietary_preference")
        if not user.purpose_of_joining:
            missing_fields.append("purpose_of_joining")
            
        if missing_fields and ans.count == 0:
            logger.warning(f"Missing required profile data for user {user_id}: {missing_fields}")
            raise HTTPException(
                status_code=400,
                detail=f"Please complete your profile before starting onboarding. Missing: {', '.join(missing_fields)}"
            )
            
        # Log user profile data for debugging
        logger.info(f"User profile data for onboarding: user_id={user_id}, "
                   f"height={user.height}, weight={user.weight}, bmi={user.bmi}, "
                   f"dietary_preference={user.dietary_preference}, purpose_of_joining={user.purpose_of_joining}")
        reports_data = [] 
        user_profile = {}  
        if ans.count == 0:
            # First round - include user profile and medical reports
            medical_reports = get_user_medical_reports_paginated(
                db=db,
                user_id=user_id,
                page=1,
                limit=2
            )
            
           
            if medical_reports and medical_reports.items:
                reports_data = [{
                    "id": str(report.id),
                    "medical_report": report.medical_report,
                    "uploaded_at": str(report.created_at)
                } for report in medical_reports.items]
            # qa_state.medical_report = json.dumps(reports_data)
            # Create data structure with user info
            # Handle null values gracefully
            user_profile = {
                "gender": user.gender or "Not specified",
                "age": calculate_age(user.dob) if user.dob else "Not specified",
                "profession": user.profession or "Not specified",
                "height": user.height or 0,
                "weight": user.weight or 0,
                "bmi": user.bmi or 0,
                "dietary_preference": user.dietary_preference or "Not specified",
                "purpose_of_joining": user.purpose_of_joining or "Not specified"
            }
            
            # Only include valid measurements
            if user.height and user.weight:
                user_profile["bmi"] = user.bmi or round(user.weight / ((user.height / 100) ** 2), 2)
            
           
        logger.info(f"User message for round  {ans.qa}")
    
        # Process the user message
        # Ensure we pass the correct QAState structure expected by the graph
       
        past_conversations = RedisQuestionStorage.get_questions(user_id=user_id)
        past_conversations = json.dumps(past_conversations)
        user_message = qa.start_qa_message_template.format(
            patient_info=json.dumps(user_profile),
            medical_report=json.dumps(reports_data),
            patient_response=ans.qa,
            qa_round_number=ans.count + 1,
            date = today.strftime("%Y-%m-%d"),
        )
        
        if ans.count > 2:
            user_message + "\n\nPlease completed the onboarding process."
        
        RedisQuestionStorage.save_questions(user_id=user_id, question=user_message)
        print("user message")
        # print(user_message)
        # user_message.format(
        #     past_conversations=past_conversations
        # )
        user_message = user_message + "\n\nPrevious QA Round ." + json.dumps(past_conversations)
        print("***************************************************")
        print(user_message)
        print("***************************************************")
        response =  graph.invoke({"message":user_message}, config=config)
        summary = ""
        print("accessing is completed")
        # print(response["questions"]["is_complete"])
        # print(list(graph.get_state_history(config)))
        if response["questions"].is_complete or ans.count >3:
            conversations = RedisQuestionStorage.get_questions(user_id=user_id)
            conv_summ_msg = qa.qa_conversation_summ_user_template.format(
                conversation=conversations,
                date= today.strftime("%Y-%m-%d")
            )
            summary = generate_summary(message=conv_summ_msg, config=config)
            # store_manager.invoke({
            #     "messages": conv_summ_msg,
            # }, config=config)
            # Update user onboarding status to completed
            user.onboarding_status = "completed"
            db.add(user)
            db.commit()
            
            # Save summary to database
            try:
                qa_summary = QASessionSummary(
                    user_id=user_id,
                    session_type="base_condition",
                    summary=summary,
                    conversation_data={
                        "conversations": conversations,
                        "qa_rounds": current_count,
                        "completed_at": datetime.now().isoformat()
                    },
                    session_metadata={
                        "session_type": "base_condition",
                        "questions_count": len(ans.qa) if ans.qa else 0,
                        "completion_round": current_count
                    }
                )
                db.add(qa_summary)
                db.commit()
                logger.info(f"QA session summary saved for user {user_id}")
               
            except SQLAlchemyError as e:
                logger.error(f"Error saving QA session summary: {str(e)}")
                db.rollback()
                # Continue even if summary save fails - don't block user completion
            
            db.commit()
            
        
        return QA(
            data=response["questions"],
            count=current_count,
            summary=summary,
        )

       
        
    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
    except Exception as e:
        logger.error(f"Error processing onboarding QA for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process onboarding QA. Please try again later.")
    
async def agent_mem_test(message: str, user_id: str):
    agent = get_memory_test_agent()
    response = agent.run(message=message, user_id=str(user_id))
    return {"response": response.content}