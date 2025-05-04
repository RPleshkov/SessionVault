from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router
from app.core.redis_service import init_redis
from fastapi_limiter import FastAPILimiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await init_redis()
    await FastAPILimiter.init(redis)
    app.state.redis = redis
    yield
    await redis.close()
    await FastAPILimiter.close()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
