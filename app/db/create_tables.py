from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database_config import get_database_config
from app.db.base import Base

# Get database configuration
db_config = get_database_config()

# Create engine with proper configuration
engine = create_engine(
    db_config.url,
    pool_pre_ping=True,
    pool_recycle=300
)

def create_all_tables():
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)