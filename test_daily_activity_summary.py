"""
Test script for Daily Activity Summary functionality.

This script demonstrates how to use the daily activity summary functions
to fetch, process, and save Google Health data by date.
"""

import asyncio
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session
from app.core.database_config import get_db
from app.services.daily_activity_summary import (
    process_daily_health_data_by_date,
    fetch_and_process_daily_health_data,
    get_daily_activity_summaries
)
from app.models.user import User
from app.models.google_health import GoogleHealthData
from app.core.logging import logger


async def test_daily_activity_summary():
    """Test the daily activity summary functionality."""
    
    # Get database session
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # Test with a sample user (you'll need to replace with actual user ID)
        test_user_id = 1
        test_date = date(2025, 7, 14)  # Yesterday's date for testing
        
        print(f"Testing Daily Activity Summary for User ID: {test_user_id}")
        print(f"Target Date: {test_date}")
        print("-" * 50)
        
        # Check if user exists
        user = db.query(User).filter(User.id == test_user_id).first()
        if not user:
            print(f"❌ User with ID {test_user_id} not found!")
            return
        
        print(f"✅ Found user: {user.username or user.email}")
        
        # Check existing Google Health data for the date
        existing_data = db.query(GoogleHealthData).filter(
            GoogleHealthData.user_id == test_user_id
        ).all()
        
        print(f"📊 Found {len(existing_data)} Google Health records for user")
        
        if existing_data:
            print("Sample data types available:")
            data_types = set(data.data_type for data in existing_data)
            for dt in data_types:
                count = len([d for d in existing_data if d.data_type == dt])
                print(f"  - {dt}: {count} records")
        
        print("\n" + "="*50)
        print("STEP 1: Preview Data Objects (without saving)")
        print("="*50)
        
        # Step 1: Preview the data objects that would be created
        try:
            data_objects = await fetch_and_process_daily_health_data(
                db=db,
                user_id=test_user_id,
                target_date=test_date
            )
            
            if data_objects:
                print(f"✅ Successfully processed {len(data_objects)} data objects:")
                for i, obj in enumerate(data_objects, 1):
                    print(f"\n  {i}. DataObject:")
                    print(f"     - Data Type: {obj.datatype}")
                    print(f"     - Source: {obj.source}")
                    print(f"     - Date: {obj.date_value}")
                    print(f"     - Total Values: {obj.total_value}")
            else:
                print("❌ No data objects created (no health data found for the date)")
                
        except Exception as e:
            print(f"❌ Error in preview step: {str(e)}")
            logger.error(f"Preview error: {str(e)}")
        
        print("\n" + "="*50)
        print("STEP 2: Process and Save Daily Activity Summary")
        print("="*50)
        
        # Step 2: Process and save the daily activity summary
        try:
            summaries = await process_daily_health_data_by_date(
                db=db,
                user_id=test_user_id,
                target_date=test_date
            )
            
            if summaries:
                print(f"✅ Successfully created/updated {len(summaries)} daily activity summaries:")
                for i, summary in enumerate(summaries, 1):
                    print(f"\n  {i}. Daily Activity Summary:")
                    print(f"     - ID: {summary.id}")
                    print(f"     - Data Type: {summary.datatype}")
                    print(f"     - Source: {summary.source}")
                    print(f"     - Date: {summary.date_value}")
                    print(f"     - Total Values: {summary.total_value}")
                    print(f"     - Created: {summary.created_at}")
                    print(f"     - Updated: {summary.updated_at}")
            else:
                print("❌ No summaries created (no health data found for the date)")
                
        except Exception as e:
            print(f"❌ Error in processing step: {str(e)}")
            logger.error(f"Processing error: {str(e)}")
        
        print("\n" + "="*50)
        print("STEP 3: Retrieve Saved Summaries")
        print("="*50)
        
        # Step 3: Retrieve the saved summaries
        try:
            retrieved_summaries = await get_daily_activity_summaries(
                db=db,
                user_id=test_user_id,
                start_date=test_date,
                end_date=test_date
            )
            
            if retrieved_summaries:
                print(f"✅ Retrieved {len(retrieved_summaries)} summaries for {test_date}:")
                for summary in retrieved_summaries:
                    print(f"  - {summary.datatype}: {summary.total_value}")
            else:
                print("❌ No summaries found in database")
                
        except Exception as e:
            print(f"❌ Error retrieving summaries: {str(e)}")
            logger.error(f"Retrieval error: {str(e)}")
        
        print("\n" + "="*50)
        print("STEP 4: Test Duplicate Prevention")
        print("="*50)
        
        # Step 4: Test running the same process again (should update, not duplicate)
        try:
            print("Running the process again to test duplicate prevention...")
            summaries_2nd_run = await process_daily_health_data_by_date(
                db=db,
                user_id=test_user_id,
                target_date=test_date
            )
            
            if summaries_2nd_run:
                print(f"✅ Second run completed. Updated {len(summaries_2nd_run)} summaries.")
                print("Checking for duplicates...")
                
                all_summaries = await get_daily_activity_summaries(
                    db=db,
                    user_id=test_user_id,
                    start_date=test_date,
                    end_date=test_date
                )
                
                # Group by datatype to check for duplicates
                datatype_counts = {}
                for summary in all_summaries:
                    datatype_counts[summary.datatype] = datatype_counts.get(summary.datatype, 0) + 1
                
                duplicates_found = any(count > 1 for count in datatype_counts.values())
                
                if duplicates_found:
                    print("❌ Duplicates found!")
                    for datatype, count in datatype_counts.items():
                        if count > 1:
                            print(f"  - {datatype}: {count} records (should be 1)")
                else:
                    print("✅ No duplicates found. Unique constraint working correctly!")
                    for datatype, count in datatype_counts.items():
                        print(f"  - {datatype}: {count} record")
            
        except Exception as e:
            print(f"❌ Error in duplicate test: {str(e)}")
            logger.error(f"Duplicate test error: {str(e)}")
        
        print("\n" + "="*50)
        print("TEST COMPLETED")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        logger.error(f"Test error: {str(e)}")
    
    finally:
        db.close()


