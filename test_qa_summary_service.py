#!/usr/bin/env python3
"""
Test script for QA Summary Service
This script tests the QA summary service functionality
"""

import asyncio
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.services.qa_summary import get_latest_qa_summary_by_user_id, get_qa_summaries_by_user_id
from app.models.qa_session_summary import QASessionSummary
from datetime import datetime

def test_qa_summary_service():
    """Test the QA summary service with sample data"""
    
    # Create a test database session
    db: Session = SessionLocal()
    
    try:
        print("=== Testing QA Summary Service ===\n")
        
        # Test 1: Check if QA summaries exist for user_id = 1
        print("Test 1: Getting latest QA summary for user_id = 1")
        latest_summary = get_latest_qa_summary_by_user_id(db, user_id=1)
        
        if latest_summary:
            print(f"✅ Found latest summary:")
            print(f"   Date: {latest_summary['date']}")
            print(f"   Summary: {latest_summary['summary'][:100]}...")
        else:
            print("❌ No QA summary found for user_id = 1")
        
        print()
        
        # Test 2: Check all QA summaries for user_id = 1
        print("Test 2: Getting all QA summaries for user_id = 1 (limit=5)")
        all_summaries = get_qa_summaries_by_user_id(db, user_id=1, limit=5)
        
        if all_summaries:
            print(f"✅ Found {len(all_summaries)} summaries:")
            for i, summary in enumerate(all_summaries, 1):
                print(f"   {i}. Date: {summary['date']}")
                print(f"      Summary: {summary['summary'][:80]}...")
        else:
            print("❌ No QA summaries found for user_id = 1")
        
        print()
        
        # Test 3: Check for non-existent user
        print("Test 3: Getting latest QA summary for non-existent user_id = 9999")
        non_existent_summary = get_latest_qa_summary_by_user_id(db, user_id=9999)
        
        if non_existent_summary:
            print(f"✅ Found summary for user 9999 (unexpected)")
        else:
            print("✅ Correctly returned None for non-existent user")
        
        print()
        
        # Test 4: Show total QA summaries in database
        print("Test 4: Database overview")
        total_summaries = db.query(QASessionSummary).count()
        print(f"   Total QA summaries in database: {total_summaries}")
        
        if total_summaries > 0:
            # Show unique user IDs
            user_ids = db.query(QASessionSummary.user_id).distinct().all()
            user_ids = [uid[0] for uid in user_ids]
            print(f"   Users with QA summaries: {user_ids}")
            
            # Show latest summary overall
            latest_overall = db.query(QASessionSummary).order_by(
                QASessionSummary.created_at.desc()
            ).first()
            
            if latest_overall:
                print(f"   Latest summary overall:")
                print(f"     User ID: {latest_overall.user_id}")
                print(f"     Date: {latest_overall.created_at}")
                print(f"     Type: {latest_overall.session_type}")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

def create_sample_data():
    """Create sample QA summary data for testing"""
    db: Session = SessionLocal()
    
    try:
        print("=== Creating Sample QA Summary Data ===\n")
        
        # Check if data already exists
        existing_count = db.query(QASessionSummary).count()
        if existing_count > 0:
            print(f"✅ Found {existing_count} existing QA summaries, skipping sample creation")
            return
        
        # Create sample QA summaries
        sample_summaries = [
            {
                "user_id": 1,
                "session_type": "base_condition",
                "summary": "Based on your responses, you have Type 2 diabetes diagnosed 3 years ago. Your current HbA1c is 7.2%, indicating good glucose control. You take Metformin 1000mg twice daily. No complications reported. Diet includes moderate carb intake and regular exercise.",
                "conversation_data": {"questions": 15, "duration_minutes": 12},
                "session_metadata": {"completion_status": "complete", "confidence": 0.92}
            },
            {
                "user_id": 1,
                "session_type": "onboarding",
                "summary": "Initial assessment shows mild hypertension (BP 135/85) and dietary concerns. BMI is 28.5 indicating overweight status. Goals include weight loss of 5-7kg and blood pressure reduction through DASH diet approach.",
                "conversation_data": {"questions": 20, "duration_minutes": 18},
                "session_metadata": {"completion_status": "complete", "confidence": 0.88}
            },
            {
                "user_id": 2,
                "session_type": "base_condition",
                "summary": "Patient has celiac disease diagnosed 5 years ago with excellent dietary compliance. Currently following strict gluten-free diet with good symptom control. No nutritional deficiencies detected in recent labs.",
                "conversation_data": {"questions": 12, "duration_minutes": 10},
                "session_metadata": {"completion_status": "complete", "confidence": 0.95}
            }
        ]
        
        for data in sample_summaries:
            qa_summary = QASessionSummary(**data)
            db.add(qa_summary)
        
        db.commit()
        print(f"✅ Created {len(sample_summaries)} sample QA summaries")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("QA Summary Service Test")
    print("=" * 50)
    
    # Create sample data if needed
    create_sample_data()
    
    # Run tests
    test_qa_summary_service()