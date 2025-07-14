# Google Health API Integration

This document provides instructions on how to set up and use the Google Health API integration in the DietGeniusAI application.

## Overview

The Google Health API integration allows users to connect their Google Fit accounts to the application and sync their health data. The integration includes:

1. Authentication with Google Health API
2. Fetching health data from Google Health API
3. Storing health data in the database
4. Daily automatic sync of health data

## Setup Instructions

### 1. Google Cloud Console Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Fitness API for your project
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Web application" as the application type
   - Add authorized redirect URIs:
     - `https://your-domain.com/api/google-health/auth/callback` (production)
     - `http://localhost:8000/api/google-health/auth/callback` (development)
   - Click "Create"
   - Note the Client ID and Client Secret

### 2. Environment Variables

Add the following environment variables to your `.env` file:

```
GOOGLE_HEALTH_CLIENT_ID=your_client_id
GOOGLE_HEALTH_CLIENT_SECRET=your_client_secret
GOOGLE_HEALTH_REDIRECT_URI=http://localhost:8000/api/google-health/auth/callback
GOOGLE_HEALTH_API_URL=https://www.googleapis.com/fitness/v1
GOOGLE_HEALTH_SCOPES=https://www.googleapis.com/auth/fitness.activity.read https://www.googleapis.com/auth/fitness.body.read https://www.googleapis.com/auth/fitness.nutrition.read https://www.googleapis.com/auth/fitness.sleep.read
```

**Note about Heart Rate Data**: If you need heart rate data, you must add the `https://www.googleapis.com/auth/fitness.heart_rate.read` scope to the `GOOGLE_HEALTH_SCOPES` variable. However, this scope requires special verification from Google, and your application must go through the OAuth verification process to request this sensitive scope.

### 3. Database Migrations

Run the database migrations to create the necessary tables:

```bash
alembic revision --autogenerate -m "Add Google Health models"
alembic upgrade head
```

### 4. Cron Job Setup

Set up a cron job to run the daily sync script at 12 AM:

```bash
crontab -e
```

Add the following line:

```
0 0 * * * /path/to/python /path/to/app/cron/google_health_sync.py
```

## API Endpoints

### Authentication

#### Get Authorization URL

```
GET /api/google-health/auth-url
```

Returns the Google Health authorization URL that the user should be redirected to.

#### Handle Authorization Callback

The authorization callback flow works in two steps:

1. Google redirects to your callback URL with the authorization code (GET endpoint)
2. Your frontend captures the code and sends it to the backend (POST endpoint)

##### GET Callback (from Google OAuth)

```
GET /api/google-health/auth/callback?code=authorization_code_from_google
```

This endpoint is called by Google OAuth after user authorization. It automatically redirects the user's browser to your frontend application with the authorization code as a query parameter.

##### POST Callback (from Frontend)

```
POST /api/google-health/auth/callback
```

Body:
```json
{
  "code": "authorization_code_from_google",
  "redirect_uri": "http://localhost:8000/api/google-health/auth/callback"
}
```

**IMPORTANT**: The `redirect_uri` must exactly match the one registered in Google Cloud Console and used in the initial authorization request. The backend will use the URI from settings rather than the one provided in the request for security reasons.

This endpoint is called by your frontend after receiving the code from the GET callback. It exchanges the authorization code for access and refresh tokens.

##### Frontend Implementation Example

```javascript
// Example frontend code for handling the callback
async function handleGoogleHealthCallback() {
  // Get the code from URL query parameters
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  
  if (!code) {
    console.error('No authorization code found');
    return;
  }
  
  try {
    // Call your backend API to exchange the code for tokens
    const response = await fetch('/api/google-health/auth/callback', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_USER_ACCESS_TOKEN' // Include user authentication
      },
      body: JSON.stringify({
        code: code,
        redirect_uri: 'http://localhost:8000/api/google-health/auth/callback' // Must match the one in your settings
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`Failed to exchange code: ${errorData.detail || 'Unknown error'}`);
    }
    
    const tokenData = await response.json();
    console.log('Successfully connected Google Health account');
    
    // Redirect to a success page or dashboard
    window.location.href = '/dashboard?google_health_connected=true';
    
  } catch (error) {
    console.error('Error exchanging code for token:', error);
    // Handle error (show error message to user)
  }
}

// Call this function when the page loads
document.addEventListener('DOMContentLoaded', handleGoogleHealthCallback);
```

##### Testing with curl

