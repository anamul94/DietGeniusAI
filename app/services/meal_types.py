from typing import List, Dict, Any
from app.models.food_nutrition import MealType
from app.schemas.meal_types import MealTypeInfo, MealTypesResponse


def get_all_meal_types() -> List[MealTypeInfo]:
    """
    Get all available meal types as a list of MealTypeInfo objects
    
    Returns:
        List of MealTypeInfo objects containing value and label
    """
    meal_types = []
    
    for meal_type in MealType:
        meal_types.append(MealTypeInfo(
            value=meal_type.value,
            label=meal_type.value.title()
        ))
    
    return meal_types


def get_meal_types_response() -> MealTypesResponse:
    """
    Get meal types as a structured response object
    
    Returns:
        MealTypesResponse object with meal types and count
    """
    meal_types = get_all_meal_types()
    
    return MealTypesResponse(
        meal_types=meal_types,
        total_count=len(meal_types)
    )


def get_meal_types_dict() -> Dict[str, Any]:
    """
    Get meal types as a simple dictionary
    
    Returns:
        Dictionary with 'values' and 'labels' keys
    """
    return {
        "values": [meal_type.value for meal_type in MealType],
        "labels": [meal_type.value.title() for meal_type in MealType]
    }


def is_valid_meal_type(meal_type_value: str) -> bool:
    """
    Check if a given string is a valid meal type
    
    Args:
        meal_type_value: String value to check
        
    Returns:
        True if valid meal type, False otherwise
    """
    try:
        MealType(meal_type_value.lower())
        return True
    except ValueError:
        return False


def get_meal_type_label(meal_type_value: str) -> str:
    """
    Get the display label for a meal type value
    
    Args:
        meal_type_value: The meal type value (e.g., 'breakfast')
        
    Returns:
        Display label (e.g., 'Breakfast') or the original value if invalid
    """
    try:
        meal_type = MealType(meal_type_value.lower())
        return meal_type.value.title()
    except ValueError:
        return meal_type_value.title()