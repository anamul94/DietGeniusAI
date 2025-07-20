#!/usr/bin/env python3
"""
Example showing how to use Redis storage with response["questions"]
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.redis_storage import question_storage

def example_usage():
    """Example of how to save response["questions"] to Redis."""
    
    # Example response structure
    response = {
        "data": {
            "questions": [
                {
                    "question_text": "What is your current weight?",
                    "input_type": "number",
                    "options": [],
                    "placeholder": "Enter weight in kg",
                    "additional_context": "Used for BMI calculation"
                },
                {
                    "question_text": "What is your activity level?",
                    "input_type": "radio",
                    "options": ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"],
                    "placeholder": "Select your activity level",
                    "additional_context": "Helps determine calorie needs"
                }
            ],
            "is_complete": False,
            "message_on_completion": "Thank you for completing the assessment!"
        },
        "count": 2,
        "summary": "Initial assessment questions"
    }
    
    # Extract questions from response
    questions = response["data"]["questions"]
    
    # User ID (this would come from your authentication system)
    user_id = "user_12345"
    
    # Save questions to Redis
    success = question_storage.save_questions(user_id, questions)
    
    if success:
        print(f"✅ Successfully saved {len(questions)} questions for user {user_id}")
        
        # Retrieve questions to verify
        saved_questions = question_storage.get_questions(user_id)
        print(f"📋 Retrieved {len(saved_questions)} questions from Redis")
        
        # Display saved questions
        for i, q in enumerate(saved_questions, 1):
            print(f"{i}. {q['question_text']} ({q['input_type']})")
        
        # Clean up
        question_storage.clear_questions(user_id)
        print("✅ Cleaned up test data")
        
    else:
        print("❌ Failed to save questions")

if __name__ == "__main__":
    print("Redis storage usage example")
    example_usage()