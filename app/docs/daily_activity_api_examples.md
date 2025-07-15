# Daily Activity Summary API Examples

This document provides practical examples of how to use the Daily Activity Summary API endpoints.

## Base URL
```
http://localhost:8000/api/daily-activity
```

## Authentication
All endpoints require authentication. Include your JWT token in the Authorization header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

## API Endpoints with Examples

### 1. Process Daily Health Data
**Endpoint:** `POST /process-daily-data/{target_date}`

**Description:** Fetch Google Health data for a specific date, process it, and save to daily activity summary table.

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/daily-activity/process-daily-data/2025-07-14" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

**Example Response:**
```json
[
  {
    "id": 1,
    "user_id": 123,
    "date_value": "2025-07-14",
    "datatype": "steps",
    "source": "Google Fit",
    "total_value": {
      "total_steps_count": 10000.0
    },
    "created_at": "2025-07-14T10:30:00Z",
    "updated_at": null
  },
  {
    "id": 2,
    "user_id": 123,
    "date_value": "2025-07-14",
    "datatype": "heart_rate",
    "source": "Google Fit",
    "total_value": {
      "average_heart_rate_bpm": 72.5
    },
    "created_at": "2025-07-14T10:30:00Z",
    "updated_at": null
  }
]
```

---

### 2. Preview Data Objects
**Endpoint:** `GET /preview-data/{target_date}`

**Description:** Preview how the raw Google Health data will be processed without saving to database.

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/daily-activity/preview-data/2025-07-14" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Example Response:**
```json
[
  {
    "datatype": "steps",
    "source": "Google Fit",
    "total_value": {
      "total_steps": 10000.0
    },
    "date_value": "2025-07-14"
  },
  {
    "datatype": "sleep",
    "source": "Google Fit",
    "total_value": {
      "total_sleep_minutes": 480.0,
      "sleep_stage_light_sleep_minutes": 240.0,
      "sleep_stage_deep_sleep_minutes": 120.0,
      "sleep_stage_rem_sleep_minutes": 120.0
    },
    "date_value": "2025-07-14"
  }
]
```

---

### 3. Get Daily Activity Summaries (with filters)
**Endpoint:** `GET /summaries`

**Description:** Retrieve daily activity summaries with optional date and data type filters.

**Example Requests:**

