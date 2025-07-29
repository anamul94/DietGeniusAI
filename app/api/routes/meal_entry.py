from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date
import json
import asyncio

from fastapi.responses import StreamingResponse

from app.api.deps import get_db, get_current_user, get_current_user_from_token
from app.models.user import User
from app.models.food_nutrition import MealType
from app.schemas.meal_entry import (
    MealEntry,
    MealEntryCreate,
    MealEntryUpdate,
    MealEntryPagination,
    MealTypeCheck
)
from app.schemas.meal_plan import (
    MealPlan,
    MealPlanPagination,
    MealPlanResponse,
    GenerateMealPlanRequest
)
from app.schemas.meal_types import MealTypesResponse, MealTypeInfo
from app.schemas.nutrition import FoodNutritionResponse
from app.services.meal_entry import (
    create_meal_entry,
    get_meal_entry_by_id,
    get_meal_entries,
    update_meal_entry,
    delete_meal_entry,
    check_meal_type_exists,
    save_nutrition_data_to_meal_entry,
    create_meal_plan,
    MealEntryServiceError
)
from app.services.meal_plan import (
    generate_and_save_meal_plan,
    get_meal_plans,
    get_latest_meal_plan,
    get_meal_plan_by_id,
    delete_meal_plan,
    generate_meal_plan_streaming,
    MealPlanServiceError
)
from app.services.meal_types import get_meal_types_response
from app.services.nutrition import parse_nutrition
from app.core.logging import logger
from app.utils.sse_session import add_connection, remove_connection


router = APIRouter()

@router.get("/meal-types", response_model=MealTypesResponse)
def get_meal_types():
    """
    Get all available meal type enum values
    
    Returns:
        Structured response containing meal types with their values and labels
    """
    try:
        response = get_meal_types_response()
        
        logger.info(
            f"Retrieved meal type enum values",
            extra={
                "total_meal_types": response.total_count,
                "meal_types": [mt.value for mt in response.meal_types]
            }
        )
        
        return response
    except Exception as e:
        logger.error(f"Error retrieving meal types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving meal types",
        )

