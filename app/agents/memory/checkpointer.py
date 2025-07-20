"""
Generic checkpointer module for LangGraph applications.
Provides reusable checkpointer instances for different storage backends.
"""

from typing import Optional
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from app.core.config import Settings
import psycopg
from psycopg import Connection

settings = Settings()

class CheckpointerManager:
    """Manages checkpointer instances for different use cases."""
    
    _instances = {}
    
    @classmethod
    def get_postgres_checkpointer(
        cls,
        connection_string: Optional[str] = None,
        table_name: str = "checkpoints",
        schema: str = "public",
        connection_kwargs: Optional[dict] = None
    ) -> PostgresSaver:
        """
        Get a Postgres checkpointer instance.
        
        Args:
            connection_string: Database connection string. Defaults to settings.DATABASE_URL
            table_name: Name of the checkpoint table
            schema: Database schema name
            connection_kwargs: Additional psycopg connection parameters
            
        Returns:
            PostgresSaver instance
        """
        cache_key = f"postgres_{schema}_{table_name}"
        
        if cache_key not in cls._instances:
            conn_str = connection_string or settings.DATABASE_URL
            conn_kwargs = connection_kwargs or {
                "autocommit": True,
                "prepare_threshold": 0,
            }
            
            conn = Connection.connect(conn_str, **conn_kwargs)
            checkpointer = PostgresSaver(conn)
            checkpointer.setup()
            
            cls._instances[cache_key] = checkpointer
            
        return cls._instances[cache_key]
    
    @classmethod
    def get_default_checkpointer(cls) -> PostgresSaver:
        """Get the default checkpointer using DATABASE_URL."""
        return cls.get_postgres_checkpointer()
    
    @classmethod
    def reset_instance(cls, checkpointer_type: str = "postgres"):
        """Reset cached instance for testing purposes."""
        keys_to_remove = [k for k in cls._instances.keys() if k.startswith(checkpointer_type)]
        for key in keys_to_remove:
            del cls._instances[key]

# Convenience function for backward compatibility
def get_checkpointer(
    connection_string: Optional[str] = None,
    table_name: str = "checkpoints",
    schema: str = "public"
) -> PostgresSaver:
    """
    Get a default Postgres checkpointer.
    
    Args:
        connection_string: Database connection string
        table_name: Name of the checkpoint table
        schema: Database schema name
        
    Returns:
        PostgresSaver instance
    """
    return CheckpointerManager.get_postgres_checkpointer(
        connection_string=connection_string,
        table_name=table_name,
        schema=schema
    )