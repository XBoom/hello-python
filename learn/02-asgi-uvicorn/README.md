# 02 · ASGI、Starlette 与 Uvicorn

## 本章目标

说清 WSGI 和 ASGI 的差别，以及 FastAPI 为什么「跑在 Uvicorn 上」却大量 API 来自 Starlette。

## 原理

传统 Python Web（Flask/Django 同步视图）走 **WSGI**：一个 worker 一次处理一个请求直到结束。并发靠多进程/多线程。

**ASGI**（Asynchronous Server Gateway Interface）把「接收连接、收请求体、发响应」做成 awaitable 调用。同一进程里可以同时挂起成千上万个等 I/O 的请求。协议文档：[ASGI](https://asgi.readthedocs.io/en/latest/)。

栈从下到上：

```text
Uvicorn     进程、HTTP、WebSocket、lifespan 事件，把字节变成 ASGI scope/receive/send
Starlette   路由、中间件、Request/Response、CORS、静态文件、异常
FastAPI     在 Starlette 上加：Pydantic 校验、依赖注入、OpenAPI
```

所以：

- `app.add_middleware(CORSMiddleware)` 是 **Starlette** 中间件。后 `add` 的先执行（洋葱模型：后注册的在外层）。
- `Request`、`JSONResponse`、`HTTPException` 也来自 Starlette 体系。
- Uvicorn 的 `app.main:app` 只要对象实现 ASGI 接口（`async def __call__(scope, receive, send)`）即可。

`--host 0.0.0.0`：在容器里监听所有网卡，宿主机端口映射才能进来。绑 `127.0.0.1` 则只有容器内部能访问。

`uvicorn[standard]` 会带上 uvloop、httptools 等更快的实现。

## 最佳实践

- 开发用 `--reload`，生产不要 reload（文件监控浪费且行为不确定）。
- 生产用多 worker 时注意：**内存里的全局状态不共享**；本项目 Session/引擎按进程各一份，这是对的。
- 中间件只做横切（请求 ID、CORS、鉴权网关），不要在中间件里写业务 SQL。
- 不要同时开 Uvicorn 自己的 access log 和业务 access log，会重复。本项目关掉了 `uvicorn.access`，由 `RequestContextMiddleware` 打一条。

## 本项目落地

- 启动：`Makefile` 的 `make dev` → `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
- 中间件顺序见 `app/main.py`：先加 `RequestContextMiddleware`（内层），再加 CORS（外层）
- `app/core/middleware.py`：基于 `BaseHTTPMiddleware`，写入 `X-Request-ID` 与耗时日志

## 动手

1. 把 `--host` 改成 `127.0.0.1` 在 Docker 里跑一次，体会「映射了端口却连不上」。
2. 读 Starlette 文档 [Middleware](https://www.starlette.io/middleware/) 里关于调用顺序的说明。

## 下一章

[03 FastAPI](../03-fastapi/)