@router.post("/", response_model=MealEntry, status_code=status.HTTP_201_CREATED)
def create_new_meal_entry(
    meal_in: MealEntryCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new meal entry with multiple food items
    """
    try:
        meal_entry = create_meal_entry(db, current_user.id, meal_in)
        logger.info(
            f"User created meal entry",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "entry_id": meal_entry.id,
                "client_ip": request.client.host if request.client else None,
            }
        )
        return meal_entry
    except MealEntryServiceError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        logger.error(f"Error creating meal entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating meal entry",
        )
    except Exception as e:
        logger.error(f"Unexpected error creating meal entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.get("/", response_model=MealEntryPagination)
def get_all_meal_entries(
    request: Request,
    meal_type: Optional[MealType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated meal entries for the current user
    """
    try:
        result = get_meal_entries(
            db, 
            user_id=current_user.id,
            meal_type=meal_type,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )
        
        logger.info(
            f"User retrieved meal entries",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "page": page,
                "limit": limit,
                "total_entries": result.total,
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return result
    except Exception as e:
        logger.error(f"Error retrieving meal entries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving meal entries",
        )

@router.get("/check", response_model=MealTypeCheck)
def check_meal_type(
    request: Request,
    meal_type: MealType,
    date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if a meal type already exists for a specific date
    """
    try:
        exists, meal_entry = check_meal_type_exists(
            db,
            current_user.id,
            meal_type,
            date
        )
        
        logger.info(
            f"User checked meal type existence",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "meal_type": meal_type,
                "date": date.isoformat(),
                "exists": exists,
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return MealTypeCheck(
            exists=exists,
            meal_entry=meal_entry
        )
    except Exception as e:
        logger.error(f"Error checking meal type: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking meal type",
        )


@router.post("/meal-plans/generate", response_model=MealPlanResponse)
async def generate_meal_plan(
    request: Request,
    current_user: User = Depends(get_current_user),
    session_id: str = Query(None, description="Session ID for tracking"),
):
    """
    Generate and save a meal plan for the current user
    """
    try:
        saved_meal_plan = await generate_and_save_meal_plan(
            user_id=current_user.id,
            session_id=session_id or f"session_{current_user.id}_{datetime.now().timestamp()}"
        )
        
        logger.info(
            f"User generated meal plan",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "meal_plan_id": saved_meal_plan.id,
                "plan_date": saved_meal_plan.plan_date.isoformat(),
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return MealPlanResponse(
            success=True,
            message="Meal plan generated and saved successfully",
            meal_plan=saved_meal_plan
        )
        
    except MealPlanServiceError as e:
        logger.error(f"Meal plan service error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error generating meal plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating meal plan",
        )

@router.get("/meal-plans", response_model=MealPlanPagination)
def get_user_meal_plans(
    request: Request,
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated meal plans for the current user (newest first)
    """
    try:
        result = get_meal_plans(
            db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )
        
        logger.info(
            f"User retrieved meal plans",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "page": page,
                "limit": limit,
                "total_plans": result.total,
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return result
    except Exception as e:
        logger.error(f"Error retrieving meal plans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving meal plans",
        )

@router.get("/meal-plans/latest", response_model=MealPlan)
def get_user_latest_meal_plan(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the latest meal plan for the current user
    """
    try:
        latest_plan = get_latest_meal_plan(db, current_user.id)
        
        if not latest_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No meal plans found for this user",
            )
        
        logger.info(
            f"User retrieved latest meal plan",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "meal_plan_id": latest_plan.id,
                "plan_date": latest_plan.plan_date.isoformat(),
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return latest_plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving latest meal plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving latest meal plan",
        )

@router.get("/meal-plans/{meal_plan_id}", response_model=MealPlan)
def get_meal_plan_by_id_endpoint(
    meal_plan_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific meal plan by ID
    """
    meal_plan = get_meal_plan_by_id(db, meal_plan_id)
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )
    
    # Check if the meal plan belongs to the current user (unless admin)
    if meal_plan.user_id != current_user.id and current_user.role != "admin":
        logger.warning(
            f"User attempted to access another user's meal plan",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "meal_plan_id": meal_plan_id,
                "meal_plan_owner_id": meal_plan.user_id,
                "client_ip": request.client.host if request.client else None,
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this meal plan",
        )
    
    logger.info(
        f"User retrieved meal plan",
        extra={
            "user_id": current_user.id,
            "username": current_user.username,
            "meal_plan_id": meal_plan_id,
            "client_ip": request.client.host if request.client else None,
        }
    )
    
    return meal_plan

@router.delete("/meal-plans/{meal_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal_plan_by_id(
    meal_plan_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a meal plan
    """
    # First check if the meal plan exists and belongs to the user
    meal_plan = get_meal_plan_by_id(db, meal_plan_id)
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found",
        )
    
    # Check if the meal plan belongs to the current user (unless admin)
    if meal_plan.user_id != current_user.id and current_user.role != "admin":
        logger.warning(
            f"User attempted to delete another user's meal plan",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "meal_plan_id": meal_plan_id,
                "meal_plan_owner_id": meal_plan.user_id,
                "client_ip": request.client.host if request.client else None,
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this meal plan",
        )
    
    try:
        success = delete_meal_plan(db, meal_plan_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found",
            )
        
        logger.info(
            f"User deleted meal plan",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "meal_plan_id": meal_plan_id,
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return None
    except MealPlanServiceError as e:
        logger.error(f"Error deleting meal plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting meal plan",
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting meal plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


@router.get("/{entry_id}", response_model=MealEntry)
def get_meal_entry(
    entry_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific meal entry by ID
    """
    entry = get_meal_entry_by_id(db, entry_id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal entry not found",
        )
    
    # Check if the entry belongs to the current user (unless admin)
    if entry.user_id != current_user.id and current_user.role != "admin":
        logger.warning(
            f"User attempted to access another user's meal entry",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "entry_id": entry_id,
                "entry_owner_id": entry.user_id,
                "client_ip": request.client.host if request.client else None,
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this entry",
        )
    
    logger.info(
        f"User retrieved meal entry",
        extra={
            "user_id": current_user.id,
            "username": current_user.username,
            "entry_id": entry_id,
            "client_ip": request.client.host if request.client else None,
        }
    )
    
    return entry

@router.put("/{entry_id}", response_model=MealEntry)
def update_meal_entry_by_id(
    entry_id: int,
    update_data: MealEntryUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a meal entry
    """
    # First check if the entry exists and belongs to the user
    entry = get_meal_entry_by_id(db, entry_id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal entry not found",
        )
    
    # Check if the entry belongs to the current user (unless admin)
    if entry.user_id != current_user.id and current_user.role != "admin":
        logger.warning(
            f"User attempted to update another user's meal entry",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "entry_id": entry_id,
                "entry_owner_id": entry.user_id,
                "client_ip": request.client.host if request.client else None,
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this entry",
        )
    
    try:
        updated_entry = update_meal_entry(db, entry_id, update_data)
        
        if not updated_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal entry not found",
            )
        
        logger.info(
            f"User updated meal entry",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "entry_id": entry_id,
                "fields_updated": list(update_data.model_dump(exclude_unset=True).keys()),
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return updated_entry
    except MealEntryServiceError as e:
        if "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        logger.error(f"Error updating meal entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating meal entry",
        )
    except Exception as e:
        logger.error(f"Unexpected error updating meal entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal_entry_by_id(
    entry_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a meal entry
    """
    # First check if the entry exists and belongs to the user
    entry = get_meal_entry_by_id(db, entry_id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal entry not found",
        )
    
    # Check if the entry belongs to the current user (unless admin)
    if entry.user_id != current_user.id and current_user.role != "admin":
        logger.warning(
            f"User attempted to delete another user's meal entry",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "entry_id": entry_id,
                "entry_owner_id": entry.user_id,
                "client_ip": request.client.host if request.client else None,
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this entry",
        )
    
    try:
        success = delete_meal_entry(db, entry_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal entry not found",
            )
        
        logger.info(
            f"User deleted meal entry",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "entry_id": entry_id,
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return None
    except MealEntryServiceError as e:
        logger.error(f"Error deleting meal entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting meal entry",
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting meal entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.post("/food-nutrition",
             status_code=status.HTTP_200_OK,
             response_model=FoodNutritionResponse)
async def upload_food_nutrition(
    files: List[UploadFile] = File(...),
    serving_size: str = Form(description="serving size"),
    consumed_at: str = Form(description="consumed at"),
    meal_type: str = Form(description="meal type"),
    session_id: str = Form(description="agent session id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload food images and get nutrition information, then save to meal entries
    """
    # Validate file types
    if files is not None and len(files) > 0:
        for file in files:
            if file.content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp", "image/gif"]:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid file type. Only JPEG, PNG, WebP, and GIF images are allowed."
                )
    
    try:
        # Parse nutrition data from files
        nutrition_result = await parse_nutrition(
            session_id=session_id,
            user_id=current_user.id,
            serving_size=serving_size,
            files=files
        )
        
        # Convert to FoodNutritionResponse if needed
        food_nutrition_response = None
        if isinstance(nutrition_result, dict):
            try:
                food_nutrition_response = FoodNutritionResponse(**nutrition_result)
            except Exception as e:
                logger.warning(f"Error converting nutrition result to FoodNutritionResponse: {str(e)}")
                food_nutrition_response = nutrition_result
        else:
            food_nutrition_response = nutrition_result
        
        # Save nutrition data to database using service
        try:
            save_nutrition_data_to_meal_entry(
                db=db,
                user_id=current_user.id,
                meal_type=meal_type,
                consumed_at=consumed_at,
                nutrition_data=food_nutrition_response.data,
                message=food_nutrition_response.message
            )
            
            logger.info(
                f"Successfully processed and saved food nutrition data",
                extra={
                    "user_id": current_user.id,
                    "username": current_user.username,
                    "meal_type": meal_type,
                    "consumed_at": consumed_at,
                    "food_count": len(food_nutrition_response.data) if food_nutrition_response.data else 0
                }
            )
            
        except Exception as e:
            logger.error(f"Error saving nutrition data to database: {str(e)}", exc_info=True)
            # Continue with the response even if saving to DB fails
            # This ensures the user still gets the nutrition information
        
        return food_nutrition_response
    
    except Exception as e:
        logger.error(f"Error processing food nutrition: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process food nutrition. Please try again later."
        )


@router.get("/stream/generate-meal-plan")
async def generate_meal_plan_stream(
    session_id: str = Query(..., description="Session ID for SSE"),
    token: str = Query(None, description="JWT token for authentication (deprecated - use cookies instead)"),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Generate meal plan using Server-Sent Events (SSE) streaming
    
    This endpoint provides real-time streaming of meal plan generation:
    1. Connection establishment
    2. Progress updates (0-100%)
    3. Real-time content streaming
    4. Final complete response
    
    **SSE Message Types:**
    - `connected`: Connection established
    - `progress`: Generation progress (0-100%)
    - `chunk`: Real-time content chunk
    - `complete`: Final complete response
    - `error`: Error message
    
    **Authentication:**
    - Preferred: Use HTTP cookies (access_token)
    - Legacy: Use query parameter token (may fail with long tokens)
    """
    logger.info(f"Generating meal plan for user with session ID: {session_id}")
    
    # Try to get token from cookies first, then fallback to query parameter
    token_value = None
    
    # Check cookies for token
    if request and hasattr(request, 'cookies'):
        token_value = request.cookies.get('access_token')
    
    # Fallback to query parameter for backward compatibility
    if not token_value:
        token_value = token
    
    if not token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required"
        )
    
    current_user = get_current_user_from_token(token_value, db)
    add_connection(session_id=session_id)
    
    return StreamingResponse(
        generate_meal_plan_streaming(user_id=current_user.id, session_id=session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "Keep-Alive": "timeout=3600, max=1000",  # 1 hour timeout, max 1000 requests
            "X-Accel-Buffering": "no",  # Disable nginx buffering
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Cache-Control",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Expose-Headers": "Cache-Control, Connection, Keep-Alive",
        }
    )