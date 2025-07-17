import json
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, AsyncGenerator
from datetime import datetime, date
from fastapi import HTTPException, status

from app.models.meal_plan import MealPlan
from app.models.user import User
from app.schemas.meal_plan import MealPlanCreate, MealPlanUpdate
from app.core.pagination import BasePaginator, PaginationResult
from app.core.logging import logger
from app.agents.agetns import meal_plan_agent
from app.services.user import get_user
from app.api.deps import get_db
from app.utils.age_calculator import calculate_age

from app.utils.sse_session import add_connection, remove_connection

class MealPlanServiceError(Exception):
    """Custom exception for meal plan service errors"""
    pass

class MealPlanPaginator(BasePaginator):
    """Paginator for meal plans"""
    
    def get_query(self, user_id: Optional[int] = None, start_date: Optional[date] = None, 
                  end_date: Optional[date] = None):
        """Return the base query for pagination with optional filters"""
        query = self.db.query(MealPlan)
        
        # Apply filters if provided
        if user_id is not None:
            query = query.filter(MealPlan.user_id == user_id)
        
        if start_date is not None:
            query = query.filter(MealPlan.plan_date >= start_date)
            
        if end_date is not None:
            query = query.filter(MealPlan.plan_date <= end_date)
            
        # Order by plan_date (newest first)
        return query.order_by(MealPlan.plan_date.desc())

async def create_or_update_meal_plan(
    db: Session, 
    user_id: int, 
    meal_plan_content: str,
    plan_date: date
) -> MealPlan:
    """
    Create a new meal plan or update existing one for the same date
    
    Args:
        db: Database session
        user_id: ID of the user
        meal_plan_content: The generated meal plan content
        plan_date: Date for which the meal plan is created
        
    Returns:
        Created or updated meal plan
        
    Raises:
        MealPlanServiceError: If error occurs during save
    """
    try:
        # Check if meal plan already exists for this user and date
        existing_plan = db.query(MealPlan).filter(
            MealPlan.user_id == user_id,
            MealPlan.plan_date == plan_date
        ).first()
        
        if existing_plan:
            # Update existing meal plan
            existing_plan.meal_plan = meal_plan_content
            existing_plan.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_plan)
            
            logger.info(
                f"Updated meal plan for user {user_id} on {plan_date}",
                extra={
                    "user_id": user_id,
                    "plan_date": plan_date.isoformat(),
                    "meal_plan_id": existing_plan.id
                }
            )
            
            return existing_plan
        else:
            # Create new meal plan
            db_meal_plan = MealPlan(
                user_id=user_id,
                meal_plan=meal_plan_content,
                plan_date=plan_date
            )
            
            db.add(db_meal_plan)
            db.commit()
            db.refresh(db_meal_plan)
            
            logger.info(
                f"Created new meal plan for user {user_id} on {plan_date}",
                extra={
                    "user_id": user_id,
                    "plan_date": plan_date.isoformat(),
                    "meal_plan_id": db_meal_plan.id
                }
            )
            
            return db_meal_plan
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating/updating meal plan: {str(e)}")
        raise MealPlanServiceError(f"Error creating/updating meal plan: {str(e)}")

def get_meal_plan_by_id(db: Session, meal_plan_id: int) -> Optional[MealPlan]:
    """
    Get a meal plan by ID
    
    Args:
        db: Database session
        meal_plan_id: ID of the meal plan to retrieve
        
    Returns:
        Meal plan if found, None otherwise
    """
    return db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()

def get_latest_meal_plan(db: Session, user_id: int) -> Optional[MealPlan]:
    """
    Get the latest meal plan for a user
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Latest meal plan if found, None otherwise
    """
    return db.query(MealPlan).filter(
        MealPlan.user_id == user_id
    ).order_by(MealPlan.plan_date.desc()).first()

def get_meal_plans(
    db: Session,
    user_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    limit: int = 10
) -> PaginationResult:
    """
    Get paginated meal plans with optional filters
    
    Args:
        db: Database session
        user_id: Optional filter by user ID
        start_date: Optional filter by start date
        end_date: Optional filter by end date
        page: Page number
        limit: Items per page
        
    Returns:
        Paginated result with meal plans
    """
    paginator = MealPlanPaginator(db)
    return paginator.paginate(
        page=page,
        limit=limit,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )

def delete_meal_plan(db: Session, meal_plan_id: int) -> bool:
    """
    Delete a meal plan
    
    Args:
        db: Database session
        meal_plan_id: ID of the meal plan to delete
        
    Returns:
        True if deleted, False if not found
    """
    db_meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
    
    if not db_meal_plan:
        return False
        
    try:
        db.delete(db_meal_plan)
        db.commit()
        
        logger.info(
            f"Deleted meal plan",
            extra={
                "meal_plan_id": meal_plan_id,
                "user_id": db_meal_plan.user_id
            }
        )
        
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting meal plan: {str(e)}")
        raise MealPlanServiceError(f"Error deleting meal plan: {str(e)}")

