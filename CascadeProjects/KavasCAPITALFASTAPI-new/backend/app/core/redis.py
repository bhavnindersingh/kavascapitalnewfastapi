from redis.asyncio import Redis
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_redis = None

async def init_redis():
    """Initialize Redis connection"""
    global _redis
    try:
        if not _redis:
            _redis = Redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await _redis.ping()
            logger.info("Redis connection initialized")
        return _redis
    except Exception as e:
        logger.error(f"Failed to initialize Redis connection: {str(e)}")
        raise

async def get_redis():
    """Get Redis connection"""
    if not _redis:
        await init_redis()
    return _redis

async def close_redis():
    """Close Redis connection"""
    global _redis
    if _redis:
        await _redis.close()
        _redis = None
        logger.info("Redis connection closed")
