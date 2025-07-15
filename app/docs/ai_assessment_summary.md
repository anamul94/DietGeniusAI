# AI Assessment Summary Service

This document describes the AI Assessment Summary service that provides AI-generated daily health assessments based on user activity and nutrition data.

## Overview

The AI Assessment Summary service combines user activity data and meal/nutrition data to generate comprehensive daily health assessments using an AI nutritionist agent. The service ensures only one assessment per user per day and provides APIs to retrieve assessments.

## Components

### 1. Database Model

**File:** `app/models/ai_assessment_summary.py`

```python
class AIAssessmentSummary(Base):
    __tablename__ = "ai_assessment_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date_value = Column(Date, nullable=False)
    summary = Column(Text, nullable=False)  # Markdown formatted summary
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Features:**
- Unique constraint on `user_id` and `date_value` (one summary per user per day)
- Stores AI-generated summaries in markdown format
- Automatic timestamps for creation and updates

### 2. Schemas

**File:** `app/schemas/ai_assessment_summary.py`

- `AIAssessmentSummaryBase`: Base schema with date and summary
- `AIAssessmentSummaryCreate`: For creating new assessments
- `AIAssessmentSummaryUpdate`: For updating existing assessments
- `AIAssessmentSummary`: Full model with all fields
- `AIAssessmentSummaryResponse`: API response format

### 3. Service Layer

**File:** `app/services/ai_assessment_summary.py`

#### Functions:

- `create_or_update_ai_assessment_summary()`: Creates new or updates existing summary
- `get_ai_assessment_summary_by_date()`: Gets summary for specific date
- `get_ai_assessment_summaries_by_date_range()`: Gets summaries for date range
- `get_today_ai_assessment_summary()`: Gets today's summary

**File:** `app/services/daily_activity_summary.py`

#### Main Function:

```python
async def daily_activity_assessment_by_ai_nutritionis(
    db: Session,
    user_id: int,
    target_date: Optional[date] = None
) -> dict:
```

**Process:**
1. Fetches user's daily activity summaries for the target date
2. Fetches user's meal entries (nutrition data) for the target date
3. Prepares structured data for AI agent
4. Generates AI assessment using the nutritionist agent
5. Saves the assessment summary to database
6. Returns the generated assessment

### 4. API Endpoints

**File:** `app/api/routes/daily_activity_summary.py`

#### Available Endpoints:

1. **POST `/generate-assessment`**
   - Generates new AI assessment for specified date (defaults to today)
   - Returns: `AIAssessmentSummaryResponse`

2. **GET `/today-assessment`**
   - Gets today's AI assessment from database
   - Returns: `AIAssessmentSummary` or `null`

3. **GET `/assessment/{target_date}`**
   - Gets AI assessment for specific date
   - Returns: `AIAssessmentSummary` or `null`

4. **GET `/assessments`**
   - Gets AI assessments for date range
   - Query params: `start_date`, `end_date`
   - Returns: `List[AIAssessmentSummary]`

## Data Sources

### Activity Data
- Source: `DailyActivitySummary` table
- Includes: steps, heart rate, sleep, nutrition, weight data
- Aggregated by data type per day

### Nutrition Data
- Source: `MealEntry` table (via `meal_entry.py` service)
- Includes: meal types, food items, nutrition facts
- Organized by meal consumption time

## AI Agent Integration

The service uses the `assesment_agent()` from `app/agents/agetns.py`:
- Model: AWS Bedrock Anthropic Sonnet 3
- Features: Memory, reasoning, markdown output
- Goal: Assess user health and provide recommendations

## Usage Examples

### Generate Assessment
```python
result = await daily_activity_assessment_by_ai_nutritionis(
    db=db,
    user_id=123,
    target_date=date(2025, 7, 15)
)
```

### Get Today's Assessment
```python
summary = get_today_ai_assessment_summary(db=db, user_id=123)
```

### Get Assessment by Date Range
```python
summaries = get_ai_assessment_summaries_by_date_range(
    db=db,
    user_id=123,
    start_date=date(2025, 7, 1),
    end_date=date(2025, 7, 31)
)
```

## API Usage Examples

### Generate New Assessment
```bash
POST /generate-assessment?target_date=2025-07-15
Authorization: Bearer <token>
```

### Get Today's Assessment
```bash
GET /today-assessment
Authorization: Bearer <token>
```

### Get Assessment by Date
```bash
GET /assessment/2025-07-15
Authorization: Bearer <token>
```

### Get Assessments by Date Range
```bash
GET /assessments?start_date=2025-07-01&end_date=2025-07-31
Authorization: Bearer <token>
```

## Database Migration

**File:** `migrations/versions/ai_assessment_summary_table.py`

Run the migration to create the `ai_assessment_summaries` table:

```bash
alembic upgrade head
```

## Testing

Use the provided test script to verify functionality:

```bash
python test_ai_assessment.py
```

## Error Handling

The service includes comprehensive error handling:
- Database connection errors
- AI agent failures
- Data validation errors
- Duplicate prevention
- Logging for debugging

## Security

- All endpoints require user authentication
- Users can only access their own assessments
- Input validation on all parameters
- SQL injection prevention through ORM

## Performance Considerations

- Database indexes on `user_id` and `date_value`
- Unique constraints prevent duplicates
- Efficient date range queries
- Streaming AI responses for better UX

## Future Enhancements

1. **Caching**: Add Redis caching for frequently accessed assessments
2. **Batch Processing**: Generate assessments for multiple dates
3. **Notifications**: Send daily assessment notifications
4. **Analytics**: Track assessment trends over time
5. **Export**: Allow users to export assessments as PDF/CSV