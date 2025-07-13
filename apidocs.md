# DietGeniusAI API Documentation

This document provides an overview of the DietGeniusAI API endpoints, their methods, request/response schemas, and functionality.

## Authentication

### Login with Username/Password

Authenticate user with username and password to get access token.

- **URL**: `/api/auth/login`
- **Method**: `POST`
- **Request Body**: `application/x-www-form-urlencoded`
    - `username`: `string` - User email or username
    - `password`: `string` - User password
- **Response**:
    - **Status**: `200 OK`
    - **Body**:
        ```json
        {
            "access_token": "string",
            "token_type": "bearer"
        }
        ```
    - **Error Responses**:
        - `401 Unauthorized`: Incorrect username or password.
        - `500 Internal Server Error`: Authentication service error.

### Google OAuth Login

Initiate Google OAuth login flow.

- **URL**: `/api/auth/google-login`
- **Method**: `GET`
- **Response**: Redirects to Google OAuth consent screen

### Google OAuth Callback

Handles Google OAuth callback and returns access token.

- **URL**: `/api/auth/google/callback`
- **Method**: `GET`
- **Query Parameters**: (Handled automatically by OAuth flow)
- **Response**:
    - **Status**: `200 OK`
    - **Body**:
        ```json
        {
            "access_token": "string",
            "token_type": "bearer",
            "user_info": {
                "id": "integer",
                "email": "string",
                "username": "string",
                "role": "string",
                "avatar": "string (optional)",
                "is_active": "boolean",
                "onboarding_status": "string (PENDING or COMPLETED)"
            }
        }
        ```
    - **Error Responses**:
        - `400 Bad Request`: OAuth error or invalid request.
        - `500 Internal Server Error`: Authentication failed.

## Medical Reports

### Upload Medical Report

Uploads one or more medical report files for processing.

- **URL**: `/api/medical-reports/medical`
- **Method**: `POST`
- **Authentication**: Required (User)
- **Request**:
    - **Headers**: `Content-Type: multipart/form-data`
    - **Body**:
        - `files`: List of `UploadFile` (PDF, DOC, DOCX, TXT, MD, JPG, JPEG, PNG, WEBP). Maximum 3 files.
- **Response**:
    - **Status**: `200 OK`
    - **Body**:
        ```json
        {
            "id": "string (UUID)",
            "processing_status": "completed",
            "data": {
                // Processed medical report data
            }
        }
        ```
    - **Error Responses**:
        - `400 Bad Request`: No files provided, too many files, or invalid file type.
        - `500 Internal Server Error`: Failed to process medical report.

### Get Medical Reports

Retrieves paginated medical reports for the current user, sorted by date (newest first).

- **URL**: `/api/medical-reports/medical`
- **Method**: `GET`
- **Authentication**: Required (User)
- **Query Parameters**:
    - `page`: `integer` (default: 1, min: 1) - Page number.
    - `limit`: `integer` (default: 10, min: 1, max: 100) - Items per page.
- **Response**:
    - **Status**: `200 OK`
    - **Body**:
        ```json
        {
            "data": [
                {
                    "id": "string (UUID)",
                    "medical_report": {
                        // Medical report data
                    },
                    "uploaded_at": "string (datetime)"
                }
            ],
            "pagination": {
                "page": "integer",
                "limit": "integer",
                "total": "integer",
                "pages": "integer"
            }
        }
        ```
    - **Error Responses**:
        - `500 Internal Server Error`: Failed to fetch medical reports.

### Onboarding QA

Processes user answers for onboarding questions and generates the next question. Conducts 4-round assessment and automatically updates user onboarding status to COMPLETED after final round.

- **URL**: `/api/medical-reports/onboarding-qa`
- **Method**: `POST`
- **Authentication**: Required (User)
- **Request Body**: `application/json`
    ```json
    {
        "answer": "string",
        "count": "integer (0-3)",
        "chat_history": [
            {
                "question": "string",
                "answer": "string"
            }
        ]
    }
    ```
