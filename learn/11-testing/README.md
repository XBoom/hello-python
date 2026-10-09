# 11 · 测试（pytest、httpx、依赖覆盖）

## 本章目标

能给新接口补一条异步测试，并说清为什么测试库不是磁盘上的 `app.db`。

## 原理

pytest 收集 `test_*.py` 里的 `test_*`。本项目 `asyncio_mode = auto`，`async def test_xxx` 会在 event loop 里跑。夹具默认 function 作用域，避免测试之间共用同一个内存库或 loop。

测 FastAPI 不要真开端口：`httpx.AsyncClient` + `ASGITransport(app=app)` 在进程内走 ASGI，和真实中间件/依赖链一致。

`app.dependency_overrides[get_db] = override_get_db`：请求里的 `Depends(get_db)` 换成内存 SQLite 的 Session。这是官方推荐的替换点，比 patch 整个 `UserService` 更能测到路由+校验+事务。

测试库用 `sqlite+aiosqlite:///:memory:` + `create_all`：快、隔离、无 Alembic 版本表。**它不证明 Postgres 迁移能跑通**；那是另一类测试（可在 CI 加 Postgres service）。本模板选择：接口行为用 SQLite，迁移靠开发者/compose 在 Postgres 上跑。

`httpx` 是同步/异步 HTTP 客户端；测试里当「假浏览器」。生产业务若要调外部 HTTP，也应优先异步客户端，避免堵 loop。

## 最佳实践

- 一个测试一个行为：重复邮箱、错密码、无 token，分开写。
- 同时断言 HTTP 状态和信封 `code`。
- 不要依赖本机 8000 端口是否已启动。
- 新模型必须 export，否则内存库没表。
- 超管测试不要走「注册接口提权」；应改库字段或专用夹具。
- CI 与本地同一条 `pytest` 命令。

## 本项目落地

- 配置：`pyproject.toml` 的 `[tool.pytest.ini_options]`
- 夹具：`tests/conftest.py`
- 用例：`tests/test_health.py`、`tests/test_auth.py`
- 规范：`docs/testing.md`

## 动手

1. 跑 `make test`，再故意把注册密码改短，看 422 测试要怎么写。
2. 读 FastAPI [Testing](https://fastapi.tiangolo.com/tutorial/testing/)。

## 下一章

[12 Ruff](../12-ruff/)
