from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status

from app.models.food_nutrition import FoodNutrition, MealType
from app.schemas.food_nutrition import FoodNutritionCreate, FoodNutritionUpdate
from app.core.pagination import BasePaginator, PaginationResult
from app.core.logging import logger

class FoodNutritionServiceError(Exception):
    """Custom exception for food nutrition service errors"""
    pass

class FoodNutritionPaginator(BasePaginator):
    """Paginator for food nutrition entries"""
    
    def get_query(self, user_id: Optional[int] = None, meal_type: Optional[MealType] = None, 
                  start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        """Return the base query for pagination with optional filters"""
        query = self.db.query(FoodNutrition)
        
        # Apply filters if provided
        if user_id is not None:
            query = query.filter(FoodNutrition.user_id == user_id)
        
        if meal_type is not None:
            query = query.filter(FoodNutrition.meal_type == meal_type)
            
        if start_date is not None:
            query = query.filter(FoodNutrition.consumed_at >= start_date)
            
        if end_date is not None:
            query = query.filter(FoodNutrition.consumed_at <= end_date)
            
        # Order by consumed_at date (newest first)
        return query.order_by(FoodNutrition.consumed_at.desc())

def create_food_nutrition(
    db: Session, 
    user_id: int, 
    food_nutrition_data: FoodNutritionCreate
) -> FoodNutrition:
    """
    Create a new food nutrition entry
    
    Args:
        db: Database session
        user_id: ID of the user creating the entry
        food_nutrition_data: Food nutrition data
        
    Returns:
        Created food nutrition entry
        
    Raises:
        FoodNutritionServiceError: If entry already exists or other error occurs
    """
    try:
        db_food_nutrition = FoodNutrition(
            user_id=user_id,
            food_name=food_nutrition_data.food_name,
            serving_size=food_nutrition_data.serving_size,
            meal_type=food_nutrition_data.meal_type,
            nutrition=food_nutrition_data.nutrition.dict(),
            consumed_at=food_nutrition_data.consumed_at
        )
        
        db.add(db_food_nutrition)
        db.commit()
        db.refresh(db_food_nutrition)
        
        logger.info(
            f"Created food nutrition entry",
            extra={
                "user_id": user_id,
                "food_name": food_nutrition_data.food_name,
                "meal_type": food_nutrition_data.meal_type,
                "entry_id": db_food_nutrition.id
            }
        )
        
        return db_food_nutrition
        
    except IntegrityError:
        db.rollback()
        logger.warning(
            f"Duplicate food nutrition entry detected",
            extra={
                "user_id": user_id,
                "food_name": food_nutrition_data.food_name,
                "meal_type": food_nutrition_data.meal_type
            }
        )
        raise FoodNutritionServiceError("This food nutrition entry already exists")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating food nutrition entry: {str(e)}")
        raise FoodNutritionServiceError(f"Error creating food nutrition entry: {str(e)}")

def get_food_nutrition_by_id(db: Session, entry_id: int) -> Optional[FoodNutrition]:
    """
    Get a food nutrition entry by ID
    
    Args:
        db: Database session
        entry_id: ID of the entry to retrieve
        
    Returns:
        Food nutrition entry if found, None otherwise
    """
    return db.query(FoodNutrition).filter(FoodNutrition.id == entry_id).first()

def get_food_nutrition_entries(
    db: Session,
    user_id: Optional[int] = None,
    meal_type: Optional[MealType] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    limit: int = 10
) -> PaginationResult:
    """
    Get paginated food nutrition entries with optional filters
    
    Args:
        db: Database session
        user_id: Optional filter by user ID
        meal_type: Optional filter by meal type
        start_date: Optional filter by start date
        end_date: Optional filter by end date
        page: Page number
        limit: Items per page
        
    Returns:
        Paginated result with food nutrition entries
    """
    paginator = FoodNutritionPaginator(db)
    return paginator.paginate(
        page=page,
        limit=limit,
        user_id=user_id,
        meal_type=meal_type,
        start_date=start_date,
        end_date=end_date
    )

def update_food_nutrition(
    db: Session,
    entry_id: int,
    update_data: FoodNutritionUpdate
) -> Optional[FoodNutrition]:
    """
    Update a food nutrition entry
    
    Args:
        db: Database session
        entry_id: ID of the entry to update
        update_data: Data to update
        
    Returns:
        Updated food nutrition entry if found, None otherwise
        
    Raises:
        FoodNutritionServiceError: If entry already exists or other error occurs
    """
    try:
        db_entry = db.query(FoodNutrition).filter(FoodNutrition.id == entry_id).first()
        
        if not db_entry:
            return None
            
        # Update fields if provided
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_entry, field, value)
            
        db.commit()
        db.refresh(db_entry)
        
        logger.info(
            f"Updated food nutrition entry",
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
            f"Duplicate food nutrition entry detected during update",
            extra={"entry_id": entry_id}
        )
        raise FoodNutritionServiceError("This update would create a duplicate entry")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating food nutrition entry: {str(e)}")
        raise FoodNutritionServiceError(f"Error updating food nutrition entry: {str(e)}")

def delete_food_nutrition(db: Session, entry_id: int) -> bool:
    """
    Delete a food nutrition entry
    
    Args:
        db: Database session
        entry_id: ID of the entry to delete
        
    Returns:
        True if deleted, False if not found
    """
    db_entry = db.query(FoodNutrition).filter(FoodNutrition.id == entry_id).first()
    
    if not db_entry:
        return False
        
    try:
        db.delete(db_entry)
        db.commit()
        
        logger.info(
            f"Deleted food nutrition entry",
            extra={
                "entry_id": entry_id,
                "user_id": db_entry.user_id
            }
        )
        
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting food nutrition entry: {str(e)}")
        raise FoodNutritionServiceError(f"Error deleting food nutrition entry: {str(e)}")