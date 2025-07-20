#!/usr/bin/env python3
"""
Test script to verify Redis question storage functionality
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.redis_storage import question_storage

def test_redis_storage():
    """Test the Redis question storage functionality."""
    
    test_user_id = "test_user_123"
    
    # Clear any existing data
    question_storage.clear_questions(test_user_id)
    print("✅ Cleared existing test data")
    
    # Test data
    test_questions = [
        {
            "question_text": "What is your age?",
            "input_type": "number",
            "options": [],
            "placeholder": "Enter your age",
            "additional_context": "We need this for personalized recommendations"
        },
        {
            "question_text": "What is your dietary preference?",
            "input_type": "radio",
            "options": ["Vegetarian", "Non-vegetarian", "Vegan"],
            "placeholder": "Select your preference",
            "additional_context": "This helps us suggest appropriate meals"
        }
    ]
    
    # Test saving questions
    print("📝 Testing save_questions...")
    success = question_storage.save_questions(test_user_id, test_questions)
    if success:
        print("✅ Questions saved successfully")
    else:
        print("❌ Failed to save questions")
        return False
    
    # Test retrieving questions
    print("📖 Testing get_questions...")
    retrieved_questions = question_storage.get_questions(test_user_id)
    print(f"✅ Retrieved {len(retrieved_questions)} questions")
    
    # Test appending more questions
    print("➕ Testing append functionality...")
    more_questions = [
        {
            "question_text": "Any food allergies?",
            "input_type": "checkbox",
            "options": ["Nuts", "Dairy", "Gluten", "None"],
            "placeholder": "Select all that apply",
            "additional_context": "Important for safety"
        }
    ]
    
    success = question_storage.save_questions(test_user_id, more_questions)
    if success:
        print("✅ Additional questions appended successfully")
    
    # Test final count
    final_questions = question_storage.get_questions(test_user_id)
    print(f"✅ Final question count: {len(final_questions)}")
    
    # Display questions
    print("\n📋 All Questions:")
    for i, q in enumerate(final_questions, 1):
        print(f"{i}. {q['question_text']} ({q['input_type']})")
    
    # Test count function
    count = question_storage.get_question_count(test_user_id)
    print(f"✅ Question count via function: {count}")
    
    # Clean up
    question_storage.clear_questions(test_user_id)
    print("✅ Test data cleaned up")
    
    return True

if __name__ == "__main__":
    print("Testing Redis question storage...")
    try:
        success = test_redis_storage()
        if success:
            print("\n🎉 All tests passed!")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        sys.exit(1)