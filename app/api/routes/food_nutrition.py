from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.food_nutrition import MealType
from app.schemas.food_nutrition import (
    FoodNutrition,
    FoodNutritionCreate,
    FoodNutritionUpdate,
    FoodNutritionPagination,
    FoodNutritionListResponse
)
from app.services.food_nutrition import (
    create_food_nutrition, 
    get_food_nutrition_by_id, 
    get_food_nutrition_entries,
    update_food_nutrition,
    delete_food_nutrition,
    FoodNutritionServiceError
)
from app.core.logging import logger

router = APIRouter()

@router.post("/", response_model=FoodNutrition, status_code=status.HTTP_201_CREATED)
def create_nutrition_entry(
    nutrition_in: FoodNutritionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new food nutrition entry
    """
    try:
        nutrition_entry = create_food_nutrition(db, current_user.id, nutrition_in)
        logger.info(
            f"User created food nutrition entry",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "entry_id": nutrition_entry.id,
                "client_ip": request.client.host if request.client else None,
            }
        )
        return nutrition_entry
    except FoodNutritionServiceError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        logger.error(f"Error creating food nutrition entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating food nutrition entry",
        )
    except Exception as e:
        logger.error(f"Unexpected error creating food nutrition entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.get("/", response_model=FoodNutritionPagination)
def get_nutrition_entries(
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
    Get paginated food nutrition entries for the current user
    """
    try:
        result = get_food_nutrition_entries(
            db, 
            user_id=current_user.id,
            meal_type=meal_type,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )
        
        logger.info(
            f"User retrieved food nutrition entries",
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
        logger.error(f"Error retrieving food nutrition entries: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving food nutrition entries",
        )

@router.get("/list", response_model=FoodNutritionListResponse)
def get_nutrition_list(
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
    Get food nutrition entries in FoodNutritionList format
    """
    try:
        result = get_food_nutrition_entries(
            db,
            user_id=current_user.id,
            meal_type=meal_type,
            start_date=start_date,
            end_date=end_date,
            page=page,
            limit=limit
        )
        
        # Convert to FoodNutritionListResponse format
        food_items = []
        for item in result.items:
            food_item = FoodNutrition(
                id=item.id,
                user_id=item.user_id,
                food_name=item.food_name,
                serving_size=item.serving_size,
                meal_type=item.meal_type,
                nutrition=item.nutrition,
                consumed_at=item.consumed_at,
                created_at=item.created_at,
                updated_at=item.updated_at
            )
            food_items.append(food_item)
        
        response = FoodNutritionListResponse(
            foods=food_items,
            total=result.total,
            page=result.page,
            limit=result.limit,
            pages=result.pages
        )
        
        logger.info(
            f"User retrieved food nutrition list",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "page": page,
                "limit": limit,
                "total_entries": result.total,
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return response
    except Exception as e:
        logger.error(f"Error retrieving food nutrition list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving food nutrition list",
        )

@router.get("/{entry_id}", response_model=FoodNutrition)
def get_nutrition_entry(
    entry_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific food nutrition entry by ID
    """
    entry = get_food_nutrition_by_id(db, entry_id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food nutrition entry not found",
        )
    
    # Check if the entry belongs to the current user (unless admin)
    if entry.user_id != current_user.id and current_user.role != "admin":
        logger.warning(
            f"User attempted to access another user's food nutrition entry",
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
        f"User retrieved food nutrition entry",
        extra={
            "user_id": current_user.id,
            "username": current_user.username,
            "entry_id": entry_id,
            "client_ip": request.client.host if request.client else None,
        }
    )
    
    return entry

@router.put("/{entry_id}", response_model=FoodNutrition)
def update_nutrition_entry(
    entry_id: int,
    update_data: FoodNutritionUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a food nutrition entry
    """
    # First check if the entry exists and belongs to the user
    entry = get_food_nutrition_by_id(db, entry_id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food nutrition entry not found",
        )
    
    # Check if the entry belongs to the current user (unless admin)
    if entry.user_id != current_user.id and current_user.role != "admin":
        logger.warning(
            f"User attempted to update another user's food nutrition entry",
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
        updated_entry = update_food_nutrition(db, entry_id, update_data)
        
        if not updated_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food nutrition entry not found",
            )
        
        logger.info(
            f"User updated food nutrition entry",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "entry_id": entry_id,
                "fields_updated": list(update_data.dict(exclude_unset=True).keys()),
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return updated_entry
    except FoodNutritionServiceError as e:
        if "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        logger.error(f"Error updating food nutrition entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating food nutrition entry",
        )
    except Exception as e:
        logger.error(f"Unexpected error updating food nutrition entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nutrition_entry(
    entry_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a food nutrition entry
    """
    # First check if the entry exists and belongs to the user
    entry = get_food_nutrition_by_id(db, entry_id)
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food nutrition entry not found",
        )
    
    # Check if the entry belongs to the current user (unless admin)
    if entry.user_id != current_user.id and current_user.role != "admin":
        logger.warning(
            f"User attempted to delete another user's food nutrition entry",
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
        success = delete_food_nutrition(db, entry_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food nutrition entry not found",
            )
        
        logger.info(
            f"User deleted food nutrition entry",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "entry_id": entry_id,
                "client_ip": request.client.host if request.client else None,
            }
        )
        
        return None
    except FoodNutritionServiceError as e:
        logger.error(f"Error deleting food nutrition entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting food nutrition entry",
        )
    except Exception as e:
        logger.error(f"Unexpected error deleting food nutrition entry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )