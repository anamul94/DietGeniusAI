from textwrap import dedent
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import datetime, date
import json
from fastapi import HTTPException, status
from app.models.user import User
from app.models.food_nutrition import MealEntry, MealType
from app.schemas.meal_entry import MealEntryCreate, MealEntryUpdate
from app.schemas.nutrition import FoodNutritionList
from app.core.pagination import BasePaginator, PaginationResult
from app.core.logging import logger
from app.agents.agetns import meal_plan_agent
from app.services.user import get_user
from app.api.deps import get_db
from app.utils.age_calculator import calculate_age

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
        foods_dict = meal_entry_data.foods.model_dump()
        
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
            update_dict['foods'] = update_dict['foods'].model_dump()
            
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

def save_nutrition_data_to_meal_entry(
    db: Session,
    user_id: int,
    meal_type: str,
    consumed_at: str,
    nutrition_data: list,
    message: str = ""
) -> Optional[MealEntry]:
    """
    Save nutrition data to meal entry table
    
    Args:
        db: Database session
        user_id: User ID
        meal_type: Meal type as string
        consumed_at: Consumed at datetime as string
        nutrition_data: List of FoodNutrition objects from response
        message: Message from food response
        
    Returns:
        Created meal entry if successful, None if duplicate exists
        
    Raises:
        MealEntryServiceError: If error occurs during save
    """
    try:
        from datetime import datetime
        
        # Parse consumed_at string to datetime
        consumed_at_dt = datetime.fromisoformat(consumed_at)
        
        # Convert meal_type string to MealType enum
        meal_type_enum = MealType(meal_type.lower())
        
        # Check if entry already exists to avoid duplicates
        exists, existing_entry = check_meal_type_exists(
            db,
            user_id,
            meal_type_enum,
            consumed_at_dt.date()
        )
        
        if exists:
            logger.info(
                f"Nutrition data already exists for this meal and date, skipping save",
                extra={
                    "user_id": user_id,
                    "meal_type": meal_type,
                    "consumed_at": consumed_at,
                    "existing_entry_id": existing_entry.id if existing_entry else None
                }
            )
            return None
        
        # Convert FoodNutrition objects to dictionaries for JSON serialization
        foods_dict_list = []
        for food_item in nutrition_data:
            if hasattr(food_item, 'model_dump'):
                # If it's a Pydantic V2 model, use model_dump
                foods_dict_list.append(food_item.model_dump())
            elif hasattr(food_item, 'dict'):
                # If it's a Pydantic V1 model, use dict (for backward compatibility)
                foods_dict_list.append(food_item.dict())
            elif isinstance(food_item, dict):
                # If it's already a dict, use as is
                foods_dict_list.append(food_item)
            else:
                # Fallback: convert to dict manually
                foods_dict_list.append(dict(food_item))
        
        # Create foods data structure
        foods_data = {
            "foods": foods_dict_list,
            "message": message
        }
        
        # Create new meal entry
        new_entry = MealEntry(
            user_id=user_id,
            meal_type=meal_type_enum,
            foods=foods_data,
            consumed_at=consumed_at_dt
        )
        
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        
        logger.info(
            f"Saved nutrition data to database",
            extra={
                "user_id": user_id,
                "meal_type": meal_type,
                "consumed_at": consumed_at,
                "entry_id": new_entry.id
            }
        )
        
        return new_entry
        
    except ValueError as e:
        logger.error(f"Invalid meal type or datetime format: {str(e)}")
        raise MealEntryServiceError(f"Invalid meal type or datetime format: {str(e)}")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving nutrition data to database: {str(e)}")
        raise MealEntryServiceError(f"Error saving nutrition data to database: {str(e)}")


def get_meal_entries_by_date(
    db: Session,
    user_id: int,
    target_date: date
) -> List[MealEntry]:
    """
    Get all meal entries for a specific user and date
    
    Args:
        db: Database session
        user_id: User ID
        target_date: Target date to get meal data for
        
    Returns:
        List[MealEntry]: List of meal entries for the date
    """
    try:
        # Convert date to start and end of day for filtering
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        meal_entries = db.query(MealEntry).filter(
            MealEntry.user_id == user_id,
            MealEntry.consumed_at >= start_of_day,
            MealEntry.consumed_at <= end_of_day
        ).order_by(MealEntry.consumed_at).all()
        
        logger.info(
            f"Retrieved {len(meal_entries)} meal entries for user {user_id} on {target_date}"
        )
        
        return meal_entries
        
    except Exception as e:
        logger.error(f"Error getting meal entries by date: {str(e)}")
        raise MealEntryServiceError(f"Error getting meal entries by date: {str(e)}")
    
async def create_meal_plan(
    user_id: int,
    session_id: str,
):
    """
    Create a new meal plan for the user

    Args:
        user_id: User ID
        session_id: Session ID
    """
    db_generator = get_db()
    db = next(db_generator)
    try:
        user = get_user(db, user_id)
        logger.info(
            f"Creating meal plan for user {user.username} with session {session_id}"
        )
        today = datetime.now().date()
        meal_planner = meal_plan_agent()
        meal_plan = ""
        age = calculate_age(user.dob)
        message=f"""Generate a well defined meal plan for 7 days,
            user name: {user.username},
            gender: {user.gender},
            age: {age},
            profession:  {user.profession}
            country: {user.country},
            city:  {user.city},
            date: {today}"
          """
        logger.info(
            f"Meal plan message: {message}"
        )
        for chunk in meal_planner.run(
            message=message,
            user_id=user.id,
            stream=True,
        ):
            if chunk is not None:
                meal_plan += chunk.content
                print(chunk.content, end="", flush=True)
                
        return {
            "meal_plan": meal_plan,
        }
    finally:
        db.close()