**Get all summaries:**
```bash
curl -X GET "http://localhost:8000/api/daily-activity/summaries" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Get steps data for July 2025:**
```bash
curl -X GET "http://localhost:8000/api/daily-activity/summaries?start_date=2025-07-01&end_date=2025-07-31&datatype=steps" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Get recent week data:**
```bash
curl -X GET "http://localhost:8000/api/daily-activity/summaries?start_date=2025-07-07" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Example Response:**
```json
[
  {
    "id": 1,
    "user_id": 123,
    "date_value": "2025-07-14",
    "datatype": "steps",
    "source": "Google Fit",
    "total_value": {
      "total_steps": 10000.0
    },
    "created_at": "2025-07-14T10:30:00Z",
    "updated_at": null
  },
  {
    "id": 2,
    "user_id": 123,
    "date_value": "2025-07-13",
    "datatype": "steps",
    "source": "Google Fit",
    "total_value": {
      "total_steps": 8500.0
    },
    "created_at": "2025-07-13T09:15:00Z",
    "updated_at": "2025-07-13T18:30:00Z"
  }
]
```

---

### 4. Get Summaries by Specific Date
**Endpoint:** `GET /summaries/{target_date}`

**Description:** Get all daily activity summaries for a specific date.

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/daily-activity/summaries/2025-07-14" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Example Response:**
```json
[
  {
    "id": 1,
    "user_id": 123,
    "date_value": "2025-07-14",
    "datatype": "steps",
    "source": "Google Fit",
    "total_value": {
      "total_steps": 10000.0
    },
    "created_at": "2025-07-14T10:30:00Z",
    "updated_at": null
  },
  {
    "id": 2,
    "user_id": 123,
    "date_value": "2025-07-14",
    "datatype": "heart_rate",
    "source": "Google Fit",
    "total_value": {
      "average_bpm": 72.5
    },
    "created_at": "2025-07-14T10:30:00Z",
    "updated_at": null
  },
  {
    "id": 3,
    "user_id": 123,
    "date_value": "2025-07-14",
    "datatype": "sleep",
    "source": "Google Fit",
    "total_value": {
      "total_sleep_minutes": 480.0
    },
    "created_at": "2025-07-14T10:30:00Z",
    "updated_at": null
  }
]
```

## Query Parameters Reference

### `/summaries` endpoint supports these query parameters:

| Parameter | Type | Required | Example | Description |
|-----------|------|----------|---------|-------------|
| `start_date` | date | No | `2025-07-01` | Filter summaries from this date onwards |
| `end_date` | date | No | `2025-07-31` | Filter summaries up to this date |
| `datatype` | string | No | `steps` | Filter by data type (steps, heart_rate, sleep, nutrition, weight) |

## Data Types and Expected Values

### Steps Data
```json
{
  "datatype": "steps",
  "total_value": {
    "total_steps": 10000.0
  }
}
```

### Heart Rate Data
```json
{
  "datatype": "heart_rate",
  "total_value": {
    "average_bpm": 72.5
  }
}
```

### Sleep Data
```json
{
  "datatype": "sleep",
  "total_value": {
    "total_sleep_minutes": 480.0,
    "sleep_stage_light_sleep_minutes": 240.0,
    "sleep_stage_deep_sleep_minutes": 120.0,
    "sleep_stage_rem_sleep_minutes": 120.0
  }
}
```

### Nutrition Data
```json
{
  "datatype": "nutrition",
  "total_value": {
    "total_calories_expended": 2200.5
  }
}
```

### Weight Data
```json
{
  "datatype": "weight",
  "total_value": {
    "weight_kg": 70.5
  }
}
```

## Error Responses

### 404 Not Found
```json
{
  "detail": "No health data found for date 2025-07-14"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error processing daily health data: [error message]"
}
```

## JavaScript/TypeScript Example

```typescript
// Example using fetch API
const API_BASE_URL = 'http://localhost:8000/api/daily-activity';
const JWT_TOKEN = 'your-jwt-token-here';

// Process daily data
async function processDailyData(date: string) {
  const response = await fetch(`${API_BASE_URL}/process-daily-data/${date}`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${JWT_TOKEN}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// Get summaries with filters
async function getSummaries(startDate?: string, endDate?: string, datatype?: string) {
  const params = new URLSearchParams();
  if (startDate) params.append('start_date', startDate);
  if (endDate) params.append('end_date', endDate);
  if (datatype) params.append('datatype', datatype);
  
  const url = `${API_BASE_URL}/summaries?${params.toString()}`;
  
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${JWT_TOKEN}`
    }
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}

// Usage examples
processDailyData('2025-07-14').then(console.log);
getSummaries('2025-07-01', '2025-07-31', 'steps').then(console.log);
```

## Python Example

```python
import requests
from datetime import date

API_BASE_URL = 'http://localhost:8000/api/daily-activity'
JWT_TOKEN = 'your-jwt-token-here'

headers = {
    'Authorization': f'Bearer {JWT_TOKEN}',
    'Content-Type': 'application/json'
}

# Process daily data
def process_daily_data(target_date: str):
    response = requests.post(
        f'{API_BASE_URL}/process-daily-data/{target_date}',
        headers=headers
    )
    response.raise_for_status()
    return response.json()

# Get summaries with filters
def get_summaries(start_date=None, end_date=None, datatype=None):
    params = {}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    if datatype:
        params['datatype'] = datatype
    
    response = requests.get(
        f'{API_BASE_URL}/summaries',
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json()

# Usage examples
summaries = process_daily_data('2025-07-14')
print(summaries)

steps_data = get_summaries(
    start_date='2025-07-01',
    end_date='2025-07-31',
    datatype='steps'
)
print(steps_data)
```

## Testing the API

1. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access the interactive API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Run the test script:**
   ```bash
   python test_daily_activity_summary.py
   ```

The interactive documentation will show all the example values and allow you to test the endpoints directly from your browser.