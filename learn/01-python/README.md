# 01 · Python 3.12、类型与异步

## 本章目标

看懂本仓库里的 `X | None`、`Annotated`、`async def`、`AsyncGenerator`，并知道为什么不要在协程里写阻塞调用。

## 原理

### 版本

`requires-python = ">=3.12"`。3.12 起可以：

- 内置泛型：`list[str]`，不必 `from typing import List`
- 联合：`str | None`
- PEP 695 泛型类：`class Response[T]`、`class BaseRepository[ModelT: Base]`

类型注解默认不在运行时执行（除非用 `from __future__ import annotations` 或 Pydantic 那种会读注解的库）。它们主要给人和检查器看；FastAPI / Pydantic 会**读取**函数和模型上的注解来做校验和 OpenAPI。

### 异步

`async def` 定义协程。调用它得到的是 coroutine 对象，必须 `await` 才会跑。事件循环（Uvicorn 里是 uvloop 或默认 loop）在等待数据库/网络时可以去处理别的请求——这就是「高并发 I/O」的来源。

若在协程里调用阻塞函数（同步 `time.sleep`、同步 HTTP、CPU 死循环），**整个 event loop 卡住**，所有请求一起停。SQLAlchemy 异步 API、`httpx.AsyncClient`、`asyncpg` 都是为了把等待交还给循环。

`async with` / `async for` 对应带 `__aenter__` / `__anext__` 的对象。`get_db` 是 `AsyncGenerator`：FastAPI 在依赖里 `yield` 前后插入进入/退出逻辑。

### 包与环境

系统 Python（尤其 Homebrew 的 3.14）常是 PEP 668 托管环境，不能直接 `pip install`。用 **venv** 或 **uv** 隔离。本项目用 `pyproject.toml` 声明依赖，`pip install -e ".[dev]"` 可编辑安装，改 `app/` 不必重装包。

## 最佳实践

- 公共函数写返回类型；用 `Annotated[T, Depends(...)]` 给 FastAPI 叠依赖，而不是靠默认参数魔法让读者猜。
- I/O 全异步；阻塞调用放到 `asyncio.to_thread` 或干脆不要出现在请求路径。
- 时间用带时区的 `datetime.now(UTC)`，不要天真本地时间。
- 风格交给 Ruff，不要争论空格（见 [12 Ruff](../12-ruff/)）。

## 本项目落地

- `app/schemas/common.py`：`class Response[T]`、`class PageResult[T]`
- `app/repositories/base.py`：`class BaseRepository[ModelT: Base]`
- `app/api/deps.py`：`CurrentUser = Annotated[User, Depends(get_current_user)]`
- `app/db/session.py`：`async def get_db() -> AsyncGenerator[AsyncSession, None]`

## 动手

1. 把某个 `async def` 里的 `await` 删掉试跑测试，看失败长什么样（做完还原）。
2. 读 [PEP 8](https://peps.python.org/pep-0008/) 命名一节，对照 `docs/python.md` 的差异表（行宽 88、双引号）。

## 下一章

[02 ASGI 与 Uvicorn](../02-asgi-uvicorn/)
