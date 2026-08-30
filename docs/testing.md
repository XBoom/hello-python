# 测试规范

## 采用的外部规范

- [pytest 文档](https://docs.pytest.org/en/stable/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- FastAPI 测试方式：[TestClient / HTTPX](https://fastapi.tiangolo.com/zh/tutorial/testing/)（本项目用 `httpx.AsyncClient` + `ASGITransport`）

## 原则

- 默认写**接口测试**：从 HTTP 打进去，覆盖路由、校验、鉴权、事务。
- 一个测试函数只断言一件行为，函数名 `test_<场景>`。
- 不依赖本机正在跑的 Uvicorn，不依赖外部 Postgres（单元/接口测试用内存 SQLite）。
- 不 Mock 掉整个 service 层来「保证路由能 import」；要 Mock 的是不稳定的外部 HTTP / 邮件等。

## 目录与命名

- 测试放 `tests/`，文件 `test_<模块>.py`。
- 共享夹具只放 `tests/conftest.py`。
- 不要把测试数据写进仓库里的真实 `.env`。

## 数据库夹具

`client` 夹具：

1. 使用 `sqlite+aiosqlite:///:memory:`
2. `Base.metadata.create_all`（仅测试，生产仍走 Alembic）
3. `app.dependency_overrides[get_db] = ...`
4. 测试结束 `overrides.clear()` 并 `engine.dispose()`

新模型必须在 `app.models` 导出，否则内存库没有表。

需要超管时：注册普通用户后，在测试里单独开 session 改 `is_superuser`，或抽一个 `superuser_client` 夹具，不要把「提权」写进产品注册接口。

## 断言

- 同时看 HTTP 状态码和信封里的 `code`。
- 鉴权用例：无 token、坏 token、过期、普通用户打超管接口。
- 冲突用例：重复邮箱 409 / `ErrorCode.EMAIL_EXISTS`。
- 不要只 `assert resp.status_code == 200` 而不看 `data`。

## 异步

- `pyproject.toml` 中 `asyncio_mode = auto`，测试函数 `async def` 即可。
- 夹具作用域保持 `function`，避免跨测试共用同一个 event loop / 内存库状态。

## 运行

```bash
make test
# 或
pytest -v
pytest tests/test_auth.py -q
```

PR 与 CI（`.github/workflows/ci.yml`）跑 lint + 全量 pytest。新行为没有测试不要合入。
