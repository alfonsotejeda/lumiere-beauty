import json
import redis.asyncio as redis
from app.config import settings

_redis: redis.Redis | None = None

async def connect_cache() -> None:
    global _redis
    _redis = redis.from_url(settings.valkey_url, decode_responses=True)

async def close_cache() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None

async def cache_get(key: str) -> dict | list | None:
    if not _redis:
        return None
    value = await _redis.get(key)
    return json.loads(value) if value else None

async def cache_set(key: str, value: dict | list, ttl: int | None = None) -> None:
    if not _redis:
        return
    await _redis.set(key, json.dumps(value, default=str), ex=ttl or settings.cache_ttl_seconds)

async def cache_delete(key: str) -> None:
    if not _redis:
        return
    await _redis.delete(key)
