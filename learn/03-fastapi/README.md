# 03 · FastAPI

## 本章目标

理解路由、依赖注入、lifespan、异常处理器如何拼成一次请求，并能在本仓库里找到对应代码。

## 原理

FastAPI 把「函数签名」当成契约：参数来自路径、Query、Header、Body 还是 `Depends`，由类型和默认值决定。返回值经 `response_model` 过滤后再序列化。

### 依赖注入（Depends）

`Depends(get_db)` 表示：先执行 `get_db`，把它的返回值（或 yield 的值）传给下游。依赖可以嵌套：`get_current_user` 依赖 `get_db` 和 `HTTPBearer`。同一请求内相同依赖默认缓存，不会把 `get_db` 打开两次。

`yield` 型依赖：函数在 `yield` 处把控制权交给路由；路由返回后，生成器继续执行 `yield` 之后的代码（commit / rollback / 关连接）。这是请求级事务的挂钩点。

### lifespan

旧的 `@app.on_event("startup")` 已不推荐。`lifespan` 是一个 async context manager：`yield` 前是启动（本项目 `setup_logging()`），`yield` 后是关闭（`engine.dispose()`）。Uvicorn 发 ASGI lifespan 事件时触发。

### 异常处理

未捕获的异常按**注册的类型**从精确到宽泛匹配。本项目：

1. `AppError` → 业务信封
2. `RequestValidationError` → 422 + Pydantic errors
3. `StarletteHTTPException` → 框架 HTTP 错误
4. `Exception` → 500，并 `logger.exception`

更宽的 `Exception` 不会抢走更具体的处理器，因为查找走 MRO 上已注册的类型。

### OpenAPI

FastAPI 根据路由和 schema 生成 `/openapi.json`，Swagger UI 读它。生产关掉文档，减少攻击面和内部结构泄露。

## 最佳实践

- 路由保持薄：校验 + 调 service + `ok(...)`。
- 用 `APIRouter(prefix=..., tags=...)` 按资源拆文件，再 `include_router`。
- 路径版本写在前缀 `/api/v1`，不要每个函数手写。
- `HTTPBearer(auto_error=False)` 以便用自己的 `UnauthorizedError` 信封，而不是 FastAPI 默认的 403 详情格式。
- 工厂模式 `create_app()`，测试里只替换 `dependency_overrides`，不要另写一套装配。

## 本项目落地

- 工厂与处理器：`app/main.py`
- 路由汇总：`app/api/v1/router.py`
- 依赖：`app/api/deps.py`（`CurrentUser`、`SuperUser`、`AuthSvc`）
- 示例路由：`app/api/v1/endpoints/auth.py`、`users.py`、`health.py`

## 动手

1. 给 `GET /api/v1/health` 临时加一个 `Depends`，在依赖里打日志，确认每请求执行一次。
2. 读官方 [Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)。

## 下一章

[04 Pydantic](../04-pydantic/)
