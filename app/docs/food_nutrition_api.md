# Food Nutrition API Documentation

This document describes the API endpoints for managing food nutrition data in the DietGeniusAI application.

## Models

### MealType Enum

Represents the type of meal:

- `breakfast`
- `lunch`
- `dinner`
- `snack`
- `brunch`
- `supper`
- `other`

### FoodNutrition Model

Represents a food nutrition entry with the following fields:

- `id`: Unique identifier for the entry
- `user_id`: ID of the user who created the entry
- `food_name`: Name of the food item
- `serving_size`: Serving size as specified by the user (e.g., "2 chicken wings", "1 bowl")
- `meal_type`: Type of meal (breakfast, lunch, dinner, snack, etc.)
- `nutrition_data`: JSON object containing nutritional information
- `consumed_at`: Timestamp when the food was consumed
- `created_at`: Timestamp when the entry was created
- `updated_at`: Timestamp when the entry was last updated

## API Endpoints

### Create Food Nutrition Entry

**POST** `/api/food-nutrition/`

Creates a new food nutrition entry for the authenticated user.

**Request Body:**
```json
{
  "food_name": "Grilled Chicken Breast",
  "serving_size": "1 piece (100g)",
  "meal_type": "dinner",
  "nutrition_data": {
    "calories": {"value": 165, "unit": "kcal"},
    "protein": {"value": 31, "unit": "g"},
    "carbs": {"value": 0, "unit": "g"},
    "fat": {"value": 3.6, "unit": "g"}
  },
  "consumed_at": "2025-07-14T18:30:00Z"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 123,
  "food_name": "Grilled Chicken Breast",
  "serving_size": "1 piece (100g)",
  "meal_type": "dinner",
  "nutrition_data": {
    "calories": {"value": 165, "unit": "kcal"},
    "protein": {"value": 31, "unit": "g"},
    "carbs": {"value": 0, "unit": "g"},
    "fat": {"value": 3.6, "unit": "g"}
  },
  "consumed_at": "2025-07-14T18:30:00Z",
  "created_at": "2025-07-14T12:45:00Z",
  "updated_at": null
}
```

**Status Codes:**
- `201 Created`: Entry created successfully
- `409 Conflict`: Entry already exists (duplicate)
- `500 Internal Server Error`: Server error

### Get Food Nutrition Entries

**GET** `/api/food-nutrition/`

Retrieves paginated food nutrition entries for the authenticated user.

**Query Parameters:**
- `meal_type` (optional): Filter by meal type
- `start_date` (optional): Filter by start date (ISO format)
- `end_date` (optional): Filter by end date (ISO format)
- `page` (optional, default=1): Page number
- `limit` (optional, default=10): Items per page

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 123,
      "food_name": "Grilled Chicken Breast",
      "serving_size": "1 piece (100g)",
      "meal_type": "dinner",
      "nutrition_data": {
        "calories": {"value": 165, "unit": "kcal"},
        "protein": {"value": 31, "unit": "g"},
        "carbs": {"value": 0, "unit": "g"},
        "fat": {"value": 3.6, "unit": "g"}
      },
      "consumed_at": "2025-07-14T18:30:00Z",
      "created_at": "2025-07-14T12:45:00Z",
      "updated_at": null
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10,
  "pages": 1
}
```

**Status Codes:**
- `200 OK`: Entries retrieved successfully
- `500 Internal Server Error`: Server error

### Get Food Nutrition Entry by ID

**GET** `/api/food-nutrition/{entry_id}`

Retrieves a specific food nutrition entry by ID.

**Path Parameters:**
- `entry_id`: ID of the entry to retrieve

**Response:**
```json
{
  "id": 1,
  "user_id": 123,
  "food_name": "Grilled Chicken Breast",
  "serving_size": "1 piece (100g)",
  "meal_type": "dinner",
  "nutrition_data": {
    "calories": {"value": 165, "unit": "kcal"},
    "protein": {"value": 31, "unit": "g"},
    "carbs": {"value": 0, "unit": "g"},
    "fat": {"value": 3.6, "unit": "g"}
  },
  "consumed_at": "2025-07-14T18:30:00Z",
  "created_at": "2025-07-14T12:45:00Z",
  "updated_at": null
}
```

**Status Codes:**
- `200 OK`: Entry retrieved successfully
- `404 Not Found`: Entry not found
- `403 Forbidden`: Not authorized to access this entry
- `500 Internal Server Error`: Server error

### Update Food Nutrition Entry

**PUT** `/api/food-nutrition/{entry_id}`

Updates a specific food nutrition entry.

**Path Parameters:**
- `entry_id`: ID of the entry to update

**Request Body:**
```json
{
  "food_name": "Grilled Chicken Breast",
  "serving_size": "2 pieces (200g)",
  "nutrition_data": {
    "calories": {"value": 330, "unit": "kcal"},
    "protein": {"value": 62, "unit": "g"},
    "carbs": {"value": 0, "unit": "g"},
    "fat": {"value": 7.2, "unit": "g"}
  }
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 123,
  "food_name": "Grilled Chicken Breast",
  "serving_size": "2 pieces (200g)",
  "meal_type": "dinner",
  "nutrition_data": {
    "calories": {"value": 330, "unit": "kcal"},
    "protein": {"value": 62, "unit": "g"},
    "carbs": {"value": 0, "unit": "g"},
    "fat": {"value": 7.2, "unit": "g"}
  },
  "consumed_at": "2025-07-14T18:30:00Z",
  "created_at": "2025-07-14T12:45:00Z",
  "updated_at": "2025-07-14T13:15:00Z"
}
```

**Status Codes:**
- `200 OK`: Entry updated successfully
- `404 Not Found`: Entry not found
- `403 Forbidden`: Not authorized to update this entry
- `409 Conflict`: Update would create a duplicate entry
- `500 Internal Server Error`: Server error

### Delete Food Nutrition Entry

**DELETE** `/api/food-nutrition/{entry_id}`

Deletes a specific food nutrition entry.

**Path Parameters:**
- `entry_id`: ID of the entry to delete

**Response:**
No content

**Status Codes:**
- `204 No Content`: Entry deleted successfully
- `404 Not Found`: Entry not found
- `403 Forbidden`: Not authorized to delete this entry
- `500 Internal Server Error`: Server error

## Duplicate Prevention

The API prevents duplicate entries by enforcing a unique constraint on the combination of:
- `user_id`
- `food_name`
- `serving_size`
- `meal_type`
- `consumed_at`

If a user attempts to create an entry that would violate this constraint, a `409 Conflict` error is returned.