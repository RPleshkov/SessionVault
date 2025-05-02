from fastapi import APIRouter

from app.api.v1.auth_router import router as auth_router
from app.api.v1.health_router import router as health_router
from app.api.v1.registration_router import router as registration_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(registration_router)
v1_router.include_router(auth_router)
v1_router.include_router(health_router)
