# Daily Activity Summary

This module provides functionality to fetch Google Health data by date, preprocess it, and save it to a daily activity summary table. The system groups data by data type and performs aggregation to create daily summaries.

## Overview

The Daily Activity Summary system:

1. **Fetches** Google Health data for a specific date from the `google_health_data` table
2. **Groups** data by `data_type` (e.g., steps, heart_rate, sleep, nutrition)
3. **Aggregates** values for each data type (summation for most metrics)
4. **Converts** to standardized `DataObject` format
5. **Saves** to `daily_activity_summary` table with duplicate prevention

## DataObject Schema

```python
class DataObject(BaseModel):
    datatype: str = Field(..., example="steps")
    source: str = Field(..., example="Google Fit")
    total_value: Dict[str, float]  # dynamic string keys, float values
    date_value: date
```

## Database Schema

### daily_activity_summary Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users table |
| date_value | Date | The date for this summary |
| datatype | String | Type of data (steps, heart_rate, sleep, etc.) |
| source | String | Data source (e.g., "Google Fit") |
| total_value | JSON | Aggregated values as key-value pairs |
| created_at | DateTime | Record creation timestamp |
| updated_at | DateTime | Last update timestamp |

**Unique Constraint**: `(user_id, date_value, datatype)` - Ensures only one record per user, per date, per data type.

## Data Processing Logic

### Steps Data
- **Input**: `{"steps": 5000}`
- **Output**: `{"total_steps": 5000.0}`
- **Aggregation**: Sum of all step counts for the day

### Heart Rate Data
- **Input**: `{"bpm": 72.5}`
- **Output**: `{"average_bpm": 72.5}`
- **Aggregation**: Average of all heart rate readings

### Sleep Data
- **Input**: `{"sleep_duration_minutes": 480, "sleep_stage": 4, "sleep_stage_name": "Light sleep"}`
- **Output**: `{"total_sleep_minutes": 480.0, "sleep_stage_light_sleep_minutes": 480.0}`
- **Aggregation**: Sum of sleep duration, categorized by sleep stage

### Nutrition Data
- **Input**: `{"calories_expended": 2200.5}`
- **Output**: `{"total_calories_expended": 2200.5}`
- **Aggregation**: Sum of all calorie expenditure

### Weight Data
- **Input**: `{"weight_kg": 70.5}`
- **Output**: `{"weight_kg": 70.5}`
- **Aggregation**: Latest weight reading for the day

## API Endpoints

### Process Daily Data
```http
POST /api/daily-activity/process-daily-data/{target_date}
```

Processes Google Health data for a specific date and saves to daily activity summary.

**Parameters:**
- `target_date`: Date in YYYY-MM-DD format

**Response:** List of created/updated daily activity summaries

### Preview Data Objects
```http
GET /api/daily-activity/preview-data/{target_date}
```

Preview processed DataObject format without saving to database.

**Parameters:**
- `target_date`: Date in YYYY-MM-DD format

**Response:** List of DataObject instances

### Get Daily Summaries
```http
GET /api/daily-activity/summaries
```

Retrieve daily activity summaries with optional filters.

**Query Parameters:**
- `start_date`: Filter from this date (optional)
- `end_date`: Filter to this date (optional)
- `datatype`: Filter by data type (optional)

### Get Summaries by Date
```http
GET /api/daily-activity/summaries/{target_date}
```

Get all daily activity summaries for a specific date.

## Usage Examples

### Python Service Usage

```python
from datetime import date
from app.services.daily_activity_summary import process_daily_health_data_by_date

# Process data for a specific date
target_date = date(2025, 7, 14)
summaries = await process_daily_health_data_by_date(
    db=db,
    user_id=user_id,
    target_date=target_date
)
```

### API Usage

```bash
# Process daily data
curl -X POST "http://localhost:8000/api/daily-activity/process-daily-data/2025-07-14" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Preview data objects
curl -X GET "http://localhost:8000/api/daily-activity/preview-data/2025-07-14" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get summaries with filters
curl -X GET "http://localhost:8000/api/daily-activity/summaries?start_date=2025-07-01&datatype=steps" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Data Aggregation Examples

### Example 1: Steps Data
**Raw Google Health Data:**
```json
[
  {"data_type": "steps", "value": {"steps": 5000}, "start_time": "2025-07-14T08:00:00Z"},
  {"data_type": "steps", "value": {"steps": 3000}, "start_time": "2025-07-14T14:00:00Z"},
  {"data_type": "steps", "value": {"steps": 2000}, "start_time": "2025-07-14T18:00:00Z"}
]
```

**Processed DataObject:**
```json
{
  "datatype": "steps",
  "source": "Google Fit",
  "total_value": {"total_steps": 10000.0},
  "date_value": "2025-07-14"
}
```

### Example 2: Multiple Data Types
**Raw Google Health Data:**
```json
[
  {"data_type": "steps", "value": {"steps": 8500}},
  {"data_type": "heart_rate", "value": {"bpm": 72.5}},
  {"data_type": "sleep", "value": {"sleep_duration_minutes": 480}},
  {"data_type": "nutrition", "value": {"calories_expended": 2200.5}}
]
```

**Processed DataObjects:**
```json
[
  {
    "datatype": "steps",
    "source": "Google Fit",
    "total_value": {"total_steps": 8500.0},
    "date_value": "2025-07-14"
  },
  {
    "datatype": "heart_rate",
    "source": "Google Fit",
    "total_value": {"average_bpm": 72.5},
    "date_value": "2025-07-14"
  },
  {
    "datatype": "sleep",
    "source": "Google Fit",
    "total_value": {"total_sleep_minutes": 480.0},
    "date_value": "2025-07-14"
  },
  {
    "datatype": "nutrition",
    "source": "Google Fit",
    "total_value": {"total_calories_expended": 2200.5},
    "date_value": "2025-07-14"
  }
]
```

## Duplicate Prevention

The system prevents duplicate records using a unique constraint on `(user_id, date_value, datatype)`. When processing data for a date that already has summaries:

1. **Existing records are updated** with new aggregated values
2. **`updated_at` timestamp is refreshed**
3. **No duplicate records are created**

## Testing

Run the test script to verify functionality:

```bash
python test_daily_activity_summary.py
```

The test script provides:
1. **Preview functionality** - Shows DataObjects without saving
2. **Processing test** - Creates/updates daily summaries
3. **Retrieval test** - Fetches saved summaries
4. **Duplicate prevention test** - Verifies unique constraint works

## Database Migration

Apply the migration to create the table:

```bash
alembic upgrade head
```

The migration file: `migrations/versions/daily_activity_summary_table.py`

## Error Handling

The system handles various error scenarios:

- **No health data found**: Returns empty list
- **Invalid data types**: Logs warnings and continues processing
- **Database errors**: Rolls back transactions and raises exceptions
- **Duplicate processing**: Updates existing records instead of failing

## Performance Considerations

- **Indexing**: Primary key and unique constraint provide efficient lookups
- **Batch processing**: Processes all data types for a date in a single transaction
- **Aggregation**: Performed in memory for better performance
- **Date filtering**: Uses efficient date range queries on indexed columns

## Future Enhancements

Potential improvements:
1. **Batch date processing** - Process multiple dates at once
2. **Custom aggregation rules** - User-defined aggregation logic
3. **Data validation** - Enhanced validation for health metrics
4. **Trend analysis** - Compare daily summaries over time
5. **Export functionality** - Export summaries to CSV/JSON