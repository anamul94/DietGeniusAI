from textwrap import dedent
from datetime import date, datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from collections import defaultdict

from app.core.logging import logger
from app.models.google_health import GoogleHealthData
from app.models.daily_activity_summary import DailyActivitySummary
from app.schemas.daily_activity_summary import (
    DataObject,
    DailyActivitySummaryCreate,
    DailyActivitySummaryUpdate
)

from app.agents.agetns import assessment_agent
from app.agents.utility_agent import report_representation_agent


async def fetch_and_process_daily_health_data(
    db: Session,
    user_id: int,
    target_date: date
) -> List[DataObject]:
    """
    Fetch Google Health data for a specific date, preprocess it, and convert to DataObject format.
    
    Args:
        db: Database session
        user_id: User ID
        target_date: The specific date to fetch data for
        
    Returns:
        List[DataObject]: List of processed data objects grouped by data type
    """
    try:
        # Define start and end datetime for the target date
        start_datetime = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        end_datetime = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
        
        logger.info(f"Fetching health data for user {user_id} on date {target_date}")
        logger.info(f"Date range: {start_datetime} to {end_datetime}")
        
        # Fetch all Google Health data for the specified date
        health_data = db.query(GoogleHealthData).filter(
            and_(
                GoogleHealthData.user_id == user_id,
                GoogleHealthData.start_time >= start_datetime,
                GoogleHealthData.start_time < end_datetime + timedelta(days=1)
            )
        ).all()
        
        logger.info(f"Found {len(health_data)} health data records for processing")
        
        if not health_data:
            logger.warning(f"No health data found for user {user_id} on date {target_date}")
            return []
        
        # Group data by data_type and aggregate values
        grouped_data = defaultdict(lambda: {
            'source': '',
            'values': defaultdict(float),
            'count': 0
        })
        
        for data in health_data:
            data_type = data.data_type
            source = data.source or "Unknown"
            
            # Set source (use the first non-empty source found)
            if not grouped_data[data_type]['source'] and source:
                grouped_data[data_type]['source'] = source
            
            # Process and aggregate values based on data type
            if data.value:
                processed_values = _process_data_values(data_type, data.value)
                
                # Aggregate values
                for key, value in processed_values.items():
                    if isinstance(value, (int, float)):
                        grouped_data[data_type]['values'][key] += float(value)
                        grouped_data[data_type]['count'] += 1
        
        # Convert grouped data to DataObject format
        data_objects = []
        for data_type, aggregated_data in grouped_data.items():
            if aggregated_data['values']:  # Only include if we have actual values
                data_object = DataObject(
                    datatype=data_type,
                    source=aggregated_data['source'] or "Google Fit",
                    total_value=dict(aggregated_data['values']),
                    date_value=target_date
                )
                data_objects.append(data_object)
                
                logger.info(f"Created DataObject for {data_type}: {data_object.total_value}")
        
        logger.info(f"Successfully processed {len(data_objects)} data objects")
        return data_objects
        
    except Exception as e:
        logger.error(f"Error fetching and processing daily health data: {str(e)}")
        raise


def _process_data_values(data_type: str, value: Dict[str, Any]) -> Dict[str, float]:
    """
    Process and normalize data values based on data type.
    
    Args:
        data_type: The type of health data
        value: The raw value dictionary from Google Health
        
    Returns:
        Dict[str, float]: Processed values with standardized keys including units
    """
    processed = {}
    
    try:
        if data_type == "steps":
            if "steps" in value:
                processed["total_steps_count"] = float(value["steps"])
        
        elif data_type == "heart_rate":
            if "bpm" in value:
                processed["average_heart_rate_bpm"] = float(value["bpm"])
        
        elif data_type == "weight":
            if "weight_kg" in value:
                processed["weight_kg"] = float(value["weight_kg"])
        
        elif data_type == "sleep":
            if "sleep_duration_minutes" in value:
                processed["total_sleep_duration_minutes"] = float(value["sleep_duration_minutes"])
            if "sleep_stage" in value:
                stage_name = value.get("sleep_stage_name", "unknown")
                processed[f"sleep_stage_{stage_name.lower().replace(' ', '_')}_duration_minutes"] = float(
                    value.get("sleep_duration_minutes", 0)
                )
        
        elif data_type == "nutrition":
            if "calories_expended" in value:
                processed["total_calories_expended_kcal"] = float(value["calories_expended"])
        
        else:
            # For unknown data types, try to extract numeric values with units
            for key, val in value.items():
                if isinstance(val, (int, float)):
                    # Try to infer unit from key name
                    if "calorie" in key.lower():
                        processed[f"total_{key}_kcal"] = float(val)
                    elif "weight" in key.lower():
                        processed[f"total_{key}_kg"] = float(val)
                    elif "distance" in key.lower():
                        processed[f"total_{key}_meters"] = float(val)
                    elif "duration" in key.lower() or "time" in key.lower():
                        processed[f"total_{key}_minutes"] = float(val)
                    elif "bpm" in key.lower() or "heart" in key.lower():
                        processed[f"total_{key}_bpm"] = float(val)
                    elif "step" in key.lower():
                        processed[f"total_{key}_count"] = float(val)
                    else:
                        processed[f"total_{key}_value"] = float(val)
    
    except (ValueError, TypeError) as e:
        logger.warning(f"Error processing values for {data_type}: {str(e)}")
    
    return processed


