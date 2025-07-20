from redis import Redis, RedisError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    socket_connect_timeout=5,
    socket_timeout=5
)

def check_redis_connection() -> bool:
    """Check if Redis connection is available during startup."""
    try:
        # Test connection with ping
        redis_client.ping()
        logger.info(f"✅ Redis connection successful: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        return True
    except RedisError as e:
        logger.error(f"❌ Redis connection failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error checking Redis: {e}")
        return False