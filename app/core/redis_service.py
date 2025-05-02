from datetime import timedelta
import json
from typing import Any

from fastapi import Request
from redis.asyncio import Redis

from app.core.settings import settings


async def init_redis() -> Redis:
    redis = Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db,
        username=settings.redis.user,
        password=settings.redis.password,
        decode_responses=True,
        encoding="utf-8",
    )
    return redis


class RedisService:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def set(self, name: str, value: Any, ex: int | timedelta) -> None:
        await self.redis.set(
            name=name, value=json.dumps(value, ensure_ascii=True), ex=ex
        )

    async def get(self, name: str) -> Any | None:
        value = await self.redis.get(name=name)

        if value is None:
            return None

        return json.loads(value)

    async def keys(self) -> list[str] | list:
        return await self.redis.keys()

    async def delete(self, name: str) -> None:
        await self.redis.delete(name)


async def get_redis(request: Request) -> RedisService:
    redis = request.app.state.redis
    return RedisService(redis=redis)
