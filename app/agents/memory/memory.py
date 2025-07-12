from agno.memory.v2.db.postgres import PostgresMemoryDb
from agno.memory.v2.memory import Memory, MemoryManager, SessionSummarizer
from agno.models.base import Model
from typing import Optional
from app.core.database_config import get_database_config
import os


def get_memory_with_manager(memory_model:Optional[Model] = None,
                                  memory_manager_model:Optional[Model] = None,
                                  system_message: str | None = None,
                                  memory_capture_instructions: str | None = None,
                                 additional_instructions: str | None = None)->Memory:
    
    
    
    db_config = get_database_config()
    memory_table = os.getenv("USER_MEMORY_TABLE", "user_memory")
    
    memory_db = PostgresMemoryDb(
        table_name=memory_table,
        schema=db_config.schema,
        db_url=db_config.url
    )
    memory_manager =  MemoryManager(
        model=memory_manager_model,
        system_message=system_message,
        memory_capture_instructions=memory_capture_instructions,
        additional_instructions=additional_instructions,
    )
    return Memory(
        model=memory_model,
        memory_manager=memory_manager,
        db=memory_db
    )



