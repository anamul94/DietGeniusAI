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

    @staticmethod
    def delete_user_data(user_id: str, data_type: str = "qa") -> bool:
        """
        Delete user data from Redis by user ID and data type.
        
        Args:
            user_id: The user ID
            data_type: Type of data to delete (default: "qa" for questions)
                      Can be "qa", "profile", "preferences", etc.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key = f"{user_id}-{data_type}"
            result = redis_client.delete(key)
            
            if result == 1:
                logger.info(f"✅ Deleted {data_type} data for user {user_id}")
                return True
            else:
                logger.info(f"ℹ️ No {data_type} data found for user {user_id}")
                return True  # Return True even if key didn't exist
            
        except Exception as e:
            logger.error(f"❌ Failed to delete {data_type} data for user {user_id}: {e}")
            return False

    @staticmethod
    def delete_all_user_data(user_id: str) -> Dict[str, bool]:
        """
        Delete all Redis data associated with a user ID.
        
        Args:
            user_id: The user ID
            
        Returns:
            Dict[str, bool]: Dictionary with deletion results for each data type
        """
        data_types = ["qa", "profile", "preferences", "settings", "cache"]
        results = {}
        
        for data_type in data_types:
            results[data_type] = RedisQuestionStorage.delete_user_data(user_id, data_type)
        
        logger.info(f"✅ Completed deletion of all data for user {user_id}")
        return results

# Create a singleton instance
question_storage = RedisQuestionStorage()