def create_sample_google_health_data(db: Session, user_id: int, target_date: date):
    """Create sample Google Health data for testing purposes."""
    
    from app.models.google_health import GoogleHealthData
    from datetime import datetime, timezone
    
    # Create sample data for the target date
    start_time = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_time = datetime.combine(target_date, datetime.max.time()).replace(tzinfo=timezone.utc)
    
    sample_data = [
        {
            "data_type": "steps",
            "value": {"steps": 8500},
            "source": "Google Fit"
        },
        {
            "data_type": "steps",
            "value": {"steps": 1500},  # Additional steps data to test aggregation
            "source": "Google Fit"
        },
        {
            "data_type": "heart_rate",
            "value": {"bpm": 72.5},
            "source": "Google Fit"
        },
        {
            "data_type": "heart_rate",
            "value": {"bpm": 68.0},  # Additional heart rate to test aggregation
            "source": "Google Fit"
        },
        {
            "data_type": "sleep",
            "value": {"sleep_duration_minutes": 480, "sleep_stage": 4, "sleep_stage_name": "Light sleep"},
            "source": "Google Fit"
        },
        {
            "data_type": "nutrition",
            "value": {"calories_expended": 2200.5},
            "source": "Google Fit"
        }
    ]
    
    created_records = []
    for data in sample_data:
        health_data = GoogleHealthData(
            user_id=user_id,
            data_type=data["data_type"],
            start_time=start_time,
            end_time=end_time,
            value=data["value"],
            source=data["source"]
        )
        db.add(health_data)
        created_records.append(health_data)
    
    db.commit()
    return created_records


async def test_with_sample_data():
    """Test the functionality with sample data."""
    
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # Create a test user if needed
        test_user = db.query(User).first()
        if not test_user:
            print("❌ No users found in database. Please create a user first.")
            return
        
        test_date = date(2025, 7, 14)
        
        print("Creating sample Google Health data...")
        sample_records = create_sample_google_health_data(db, test_user.id, test_date)
        print(f"✅ Created {len(sample_records)} sample health records")
        
        # Now run the main test
        await test_daily_activity_summary()
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Daily Activity Summary Test")
    print("=" * 50)
    
    # Choose which test to run
    print("1. Test with existing data")
    print("2. Test with sample data (creates sample Google Health records)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(test_daily_activity_summary())
    elif choice == "2":
        asyncio.run(test_with_sample_data())
    else:
        print("Invalid choice. Running test with existing data...")
        asyncio.run(test_daily_activity_summary())