"""F10 缓存层测试。

覆盖:
- InMemoryCache: get/set/delete/expire + 过期语义
- RedisCache: 用 fakeredis 替代真实 Redis(避免测试依赖真 Redis)
- get_cache() 工厂:无 REDIS_URL → InMemoryCache;有 REDIS_URL → RedisCache
- /cache-demo/ping 端点:第一次返回 miss,第二次返回 hit
"""

from __future__ import annotations

import asyncio
import time

import fakeredis.aioredis
import pytest
from httpx import AsyncClient

from app.core import cache as cache_module
from app.core.cache import (
    InMemoryCache,
    RedisCache,
    get_cache,
    reset_cache_for_tests,
)
from app.core.config import Settings
from app.main import app


# -------------------- InMemoryCache --------------------


@pytest.mark.asyncio
async def test_in_memory_set_get() -> None:
    cache = InMemoryCache()
    await cache.set("k1", "v1")
    assert await cache.get("k1") == "v1"


@pytest.mark.asyncio
async def test_in_memory_get_missing_returns_none() -> None:
    cache = InMemoryCache()
    assert await cache.get("missing") is None


@pytest.mark.asyncio
async def test_in_memory_delete() -> None:
    cache = InMemoryCache()
    await cache.set("k1", "v1")
    await cache.delete("k1")
    assert await cache.get("k1") is None
    # 重复删除幂等
    await cache.delete("k1")


@pytest.mark.asyncio
async def test_in_memory_expire() -> None:
    cache = InMemoryCache()
    await cache.set("k1", "v1")
    await cache.expire("k1", 1)
    # 立即读取应命中
    assert await cache.get("k1") == "v1"
    # 模拟 1.1 秒后过期(用 monkey patch 加速)
    original = time.monotonic
    cache_module.time.monotonic = lambda: original() + 1.1  # type: ignore[assignment]
    try:
        assert await cache.get("k1") is None
    finally:
        cache_module.time.monotonic = original  # type: ignore[assignment]


@pytest.mark.asyncio
async def test_in_memory_set_with_expire_expires() -> None:
    cache = InMemoryCache()
    await cache.set("k1", "v1", expire=1)
    original = time.monotonic
    cache_module.time.monotonic = lambda: original() + 1.1  # type: ignore[assignment]
    try:
        assert await cache.get("k1") is None
    finally:
        cache_module.time.monotonic = original  # type: ignore[assignment]


@pytest.mark.asyncio
async def test_in_memory_ping() -> None:
    cache = InMemoryCache()
    assert await cache.ping() is True


# -------------------- RedisCache (fakeredis) --------------------


@pytest.mark.asyncio
async def test_redis_set_get_with_prefix() -> None:
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    cache = RedisCache(client=fake, prefix="hp-test")
    await cache.set("k1", "v1")
    assert await cache.get("k1") == "v1"
    # 验证 key 前缀生效
    assert await fake.get("hp-test:k1") == "v1"
    await cache.close()


@pytest.mark.asyncio
async def test_redis_set_with_ttl() -> None:
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    cache = RedisCache(client=fake, prefix="hp-test")
    await cache.set("k1", "v1", expire=60)
    assert await fake.ttl("hp-test:k1") > 0
    await cache.close()


@pytest.mark.asyncio
async def test_redis_delete() -> None:
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    cache = RedisCache(client=fake, prefix="hp-test")
    await cache.set("k1", "v1")
    await cache.delete("k1")
    assert await cache.get("k1") is None
    await cache.close()


@pytest.mark.asyncio
async def test_redis_expire() -> None:
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    cache = RedisCache(client=fake, prefix="hp-test")
    await fake.set("hp-test:k1", "v1")
    await cache.expire("k1", 120)
    assert await fake.ttl("hp-test:k1") > 0
    await cache.close()


@pytest.mark.asyncio
async def test_redis_ping() -> None:
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    cache = RedisCache(client=fake, prefix="hp-test")
    assert await cache.ping() is True
    await cache.close()


# -------------------- get_cache() 工厂 --------------------


def test_factory_returns_in_memory_when_redis_url_is_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """REDIS_URL 为 None 时,工厂返回 InMemoryCache。"""
    reset_cache_for_tests(None)
    fake_settings = Settings(REDIS_URL=None)
    monkeypatch.setattr(cache_module, "settings", fake_settings)
    reset_cache_for_tests(None)
    cache = get_cache()
    assert isinstance(cache, InMemoryCache)
    reset_cache_for_tests(None)


def test_factory_returns_redis_when_redis_url_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    """REDIS_URL 配置时,工厂返回 RedisCache。"""
    fake_settings = Settings(REDIS_URL="redis://localhost:6379/0")
    monkeypatch.setattr(cache_module, "settings", fake_settings)
    reset_cache_for_tests(None)
    cache = get_cache()
    assert isinstance(cache, RedisCache)
    # 清理:换回无 Redis URL 状态,避免污染后续测试
    reset_cache_for_tests(None)
    monkeypatch.setattr(cache_module, "settings", Settings(REDIS_URL=None))


# -------------------- /cache-demo/ping endpoint --------------------


@pytest.mark.asyncio
async def test_cache_demo_first_miss_second_hit(client: AsyncClient) -> None:
    """第一次调用 source=miss,第二次 source=hit。"""
    reset_cache_for_tests(InMemoryCache())
    try:
        # 清空可能残留的缓存键
        cache = get_cache()
        await cache.delete("demo:ping")

        resp1 = await client.get("/api/v1/cache-demo/ping")
        assert resp1.status_code == 200
        body1 = resp1.json()
        assert body1["code"] == 0
        assert body1["data"]["source"] == "miss"

        resp2 = await client.get("/api/v1/cache-demo/ping")
        assert resp2.status_code == 200
        body2 = resp2.json()
        assert body2["data"]["source"] == "hit"
    finally:
        await cache.delete("demo:ping")
        reset_cache_for_tests(None)
