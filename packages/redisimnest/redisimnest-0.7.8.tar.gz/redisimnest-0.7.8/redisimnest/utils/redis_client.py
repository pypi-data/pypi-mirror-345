import os
import redis.asyncio as aioredis
from ..settings import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_USERNAME,
    REDIS_PASS,
)

class RedisManager:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = aioredis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                username=REDIS_USERNAME,
                password=REDIS_PASS,
                decode_responses=True
            )
        return cls._client

    @classmethod
    async def close_client(cls):
        if cls._client:
            await cls._client.aclose()
            cls._client = None
