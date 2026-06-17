import json
import logging
import time
from typing import Any

import redis.asyncio as redis

from toutiao_backend.config.settings import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)
redis_retry_after = 0.0

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
    retry_on_timeout=False,
)


def redis_is_available() -> bool:
    return time.monotonic() >= redis_retry_after


def mark_redis_unavailable() -> None:
    global redis_retry_after
    redis_retry_after = time.monotonic() + settings.cache_retry_interval


async def get_cache(key: str) -> str | None:
    if not redis_is_available():
        return None

    try:
        return await redis_client.get(key)
    except Exception as exc:
        mark_redis_unavailable()
        logger.warning("Cache read failed: %s", exc)
        return None


async def get_json_cache(key: str) -> dict[str, Any] | list[Any] | None:
    if not redis_is_available():
        return None

    try:
        data = await redis_client.get(key)
        return json.loads(data) if data else None
    except Exception as exc:
        mark_redis_unavailable()
        logger.warning("JSON cache read failed: %s", exc)
        return None


async def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    if not redis_is_available():
        return False

    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        await redis_client.setex(key, expire, value)
        return True
    except Exception as exc:
        mark_redis_unavailable()
        logger.warning("Cache write failed: %s", exc)
        return False
