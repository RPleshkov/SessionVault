from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router
from app.core.redis_service import init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await init_redis()
    app.state.redis = redis
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
