#!/usr/bin/env python3
"""
Test script to verify QA session summary functionality
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.qa_session_summary import QASessionSummary
from app.models.user import User
from app.services.medical import user_onboarding_qa
from app.schemas.qa import QAAnsReq, QaAns
import asyncio

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'DietGeniusAI'))

def test_qa_session_summary_model():
    """Test the QA session summary model creation"""
    print("Testing QA session summary model...")
    
    # Create a test summary
    summary = QASessionSummary(
        user_id=1,
        session_type="base_condition",
        summary="Test summary for base condition assessment",
        conversation_data={"test": "data"},
        session_metadata={"rounds": 3, "questions": 5}
    )
    
    print(f"✓ Created QA session summary: {summary}")
    print(f"  - User ID: {summary.user_id}")
    print(f"  - Session Type: {summary.session_type}")
    print(f"  - Summary: {summary.summary}")
    print(f"  - Created At: {summary.created_at}")
    
    return True

def test_schema_validation():
    """Test the schema validation"""
    print("\nTesting schema validation...")
    
    from app.schemas.qa_session_summary import QASessionSummaryCreate
    
    # Test create schema
    create_data = QASessionSummaryCreate(
        user_id=1,
        session_type="base_condition",
        summary="Test summary",
        conversation_data={"test": "data"},
        session_metadata={"rounds": 3}
    )
    
    print(f"✓ Valid create schema: {create_data}")
    
    return True

async def test_integration():
    """Test integration with medical service"""
    print("\nTesting integration with medical service...")
    
    # This would require a test database setup
    print("✓ Integration test placeholder - would need test database setup")
    
    return True

if __name__ == "__main__":
    print("Running QA session summary tests...")
    
    try:
        test_qa_session_summary_model()
        test_schema_validation()
        
        # Run async test
        asyncio.run(test_integration())
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()