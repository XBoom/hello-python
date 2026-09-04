"""缓存层抽象 + 实现 + 工厂。

设计目标:
- 默认不依赖 Redis,无 `REDIS_URL` 时使用进程内 `InMemoryCache` 单例,带 WARN 日志。
- 配置 `REDIS_URL` 后切换到 `RedisCache`,使用 redis-py 原生 async 客户端。
- 接口最小集:get / set / delete / expire,便于在测试中用 fakeredis 替换真实 Redis。
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class Cache(ABC):
    """缓存抽象接口。"""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """取值,缺失或反序列化失败返回 None。"""

    @abstractmethod
    async def set(self, key: str, value: Any, expire: int | None = None) -> None:
        """写值。`expire` 单位为秒,None 表示不过期(对 InMemoryCache 仅本次进程有效)。"""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """删除键。键不存在视为幂等成功。"""

    @abstractmethod
    async def expire(self, key: str, seconds: int) -> None:
        """给已存在的键设置过期时间。键不存在时实现应保持幂等。"""

    @abstractmethod
    async def ping(self) -> bool:
        """健康检查。用于启动期连通性探测。"""

    @abstractmethod
    async def close(self) -> None:
        """释放底层连接。FastAPI lifespan 关闭期调用。"""


class InMemoryCache(Cache):
    """进程内缓存实现,使用 dict + 时间戳实现 TTL 过期。

    单实例 fallback:仅在 REDIS_URL 未配置时使用,重启即失效。
    """

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float | None]] = {}

    async def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if item is None:
            return None
        value, expire_at = item
        if expire_at is not None and expire_at <= time.monotonic():
            self._store.pop(key, None)
            return None
        return value

    async def set(self, key: str, value: Any, expire: int | None = None) -> None:
        expire_at = time.monotonic() + expire if expire else None
        self._store[key] = (value, expire_at)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    async def expire(self, key: str, seconds: int) -> None:
        item = self._store.get(key)
        if item is None:
            return
        value, _ = item
        self._store[key] = (value, time.monotonic() + seconds)

    async def ping(self) -> bool:
        return True

    async def close(self) -> None:
        self._store.clear()


class RedisCache(Cache):
    """Redis 缓存实现,基于 redis-py 原生 async 客户端。"""

    def __init__(self, client: Any, prefix: str = "hello-python") -> None:
        self._client = client
        self._prefix = prefix

    def _key(self, key: str) -> str:
        return f"{self._prefix}:{key}"

    async def get(self, key: str) -> Any | None:
        raw = await self._client.get(self._key(key))
        if raw is None:
            return None
        # 默认按 utf-8 解码;非字符串值由调用方自行序列化(JSON/Pickle 等)。
        if isinstance(raw, (bytes, bytearray)):
            return raw.decode("utf-8")
        return raw

    async def set(self, key: str, value: Any, expire: int | None = None) -> None:
        await self._client.set(self._key(key), value, ex=expire)

    async def delete(self, key: str) -> None:
        await self._client.delete(self._key(key))

    async def expire(self, key: str, seconds: int) -> None:
        await self._client.expire(self._key(key), seconds)

    async def ping(self) -> bool:
        try:
            return bool(await self._client.ping())
        except Exception:
            return False

    async def close(self) -> None:
        # redis.asyncio.Redis.close() 关闭连接池。
        close = getattr(self._client, "close", None)
        if close is not None:
            result = close()
            # 兼容 sync 与 async 两种实现。
            if hasattr(result, "__await__"):
                await result


_cache: Cache | None = None


def _build_cache() -> Cache:
    """根据 settings 构造缓存实例(单例工厂)。"""
    import redis.asyncio as redis_async

    if settings.REDIS_URL:
        client = redis_async.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
        logger.info("缓存: RedisCache 已初始化 url=%s prefix=%s", settings.REDIS_URL, settings.REDIS_KEY_PREFIX)
        return RedisCache(client=client, prefix=settings.REDIS_KEY_PREFIX)
    logger.warning("缓存: REDIS_URL 未配置,使用 InMemoryCache(进程内,重启失效)")
    return InMemoryCache()


def get_cache() -> Cache:
    """返回进程级缓存单例。"""
    global _cache
    if _cache is None:
        _cache = _build_cache()
    return _cache


def reset_cache_for_tests(cache: Cache | None = None) -> None:
    """测试钩子:替换或清空单例。仅供测试代码使用。"""
    global _cache
    _cache = cache


__all__ = [
    "Cache",
    "InMemoryCache",
    "RedisCache",
    "get_cache",
    "reset_cache_for_tests",
]
