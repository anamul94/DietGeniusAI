from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.food_nutrition import MealType
from app.schemas.meal_entry import (
    MealEntry, 
    MealEntryCreate, 
    MealEntryUpdate,
    MealEntryPagination,
    MealTypeCheck
)
from app.services.meal_entry import (
    create_meal_entry, 
    get_meal_entry_by_id, 
    get_meal_entries,
    update_meal_entry,
    delete_meal_entry,
    check_meal_type_exists,
    MealEntryServiceError
)
from app.core.logging import logger

router = APIRouter()

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
                "fields_updated": list(update_data.dict(exclude_unset=True).keys()),
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