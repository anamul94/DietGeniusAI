from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import datetime, date
import json
from fastapi import HTTPException, status

from app.models.food_nutrition import MealEntry, MealType
from app.schemas.meal_entry import MealEntryCreate, MealEntryUpdate
from app.schemas.nutrition import FoodNutritionList
from app.core.pagination import BasePaginator, PaginationResult
from app.core.logging import logger

class MealEntryServiceError(Exception):
    """Custom exception for meal entry service errors"""
    pass

class MealEntryPaginator(BasePaginator):
    """Paginator for meal entries"""
    
    def get_query(self, user_id: Optional[int] = None, meal_type: Optional[MealType] = None, 
                  start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        """Return the base query for pagination with optional filters"""
        query = self.db.query(MealEntry)
        
        # Apply filters if provided
        if user_id is not None:
            query = query.filter(MealEntry.user_id == user_id)
        
        if meal_type is not None:
            query = query.filter(MealEntry.meal_type == meal_type)
            
        if start_date is not None:
            query = query.filter(MealEntry.consumed_at >= start_date)
            
        if end_date is not None:
            query = query.filter(MealEntry.consumed_at <= end_date)
            
        # Order by consumed_at date (newest first)
        return query.order_by(MealEntry.consumed_at.desc())

def create_meal_entry(
    db: Session, 
    user_id: int, 
    meal_entry_data: MealEntryCreate
) -> MealEntry:
    """
    Create a new meal entry
    
    Args:
        db: Database session
        user_id: ID of the user creating the entry
        meal_entry_data: Meal entry data
        
    Returns:
        Created meal entry
        
    Raises:
        MealEntryServiceError: If entry already exists or other error occurs
    """
    try:
        # Convert FoodNutritionList to dict for JSON storage
        foods_dict = meal_entry_data.foods.dict()
        
        db_meal_entry = MealEntry(
            user_id=user_id,
            meal_type=meal_entry_data.meal_type,
            foods=foods_dict,
            consumed_at=meal_entry_data.consumed_at
        )
        
        db.add(db_meal_entry)
        db.commit()
        db.refresh(db_meal_entry)
        
        logger.info(
            f"Created meal entry",
            extra={
                "user_id": user_id,
                "meal_type": meal_entry_data.meal_type,
                "entry_id": db_meal_entry.id
            }
        )
        
        return db_meal_entry
        
    except IntegrityError:
        db.rollback()
        logger.warning(
            f"Duplicate meal entry detected",
            extra={
                "user_id": user_id,
                "meal_type": meal_entry_data.meal_type
            }
        )
        raise MealEntryServiceError("This meal entry already exists for this date")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating meal entry: {str(e)}")
        raise MealEntryServiceError(f"Error creating meal entry: {str(e)}")

def get_meal_entry_by_id(db: Session, entry_id: int) -> Optional[MealEntry]:
    """
    Get a meal entry by ID
    
    Args:
        db: Database session
        entry_id: ID of the entry to retrieve
        
    Returns:
        Meal entry if found, None otherwise
    """
    return db.query(MealEntry).filter(MealEntry.id == entry_id).first()

def check_meal_type_exists(
    db: Session,
    user_id: int,
    meal_type: MealType,
    check_date: date
) -> tuple[bool, Optional[MealEntry]]:
    """
    Check if a meal type already exists for a specific date
    
    Args:
        db: Database session
        user_id: User ID
        meal_type: Meal type to check
        check_date: Date to check
        
    Returns:
        Tuple of (exists, meal_entry)
    """
    # Convert date to datetime range for the entire day
    start_datetime = datetime.combine(check_date, datetime.min.time())
    end_datetime = datetime.combine(check_date, datetime.max.time())
    
    meal_entry = db.query(MealEntry).filter(
        MealEntry.user_id == user_id,
        MealEntry.meal_type == meal_type,
        MealEntry.consumed_at >= start_datetime,
        MealEntry.consumed_at <= end_datetime
    ).first()
    
    return (meal_entry is not None, meal_entry)

def get_meal_entries(
    db: Session,
    user_id: Optional[int] = None,
    meal_type: Optional[MealType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    limit: int = 10
) -> PaginationResult:
    """
    Get paginated meal entries with optional filters
    
    Args:
        db: Database session
        user_id: Optional filter by user ID
        meal_type: Optional filter by meal type
        start_date: Optional filter by start date
        end_date: Optional filter by end date
        page: Page number
        limit: Items per page
        
    Returns:
        Paginated result with meal entries
    """
    paginator = MealEntryPaginator(db)
    return paginator.paginate(
        page=page,
        limit=limit,
        user_id=user_id,
        meal_type=meal_type,
        start_date=start_date,
        end_date=end_date
    )

def update_meal_entry(
    db: Session,
    entry_id: int,
    update_data: MealEntryUpdate
) -> Optional[MealEntry]:
    """
    Update a meal entry
    
    Args:
        db: Database session
        entry_id: ID of the entry to update
        update_data: Data to update
        
    Returns:
        Updated meal entry if found, None otherwise
        
    Raises:
        MealEntryServiceError: If entry already exists or other error occurs
    """
    try:
        db_entry = db.query(MealEntry).filter(MealEntry.id == entry_id).first()
        
        if not db_entry:
            return None
            
        # Update fields if provided
        update_dict = update_data.dict(exclude_unset=True)
        
        # Special handling for foods field
        if 'foods' in update_dict:
            update_dict['foods'] = update_dict['foods'].dict()
            
        for field, value in update_dict.items():
            setattr(db_entry, field, value)
            
        db.commit()
        db.refresh(db_entry)
        
        logger.info(
            f"Updated meal entry",
            extra={
                "entry_id": entry_id,
                "user_id": db_entry.user_id,
                "fields_updated": list(update_dict.keys())
            }
        )
        
        return db_entry
        
    except IntegrityError:
        db.rollback()
        logger.warning(
            f"Duplicate meal entry detected during update",
            extra={"entry_id": entry_id}
        )
        raise MealEntryServiceError("This update would create a duplicate entry")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating meal entry: {str(e)}")
        raise MealEntryServiceError(f"Error updating meal entry: {str(e)}")

def delete_meal_entry(db: Session, entry_id: int) -> bool:
    """
    Delete a meal entry
    
    Args:
        db: Database session
        entry_id: ID of the entry to delete
        
    Returns:
        True if deleted, False if not found
    """
    db_entry = db.query(MealEntry).filter(MealEntry.id == entry_id).first()
    
    if not db_entry:
        return False
        
    try:
        db.delete(db_entry)
        db.commit()
        
        logger.info(
            f"Deleted meal entry",
            extra={
                "entry_id": entry_id,
                "user_id": db_entry.user_id
            }
        )
        
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting meal entry: {str(e)}")
        raise MealEntryServiceError(f"Error deleting meal entry: {str(e)}")