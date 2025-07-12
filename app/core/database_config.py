from urllib.parse import urlparse
from typing import NamedTuple
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig(NamedTuple):
    host: str
    port: int
    database: str
    username: str
    password: str
    schema: str = "public"
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

def parse_database_url(url: str) -> DatabaseConfig:
    """Parse DATABASE_URL into components"""
    parsed = urlparse(url)
    return DatabaseConfig(
        host=parsed.hostname or "localhost",
        port=parsed.port or 5432,
        database=parsed.path.lstrip('/') if parsed.path else "",
        username=parsed.username or "",
        password=parsed.password or "",
        schema="public"
    )

def get_database_config() -> DatabaseConfig:
    """Get database configuration from environment"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")
    
    return parse_database_url(database_url)