async def generate_and_save_meal_plan(
    user_id: int,
    session_id: str,
) -> MealPlan:
    """
    Generate a new meal plan for the user and save it to database
    
    Args:
        user_id: User ID
        session_id: Session ID
        
    Returns:
        Created meal plan
    """
    db_generator = get_db()
    db = next(db_generator)
    try:
        user = get_user(db, user_id)
        logger.info(
            f"Generating meal plan for user {user.username} with session {session_id}"
        )
        
        today = datetime.now().date()
        meal_planner = meal_plan_agent()
        meal_plan_content = ""
        age = calculate_age(user.dob)
        
        message = f"""Generate a well defined meal plan for 7 days,
            user name: {user.username},
            gender: {user.gender},
            age: {age},
            profession: {user.profession}
            country: {user.country},
            city: {user.city},
            "dietary preferences": {user.dietary_preference or ''},
            "purpose of joining": {user.purpose_of_joining or ''},
            date: {today}
        """
        
        logger.info(f"Meal plan generation message: {message}")
        
        # Generate meal plan using the agent
        for chunk in meal_planner.run(
            message=message,
            user_id=user.id,
            stream=True,
        ):
            if chunk is not None:
                meal_plan_content += chunk.content
                print(chunk.content, end="", flush=True)
        
        # Save the generated meal plan to database
        saved_meal_plan = create_or_update_meal_plan(
            db=db,
            user_id=user_id,
            meal_plan_content=meal_plan_content,
            plan_date=today
        )
        
        return saved_meal_plan
        
    finally:
        db.close()



async def generate_meal_plan_streaming(
    user_id: int,
    session_id: str,
) -> AsyncGenerator[str, None]:
    """
    Generate meal plan with streaming response
    
    Args:
        user_id: User ID
        session_id: Session ID
        
    Yields:
        Chunks of meal plan content as they're generated
    """
    db_generator = get_db()
    db = next(db_generator)
    
    # Set timeout for the entire streaming process (5 minutes)
    MAX_STREAMING_TIME = 300  # 5 minutes in seconds
    
    try:
        user = get_user(db, user_id)
        logger.info(
            f"Streaming meal plan for user {user.username} with session {session_id}"
        )
        
        # Track start time for timeout
        start_time = asyncio.get_event_loop().time()
        
        yield f"data: {json.dumps({'type': 'connection', 'message': 'Connection established'})}\n\n"
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Initializing meal plan agent...', 'progress': 10})}\n\n"
        await asyncio.sleep(0.5)
        
        # Check for timeout
        if asyncio.get_event_loop().time() - start_time > MAX_STREAMING_TIME:
            raise TimeoutError("Streaming timeout exceeded")
        
        today = date.today()
        meal_planner = meal_plan_agent()
        age = calculate_age(user.dob)
        
        message = f"""Generate a well defined meal plan for 7 days,
            user name: {user.username},
            gender: {user.gender},
            age: {age},
            profession: {user.profession}
            country: {user.country},
            city: {user.city},
            "dietary preferences": {user.dietary_preference or ''},
            "purpose of joining": {user.purpose_of_joining or ''},
            date: {today}
        """
        
        logger.info(f"Meal plan streaming message: {message}")
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Preparing personalized meal plan...', 'progress': 20})}\n\n"
        await asyncio.sleep(0.5)
        
        # Check for timeout
        if asyncio.get_event_loop().time() - start_time > MAX_STREAMING_TIME:
            raise TimeoutError("Streaming timeout exceeded")
        
        # Generate meal plan using the agent with streaming
        chunk_index = 0
        meal_plan_content = ""
        
        try:
            # Use asyncio.wait_for to add timeout to the agent generation
            agent_generator = meal_planner.run(
                message=message,
                user_id=str(user.id),
                stream=True,
            )
            
            for chunk in agent_generator:
                # Check for timeout on each chunk
                if asyncio.get_event_loop().time() - start_time > MAX_STREAMING_TIME:
                    raise TimeoutError("Streaming timeout exceeded")
                    
                if chunk is not None and chunk.content:
                    yield f"data: {json.dumps({'type': 'chunk', 'data': chunk.content, 'chunk_index': chunk_index})}\n\n"
                    chunk_index += 1
                    meal_plan_content += chunk.content
                    
                    # Add small delay to prevent overwhelming the client
                    await asyncio.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"Error during agent streaming: {str(e)}")
            raise
        
        # Check for timeout
        if asyncio.get_event_loop().time() - start_time > MAX_STREAMING_TIME:
            raise TimeoutError("Streaming timeout exceeded")
        
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Finalizing meal plan...', 'progress': 90})}\n\n"
        
        saved_meal_plan = await create_or_update_meal_plan(
            db=db,
            user_id=user_id,
            meal_plan_content=meal_plan_content,
            plan_date=today
        )
        
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Meal plan completed!', 'progress': 100})}\n\n"
        await asyncio.sleep(0.5)
        
        # Send complete response with proper structure
        complete_response = {
            'type': 'complete',
            'full_response': meal_plan_content,
            'plan_date': today.isoformat(),
            'meal_plan': saved_meal_plan.to_dict()
        }
        yield f"data: {json.dumps(complete_response)}\n\n"
        
        # Send end event to properly close the connection
        yield f"data: {json.dumps({'type': 'end', 'message': 'Streaming completed'})}\n\n"
    
    except asyncio.CancelledError:
        # This is expected when the client disconnects.
        logger.info(f"Client disconnected for session_id {session_id}")
        raise
    except TimeoutError as e:
        logger.error(f"Streaming timeout for session_id {session_id}: {str(e)}")
        error_response = {
            'type': 'error',
            'message': "Meal plan generation timed out. Please try again."
        }
        yield f"data: {json.dumps(error_response)}\n\n"
    except Exception as e:
        logger.error(f"Error in meal plan streaming: {str(e)}")
        error_response = {
            'type': 'error',
            'message': f"Error generating meal plan: {str(e)}"
        }
        yield f"data: {json.dumps(error_response)}\n\n"
    
    finally:
        # Clean up connection
        remove_connection(session_id=session_id)
        db.close()
        
    
    

#########***********STREAM*************************

# async def generate_meal_plan_streaming(
#     user_id: int,
#     session_id: str,
# ) -> AsyncGenerator[str, None]:
    
    
    