async def save_daily_activity_summary(
    db: Session,
    data_objects: List[DataObject],
    user_id: int
) -> List[DailyActivitySummary]:
    """
    Save processed data objects to the daily activity summary table.
    Handles upsert logic to prevent duplicates for the same day and data type.
    
    Args:
        db: Database session
        data_objects: List of processed data objects
        user_id: User ID
        
    Returns:
        List[DailyActivitySummary]: List of saved/updated summary records
    """
    saved_summaries = []
    
    try:
        for data_obj in data_objects:
            # Check if a summary already exists for this user, date, and data type
            existing_summary = db.query(DailyActivitySummary).filter(
                and_(
                    DailyActivitySummary.user_id == user_id,
                    DailyActivitySummary.date_value == data_obj.date_value,
                    DailyActivitySummary.datatype == data_obj.datatype
                )
            ).first()
            
            if existing_summary:
                # Update existing record
                logger.info(f"Updating existing summary for {data_obj.datatype} on {data_obj.date_value}")
                existing_summary.total_value = data_obj.total_value
                existing_summary.source = data_obj.source
                existing_summary.updated_at = datetime.now(timezone.utc)
                
                db.commit()
                db.refresh(existing_summary)
                saved_summaries.append(existing_summary)
                
            else:
                # Create new record
                logger.info(f"Creating new summary for {data_obj.datatype} on {data_obj.date_value}")
                summary_create = DailyActivitySummaryCreate(
                    user_id=user_id,
                    date_value=data_obj.date_value,
                    datatype=data_obj.datatype,
                    source=data_obj.source,
                    total_value=data_obj.total_value
                )
                
                db_summary = DailyActivitySummary(**summary_create.model_dump())
                db.add(db_summary)
                db.commit()
                db.refresh(db_summary)
                saved_summaries.append(db_summary)
        
        logger.info(f"Successfully saved/updated {len(saved_summaries)} daily activity summaries")
        return saved_summaries
        
    except Exception as e:
        logger.error(f"Error saving daily activity summary: {str(e)}")
        db.rollback()
        raise


async def process_daily_health_data_by_date(
    db: Session,
    user_id: int,
    target_date: date
) -> List[DailyActivitySummary]:
    """
    Main function to fetch, process, and save daily health data for a specific date.
    
    Args:
        db: Database session
        user_id: User ID
        target_date: The specific date to process
        
    Returns:
        List[DailyActivitySummary]: List of saved daily activity summaries
    """
    try:
        logger.info(f"Starting daily health data processing for user {user_id} on {target_date}")
        
        # Step 1: Fetch and process data
        data_objects = await fetch_and_process_daily_health_data(db, user_id, target_date)
        
        if not data_objects:
            logger.warning(f"No data objects to process for user {user_id} on {target_date}")
            return []
        
        # Step 2: Save to daily activity summary table
        saved_summaries = await save_daily_activity_summary(db, data_objects, user_id)
        
        logger.info(f"Successfully processed daily health data for user {user_id} on {target_date}")
        logger.info(f"Created/updated {len(saved_summaries)} summary records")
        
        return saved_summaries
        
    except Exception as e:
        logger.error(f"Error in process_daily_health_data_by_date: {str(e)}")
        raise


