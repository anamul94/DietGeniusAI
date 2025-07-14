from app.core.database_config import get_database_config
from app.core.config import settings
import os

from agno.storage.postgres import PostgresStorage

db_url = get_database_config().url

USER_DAILY_LOG_SESSION_TABLE = settings.USER_DAILY_LOG_SESSION_TABLE
GENERAL_SESSION_TABLE = settings.GENERAL_SESSION_TABLE


USER_DAILY_LOG_SESSION_STORAGE = PostgresStorage(
    table_name=USER_DAILY_LOG_SESSION_TABLE,
    db_url=db_url,
    
)

GENERAL_SESSION_STORAGE = PostgresStorage(
    table_name=GENERAL_SESSION_TABLE,
    db_url=db_url,
)