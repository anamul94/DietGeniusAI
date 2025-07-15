#!/usr/bin/env python3
"""
Test script for AI Assessment Summary functionality
"""
import asyncio
from datetime import date, datetime
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.services.daily_activity_summary import daily_activity_assessment_by_ai_nutritionis
from app.services.ai_assessment_summary import (
    get_today_ai_assessment_summary,
    get_ai_assessment_summary_by_date,
    get_ai_assessment_summaries_by_date_range
)

async def test_ai_assessment():
    """Test the AI assessment functionality"""
    
    # Get database session
    db_gen = get_db()
    db: Session = next(db_gen)
    
    try:
        # Test user ID (replace with actual user ID from your database)
        test_user_id = 1
        test_date = date.today()
        
        print(f"Testing AI Assessment for User ID: {test_user_id}")
        print(f"Target Date: {test_date}")
        print("-" * 50)
        
        # Test 1: Generate AI assessment
        print("1. Generating AI assessment...")
        try:
            result = await daily_activity_assessment_by_ai_nutritionis(
                db=db,
                user_id=test_user_id,
                target_date=test_date
            )
            print(f"✅ AI Assessment generated successfully")
            print(f"Date: {result['date']}")
            print(f"Summary length: {len(result['summary'])} characters")
            print(f"Summary preview: {result['summary'][:200]}...")
        except Exception as e:
            print(f"❌ Error generating AI assessment: {str(e)}")
        
        print("\n" + "-" * 50)
        
        # Test 2: Get today's assessment
        print("2. Getting today's assessment from database...")
        try:
            today_summary = get_today_ai_assessment_summary(db=db, user_id=test_user_id)
            if today_summary:
                print(f"✅ Today's assessment found")
                print(f"ID: {today_summary.id}")
                print(f"Date: {today_summary.date_value}")
                print(f"Summary length: {len(today_summary.summary)} characters")
            else:
                print("ℹ️ No assessment found for today")
        except Exception as e:
            print(f"❌ Error getting today's assessment: {str(e)}")
        
        print("\n" + "-" * 50)
        
        # Test 3: Get assessment by specific date
        print("3. Getting assessment by specific date...")
        try:
            date_summary = get_ai_assessment_summary_by_date(
                db=db, 
                user_id=test_user_id, 
                target_date=test_date
            )
            if date_summary:
                print(f"✅ Assessment found for {test_date}")
                print(f"ID: {date_summary.id}")
                print(f"Created: {date_summary.created_at}")
                print(f"Updated: {date_summary.updated_at}")
            else:
                print(f"ℹ️ No assessment found for {test_date}")
        except Exception as e:
            print(f"❌ Error getting assessment by date: {str(e)}")
        
        print("\n" + "-" * 50)
        
        # Test 4: Get assessments by date range
        print("4. Getting assessments by date range (last 7 days)...")
        try:
            from datetime import timedelta
            start_date = test_date - timedelta(days=7)
            end_date = test_date
            
            range_summaries = get_ai_assessment_summaries_by_date_range(
                db=db,
                user_id=test_user_id,
                start_date=start_date,
                end_date=end_date
            )
            print(f"✅ Found {len(range_summaries)} assessments in date range")
            for summary in range_summaries:
                print(f"  - {summary.date_value}: {len(summary.summary)} chars")
        except Exception as e:
            print(f"❌ Error getting assessments by date range: {str(e)}")
        
        print("\n" + "=" * 50)
        print("✅ AI Assessment testing completed!")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🧪 Starting AI Assessment Summary Tests")
    print("=" * 50)
    asyncio.run(test_ai_assessment())