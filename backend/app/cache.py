import redis.asyncio as aioredis
import os

_client = None


def get_redis() -> aioredis.Redis:
    """
    Returns a shared async Redis client.
    Connection is lazy — no real socket until first command.
    """
    global _client
    if _client is None:
        _client = aioredis.from_url(
            os.environ["REDIS_URL"],
            decode_responses=True,   # return str, not bytes
            socket_connect_timeout=5,
        )
    return _client


NOTES_CACHE_KEY = "notes:all"
CACHE_TTL_SECONDS = 60