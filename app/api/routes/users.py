from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
import random
import string

from app.api.deps import get_db, get_current_user, get_current_admin_user
from app.models.user import User, UserRole, DietaryPreference, JoiningPurpose
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.schemas.profile import ProfileUpdate, DietaryPreferenceList, JoiningPurposeList
from app.services.user import create_user, get_user_by_email, get_user_by_username, get_user, update_user, get_users, UserServiceError
from app.core.logging import logger

router = APIRouter()

@router.get("/dietary-preferences", response_model=DietaryPreferenceList)
def get_dietary_preferences():
    """
    Get list of all dietary preferences
    """
    return DietaryPreferenceList()

@router.get("/joining-purposes", response_model=JoiningPurposeList)
def get_joining_purposes():
    """
    Get list of all purposes for joining
    """
    return JoiningPurposeList()

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_in: UserCreate, 
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Create new user
    """
    try:
        user = create_user(db, user_in)
        logger.info(
            f"New user registered",
            extra={
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "client_ip": request.client.host if request.client else None,
            }
        )
        return user
    except UserServiceError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user",
        )
    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.get("/me", response_model=UserSchema)
def read_user_me(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Get current user
    """
    logger.info(
        f"User retrieved own profile",
        extra={
            "user_id": current_user.id,
            "username": current_user.username,
            "client_ip": request.client.host if request.client else None,
        }
    )
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user_me(
    user_in: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update own user
    """
    try:
        # Prevent regular users from changing their role
        if user_in.role is not None and current_user.role != UserRole.ADMIN:
            user_in.role = current_user.role
            logger.warning(
                f"User attempted to change their role",
                extra={
                    "user_id": current_user.id,
                    "username": current_user.username,
                    "client_ip": request.client.host if request.client else None,
                }
            )
            
        user = update_user(db, current_user, user_in)
        logger.info(
            f"User updated own profile",
            extra={
                "user_id": user.id,
                "username": user.username,
                "client_ip": request.client.host if request.client else None,
                "fields_updated": list(user_in.dict(exclude_unset=True).keys()),
            }
        )
        return user
    except UserServiceError as e:
        if "already registered" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user",
        )
    except Exception as e:
        logger.error(f"Unexpected error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.get("/all", response_model=List[UserSchema])
def read_all_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Get all users (admin only)
    """
    try:
        users = get_users(db, skip=skip, limit=limit)
        logger.info(
            f"Admin retrieved all users",
            extra={
                "admin_id": current_user.id,
                "admin_username": current_user.username,
                "user_count": len(users),
                "client_ip": request.client.host if request.client else None,
            }
        )
        return users
    except Exception as e:
        logger.error(f"Error retrieving all users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users",
        )

@router.put("/profile", response_model=UserSchema)
def update_user_profile(
    profile_in: ProfileUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update user profile information
    """
    try:
        # Convert ProfileUpdate to UserUpdate
        update_data = profile_in.dict(exclude_unset=True)
        
        # Calculate BMI if height and weight are provided
        if profile_in.height and profile_in.weight:
            height_m = profile_in.height / 100  # Convert cm to m
            bmi = profile_in.weight / (height_m * height_m)
            update_data['bmi'] = round(bmi, 2)
            
        user_update = UserUpdate(**update_data)
        user = update_user(db, current_user, user_update)
        
        logger.info(
            f"User updated profile",
            extra={
                "user_id": user.id,
                "username": user.username,
                "client_ip": request.client.host if request.client else None,
                "fields_updated": list(update_data.keys()),
            }
        )
        return user
    except UserServiceError as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating profile",
        )
    except Exception as e:
        logger.error(f"Unexpected error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )

@router.post("/randomize", response_model=UserSchema)
def randomize_user_info(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update current user's email and username to random values
    """
    try:
        # Generate random username (8 characters)
        random_username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        # Generate random email
        random_email = f"{random_username}@example.com"
        
        # Create update data
        user_update = UserUpdate(
            username=random_username,
            email=random_email
        )
        
        # Update user
        user = update_user(db, current_user, user_update)
        
        logger.info(
            f"User randomized their info",
            extra={
                "user_id": user.id,
                "old_username": current_user.username,
                "new_username": user.username,
                "client_ip": request.client.host if request.client else None,
            }
        )
        return user
        
    except UserServiceError as e:
        logger.error(f"Error randomizing user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user information",
        )
    except Exception as e:
        logger.error(f"Unexpected error randomizing user info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )