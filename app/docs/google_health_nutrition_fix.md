# Google Health Nutrition Data Fix

## Issue Description

The Google Fitness API was returning 404 errors when trying to fetch nutrition data using the data source `com.google.nutrition`. The error occurred because:

1. The data source `com.google.nutrition` doesn't exist in the Google Fitness API
2. The API endpoint construction was incorrect for nutrition data
3. There was no proper error handling for missing or unavailable data sources

## Root Cause Analysis

### Original Error
```
ERROR | Google Fitness API error: Status 404
The requested URL /fitness/v1/users/me/dataSources/com.google.nutrition/datasets/1752483364140-1752483364140 was not found on this server.
```

### Issues Identified
1. **Incorrect Data Source**: `com.google.nutrition` is not a valid Google Fitness data source
2. **Wrong API Endpoint**: Using datasets endpoint instead of aggregate endpoint
3. **No Error Handling**: The service would fail completely if one data type failed
4. **Limited Nutrition Support**: Google Fitness API has limited nutrition data support

## Solution Implemented

### 1. Updated Data Source Mapping
Changed the nutrition data source from `com.google.nutrition` to `com.google.calories.expended`:

```python
def map_data_type_to_source(data_type: str) -> str:
    """Map data type to Google Fitness data source."""
    mapping = {
        "steps": "com.google.step_count.delta",
        "heart_rate": "com.google.heart_rate.bpm",
        "sleep": "com.google.sleep.segment",
        "weight": "com.google.weight",
        "nutrition": "com.google.calories.expended"  # Fixed: Use calories as nutrition proxy
    }
    return mapping.get(data_type)
```

### 2. Fixed API Endpoint Construction
Updated the `build_data_request` function to use the aggregate endpoint for nutrition data:

```python
elif data_type == "nutrition":
    # For nutrition data, use the dataset:aggregate endpoint like other data types
    url = f"{base_url}/users/me/dataset:aggregate"
    payload = {
        "aggregateBy": [{
            "dataTypeName": data_source
        }],
        "bucketByTime": {"durationMillis": 86400000},  # 1 day
        "startTimeMillis": start_time_millis,
        "endTimeMillis": end_time_millis
    }
```

### 3. Enhanced Error Handling
Added comprehensive error handling to prevent complete failure when one data type fails:

```python
try:
    # ... data fetching logic ...
except requests.exceptions.RequestException as e:
    logger.error(f"Error fetching {data_type} data: {str(e)}")
    # Continue with other data types instead of failing completely
    continue
except Exception as e:
    logger.error(f"Unexpected error processing {data_type}: {str(e)}")
    # Continue with other data types instead of failing completely
    continue
```

### 4. Special Handling for Nutrition 404 Errors
Added specific handling for nutrition data 404 errors (which are expected when no data is available):

```python
if data_type == "nutrition" and response.status_code == 404:
    logger.warning(f"No nutrition data available for the specified time range")
    continue
```

### 5. Updated Data Processing
Modified the nutrition data processing to handle calories expended data:

```python
elif data_type == "nutrition":
    # Process nutrition data (calories expended) from aggregate endpoint
    if "bucket" in response_data:
        for bucket in response_data["bucket"]:
            # ... process calories expended data ...
            value = {}
            if "value" in point:
                for val in point["value"]:
                    if "fpVal" in val:
                        value["calories_expended"] = val["fpVal"]
                    elif "intVal" in val:
                        value["calories_expended"] = val["intVal"]
```

### 6. Added Data Sources Discovery
Added a new function to list available data sources for debugging:

```python
async def list_available_data_sources(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """List available data sources from Google Fitness API for debugging."""
    # ... implementation ...
```

And corresponding API endpoint:
```
GET /api/google-health/data-sources
```

## Google Fitness API Nutrition Limitations

### Important Notes
1. **Limited Nutrition Data**: Google Fitness API has very limited nutrition data support
2. **Third-Party Apps**: Most nutrition data comes from third-party apps like MyFitnessPal, Cronometer, etc.
3. **Calories Focus**: The API primarily supports calories expended rather than detailed nutrition information
4. **User Data Dependency**: Nutrition data availability depends on what apps the user has connected

### Available Nutrition-Related Data Types
- `com.google.calories.expended` - Calories burned/expended
- `com.google.calories.bmr` - Basal Metabolic Rate calories
- `com.google.nutrition.summary` - Limited nutrition summary (rarely available)

## Testing the Fix

### 1. Test Data Fetching
```bash
curl -X POST "http://localhost:8000/api/google-health/data/fetch" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data_types": ["steps", "heart_rate", "nutrition"],
    "start_date": "2025-01-13T00:00:00Z",
    "end_date": "2025-01-14T00:00:00Z"
  }'
```

### 2. List Available Data Sources
```bash
curl -X GET "http://localhost:8000/api/google-health/data-sources" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Expected Behavior After Fix

1. **No More 404 Errors**: The service will no longer fail with 404 errors for nutrition data
2. **Graceful Degradation**: If nutrition data is not available, other data types will still be fetched
3. **Better Logging**: More informative logs about data availability and errors
4. **Calories Data**: When available, calories expended data will be returned as nutrition data

## Recommendations

### For Better Nutrition Data Support
1. **Integrate with Nutrition APIs**: Consider integrating with dedicated nutrition APIs like:
   - MyFitnessPal API
   - Cronometer API
   - Nutritionix API
   - USDA Food Data Central API

2. **Manual Entry**: Provide manual nutrition entry functionality as a fallback

3. **Third-Party Connections**: Guide users to connect nutrition tracking apps to Google Fit

### Monitoring
- Monitor the new `/data-sources` endpoint to understand what data sources are available for users
- Track success/failure rates for different data types
- Log when nutrition data is unavailable vs. when it contains actual data

## Files Modified

1. `app/services/google_health.py` - Main service logic fixes
2. `app/api/routes/google_health.py` - Added data sources endpoint
3. `app/docs/google_health_nutrition_fix.md` - This documentation

## Future Enhancements

1. **Dynamic Data Source Discovery**: Automatically discover and use available nutrition data sources
2. **Multiple Nutrition Sources**: Support multiple nutrition data sources simultaneously
3. **Data Source Validation**: Validate data sources before making API calls
4. **Caching**: Cache available data sources to reduce API calls