from fastapi import APIRouter

from app.api.v1.endpoints import auth, cache_demo, health, users
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)

# Cache 演示接口仅在 DEBUG 模式下挂载,生产环境自动隐藏。
if settings.DEBUG:
    api_router.include_router(cache_demo.router)
