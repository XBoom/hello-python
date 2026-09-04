"""Cache 演示接口。

仅在 `DEBUG=True` 时挂载,便于本地演示 cache.get / cache.set 的命中与未命中。
"""

import time

from fastapi import APIRouter

from app.core.cache import get_cache
from app.schemas.common import Response, ok

router = APIRouter(tags=["cache-demo"])


@router.get("/cache-demo/ping", response_model=Response[dict])
async def cache_ping() -> dict:
    """第一次调用写入缓存,后续调用命中缓存。

    返回 `source` 字段:`miss` 表示新写入,`hit` 表示从缓存读取。
    """
    cache = get_cache()
    cached = await cache.get("demo:ping")
    if cached is not None:
        return ok({"source": "hit", "value": cached})
    payload = {"message": "pong", "timestamp": time.time()}
    await cache.set("demo:ping", payload, expire=60)
    return ok({"source": "miss", "value": payload})