You can test the POST endpoint with curl:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/google-health/auth/callback' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -d '{
  "code": "YOUR_AUTHORIZATION_CODE"
}'
```

Note that you don't need to include the `redirect_uri` in the request anymore, as the backend will use the one from settings.

### Data Management

#### Fetch Health Data

```
POST /api/google-health/data/fetch
```

Body:
```json
{
  "data_types": ["steps", "heart_rate", "sleep", "weight", "nutrition"],
  "start_date": "2023-01-01T00:00:00Z",
  "end_date": "2023-01-02T00:00:00Z"
}
```

Fetches health data from Google Health API for the specified time range.

#### Get Health Data

```
GET /api/google-health/data?data_type=steps&start_date=2023-01-01T00:00:00Z&end_date=2023-01-02T00:00:00Z
```

Gets health data from the database for the specified time range.

#### Check Connection Status

```
GET /api/google-health/status
```

Checks if the user has connected their Google Health account and returns:
- Connection status
- Token expiration time
- List of granted scopes

#### Revoke Access

```
POST /api/google-health/revoke
```

Revokes the Google Health access token and removes it from the database. This endpoint is useful when a user wants to disconnect their Google Health account from your application.

## Implementation Details

### Data Types

The following data types are supported:

- `steps`: Step count
- `heart_rate`: Heart rate measurements
- `sleep`: Sleep segments
- `weight`: Weight measurements
- `nutrition`: Nutrition information

### Duplicate Data Handling

The system automatically checks for duplicate data when saving to the database. Duplicate data is identified by:

- User ID
- Data type
- Start time
- End time

### Token Refresh

Access tokens are automatically refreshed when they expire or are about to expire (within 5 minutes).

## Troubleshooting

### Common Issues

1. **Authorization Error**: Make sure the redirect URI in your code matches exactly with the one registered in the Google Cloud Console.

2. **Scope Error**: Ensure that all required scopes are included in the authorization URL.

3. **Token Refresh Error**: If token refresh fails, the user may need to re-authorize the application.

4. **Data Not Syncing**: Check the cron job logs at `/var/log/google_health_sync.log` for errors.

5. **"invalid_grant" Error**: This error occurs when:
   - The authorization code has already been used (they're one-time use only)
   - The authorization code has expired (they typically expire after 10 minutes)
   - The redirect URI in the token request doesn't match the one used in the authorization request

   **Solution**: Always start the OAuth flow from the beginning when testing. Don't try to reuse authorization codes.

### Testing the OAuth Flow

When testing the OAuth flow, keep these important points in mind:

1. **Authorization codes are one-time use only**: Once you use a code to get tokens, you cannot use it again. If you get an "invalid_grant" error, you need to start the OAuth flow from the beginning.

2. **Authorization codes expire quickly**: Codes typically expire after 10 minutes. If you wait too long to exchange the code for tokens, you'll get an "invalid_grant" error.

3. **Redirect URIs must match exactly**: The redirect URI used in the token exchange request must exactly match the one used in the authorization request and the one registered in the Google Cloud Console.

4. **Testing workflow**:
   - Start by visiting the auth URL endpoint to get a fresh authorization URL
   - Complete the Google OAuth consent flow
   - Let the system redirect you to your frontend
   - Have your frontend immediately exchange the code for tokens

5. **403 Forbidden Error when Fetching Data**: If you encounter a 403 Forbidden error when trying to fetch health data, check:
   - That you've enabled the Fitness API in your Google Cloud Console project
   - That the user has granted all the requested scopes during the consent screen
   - That the scopes in your token match the ones required for the data you're trying to access
   - That you're using the correct API endpoint for the data type

   **Solution**:
   - Verify the Fitness API is enabled in your Google Cloud Console
   - Make sure to request all necessary scopes in your authorization URL
   - Check the logs to see which scopes were actually granted
   - Try re-authorizing with the user to ensure all scopes are granted
   - If using specific data types like steps, ensure you're using the correct dataSourceId

   **Required Scopes for Different Data Types**:
   - Steps: `https://www.googleapis.com/auth/fitness.activity.read`
   - Heart Rate: `https://www.googleapis.com/auth/fitness.heart_rate.read`
   - Sleep: `https://www.googleapis.com/auth/fitness.sleep.read`
   - Weight: `https://www.googleapis.com/auth/fitness.body.read`
   - Nutrition: `https://www.googleapis.com/auth/fitness.nutrition.read`
   
   **Google Consent Screen Options**:
   
   When users authorize your application, they will see these options on the Google consent screen:
   
   1. "See your sleep data in Google Fit" - Grants `fitness.sleep.read` scope
   2. "See info about your nutrition in Google Fit" - Grants `fitness.nutrition.read` scope
   3. "See info about your body measurements in Google Fit" - Grants `fitness.body.read` scope
   4. "Use Google Fit to see and store your physical activity data" - Grants `fitness.activity.read` scope
   
   **IMPORTANT**: The heart rate permission (`fitness.heart_rate.read`) requires special verification from Google. If you need heart rate data, you must complete the Google OAuth verification process and request this sensitive scope specifically. Without this verification, the heart rate permission option won't appear on the consent screen, and your application won't be able to access heart rate data.

   **Common API Endpoints**:
   - Aggregate data (steps, heart rate, weight, sleep): `/users/me/dataset:aggregate`
   - Datasets (nutrition): `/users/me/dataSources/{dataSourceId}/datasets/{startTimeMillis}-{endTimeMillis}`
   
   **Note**: Initially we tried using the `/users/me/sessions` endpoint for sleep data, but it returns a 404 Not Found error. We now use the dataset:aggregate endpoint for sleep data as well.

### Logging

Logs for the Google Health integration can be found in:

- Application logs for API requests
- `/var/log/google_health_sync.log` for the cron job

## Security Considerations

- Access tokens are stored in the database and should be encrypted at rest
- All API endpoints require user authentication
- The application only requests the minimum required scopes
- Tokens are refreshed securely using the refresh token flow