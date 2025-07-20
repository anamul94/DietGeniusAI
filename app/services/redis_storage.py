import json
import logging
from typing import List, Dict, Any, Optional
from app.db.redis import redis_client

logger = logging.getLogger(__name__)

class RedisQuestionStorage:
    """Service for storing and retrieving user questions in Redis."""
    
    @staticmethod
    def save_questions(user_id: str, question: str) -> bool:
        """
        Save a question string into a list stored as a JSON array in Redis.

        Args:
            user_id: The user ID
            question: A string representing the question data

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"{user_id}-qa"

            # Fetch existing list from Redis
            existing_data = redis_client.get(key)
            existing_questions = []

            if existing_data:
                try:
                    existing_questions = json.loads(existing_data)
                    if not isinstance(existing_questions, list):
                        existing_questions = []
                except json.JSONDecodeError:
                    logger.warning(f"Corrupted data for key {key}, starting fresh")
                    existing_questions = []

            # Append the new question string
            existing_questions.append(question)

            # Save back as JSON array
            redis_client.set(key, json.dumps(existing_questions))

            logger.info(f"✅ Saved question for user {user_id} (total: {len(existing_questions)})")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save question for user {user_id}: {e}")
            return False

    @staticmethod
    def get_questions(user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all questions for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of question objects
        """
        try:
            key = f"{user_id}-qa"
            data = redis_client.get(key)
            
            if not data:
                return []
            
            questions = json.loads(data)
            if isinstance(questions, list):
                return questions
            else:
                logger.warning(f"Invalid data format for key {key}, expected list")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to get questions for user {user_id}: {e}")
            return []
    
    @staticmethod
    def clear_questions(user_id: str) -> bool:
        """
        Clear all questions for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"{user_id}:qa"
            redis_client.delete(key)
            logger.info(f"✅ Cleared questions for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to clear questions for user {user_id}: {e}")
            return False
    
    @staticmethod
    def get_question_count(user_id: str) -> int:
        """
        Get the count of questions for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            Number of questions
        """
        return len(RedisQuestionStorage.get_questions(user_id))

# Create a singleton instance
question_storage = RedisQuestionStorage()