async def get_daily_activity_summaries(
    db: Session,
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    datatype: Optional[str] = None
) -> List[DailyActivitySummary]:
    """
    Retrieve daily activity summaries for a user with optional filters.
    
    Args:
        db: Database session
        user_id: User ID
        start_date: Optional start date filter
        end_date: Optional end date filter
        datatype: Optional data type filter
        
    Returns:
        List[DailyActivitySummary]: List of daily activity summaries
    """
    query = db.query(DailyActivitySummary).filter(DailyActivitySummary.user_id == user_id)
    
    if start_date:
        query = query.filter(DailyActivitySummary.date_value >= start_date)
    
    if end_date:
        query = query.filter(DailyActivitySummary.date_value <= end_date)
    
    if datatype:
        query = query.filter(DailyActivitySummary.datatype == datatype)
    
    return query.order_by(DailyActivitySummary.date_value.desc()).all()


async def daily_activity_assessment_by_ai_nutritionis(
    db: Session,
    user_id: int,
    user_name: str,
    target_date: Optional[date] = None
) -> dict:
    """
    Generate AI-based assessment for user's daily activity and nutrition data.
    Fetches activity and food data for the specified date, gets AI assessment,
    and saves the summary to the database.
    
    Args:
        db: Database session
        user_id: User ID
        target_date: Date to assess (defaults to today)
        
    Returns:
        dict: Contains date and summary
    """
    try:
        from app.services.meal_entry import get_meal_entries_by_date
        from app.services.ai_assessment_summary import create_or_update_ai_assessment_summary
        
        # Use today if no target date provided
        if target_date is None:
            target_date = datetime.now().date()
        
        logger.info(f"Starting AI assessment for user {user_id} on {target_date}")
        
        # Fetch daily activity summaries for the target date
        daily_activity_summaries = await get_daily_activity_summaries(
            db=db,
            user_id=user_id,
            start_date=target_date,
            end_date=target_date
        )
        
        # Fetch meal entries (food nutrition data) for the target date
        meal_entries = get_meal_entries_by_date(
            db=db,
            user_id=user_id,
            target_date=target_date
        )
        
        # Prepare data for AI agent
        activity_summary = {}
        for activity in daily_activity_summaries:
            activity_summary[activity.datatype] = {
                "source": activity.source,
                "values": activity.total_value,
                "date": str(activity.date_value)
            }
        
        nutrition_summary = []
        for meal_entry in meal_entries:
            nutrition_summary.append({
                "meal_type": meal_entry.meal_type.value,
                "foods": meal_entry.foods,
                "consumed_at": str(meal_entry.consumed_at)
            })
        
        if activity_summary is None:
            activity_summary = {}
        if nutrition_summary is None:
            nutrition_summary = []
        # Create message for AI agent
        message = dedent(f"""\
            User Name: {user_name}
            Assessment Date: {target_date}
            
            Daily Activity Data:
            {activity_summary}
            
            Nutrition Data (Meal Entries):
            {nutrition_summary}
            
            Please provide a comprehensive health assessment based on the user's activity and nutrition data for this date.
            Include insights about their physical activity levels, nutritional intake, and recommendations for improvement.
        """)
        
        # Get AI assessment
        nutritionist_agent = assessment_agent()
        summary = ""
        for chunk in nutritionist_agent.run(message=message, stream=True):
            if chunk.content is not None:
                summary += chunk.content
                print(chunk.content, end="", flush=True)
                
        # docs_formater = report_representation_agent()
        logger.info("**********************************************")
        final_summary = ""
        for chunk in report_representation_agent.run(message=summary, stream=True):
            if chunk.content is not None:
                final_summary += chunk.content
                print(chunk.content, end="", flush=True)
        
        # Save summary to database
        ai_summary = create_or_update_ai_assessment_summary(
            db=db,
            user_id=user_id,
            target_date=target_date,
            summary=final_summary
        )
        
        logger.info(f"Successfully created AI assessment for user {user_id} on {target_date}")
        
        return {
            "date": target_date,
            "summary": final_summary
        }
        
    except Exception as e:
        logger.error(f"Error in daily_activity_assessment_by_ai_nutritionis: {str(e)}")
        raise