- **Response**:
    - **Status**: `200 OK`
    - **Body**:
        ```json
        {
            "question": "string",
            "count": "integer (1-4)",
            "chat_history": [
                {
                    "question": "string",
                    "answer": "string"
                }
            ]
        }
        ```
    - **Notes**:
        - Round 1-3: Assessment questions
        - Round 4: Final summary with completion message
        - User onboarding_status automatically updated to COMPLETED after round 4
    - **Error Responses**:
        - `500 Internal Server Error`: Failed to process onboarding QA.

### Memory Test

Tests the agent's memory by processing a message.

- **URL**: `/api/medical-reports/memory-test`
- **Method**: `POST`
- **Authentication**: Required (User)
- **Request Body**: `application/json`
    ```json
    {
        "message": "string"
    }
    ```
- **Response**:
    - **Status**: `200 OK`
    - **Body**: (Varies based on agent's response)
- **Error Responses**:
    - `500 Internal Server Error`: Failed to process memory test.

## Users

### Get Current User

Retrieves the profile information of the currently authenticated user.

- **URL**: `/api/users/me`
- **Method**: `GET`
- **Authentication**: Required (User)
- **Response**:
    - **Status**: `200 OK`
    - **Body**:
        ```json
        {
            "email": "string (email)",
            "username": "string",
            "avatar": "string (optional)",
            "gender": "string (optional)",
            "dob": "string (date, YYYY-MM-DD, optional)",
            "phone": "string (optional)",
            "address": "string (optional)",
            "city": "string (optional)",
            "country": "string (optional)",
            "postal_code": "string (optional)",
            "timezone": "string (optional)",
            "profession": "string (optional)",
            "id": "integer",
            "is_active": "boolean",
            "role": "string (USER or ADMIN)",
            "onboarding_status": "string (PENDING or COMPLETED)",
            "created_at": "string (datetime)",
            "updated_at": "string (datetime, optional)",
            "age": "integer (computed, optional)"
        }
        ```

### Update Current User

Updates the profile information of the currently authenticated user.

- **URL**: `/api/users/me`
- **Method**: `PUT`
- **Authentication**: Required (User)
- **Request Body**: `application/json`
    ```json
    {
        "email": "string (email, optional)",
        "username": "string (optional)",
        "password": "string (optional)",
        "role": "string (optional, only modifiable by ADMIN)",
        "avatar": "string (optional)",
        "gender": "string (optional)",
        "dob": "string (date, YYYY-MM-DD, optional)",
        "phone": "string (optional)",
        "address": "string (optional)",
        "city": "string (optional)",
        "country": "string (optional)",
        "postal_code": "string (optional)",
        "timezone": "string (optional)",
        "profession": "string (optional)"
    }
    ```
- **Response**:
    - **Status**: `200 OK`
    - **Body**: (Same as Get Current User response)
    - **Error Responses**:
        - `400 Bad Request`: If email/username already registered or other validation errors.
        - `500 Internal Server Error`: Error updating user.

### Get All Users (Admin Only)

Retrieves a list of all users. This endpoint is restricted to admin users.

- **URL**: `/api/users/all`
- **Method**: `GET`
- **Authentication**: Required (Admin)
- **Query Parameters**:
    - `skip`: `integer` (default: 0) - Number of items to skip.
    - `limit`: `integer` (default: 100) - Maximum number of items to return.
- **Response**:
    - **Status**: `200 OK`
    - **Body**: `array` of User objects (Same as Get Current User response)
    - **Error Responses**:
        - `403 Forbidden`: If the authenticated user is not an admin.
        - `500 Internal Server Error`: Error retrieving users.

### Update User Profile Information

Updates specific profile information for the current user.

- **URL**: `/api/users/profile`
- **Method**: `PUT`
- **Authentication**: Required (User)
- **Request Body**: `application/json`
    ```json
    {
        "gender": "string (optional)",
        "dob": "string (date, YYYY-MM-DD, optional)",
        "phone": "string (optional)",
        "address": "string (optional)",
        "city": "string (optional)",
        "country": "string (optional)",
        "postal_code": "string (optional)",
        "timezone": "string (optional)",
        "profession": "string (optional)"
    }
    ```
- **Response**:
    - **Status**: `200 OK`
    - **Body**: (Same as Get Current User response)
    - **Error Responses**:
        - `500 Internal Server Error`: Error updating profile.
