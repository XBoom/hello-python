# 00 · 项目全景

## 本章目标

能画出一次请求从端口 8000 到数据库再回到 JSON 的路径，并说清每个目录存在的理由。

## 原理

后端模板不是「一堆库堆在一起」，而是把**稳定的横切能力**（配置、鉴权、事务、日志、错误形态）先搭好，业务只往约定的层里填。

本仓库的运行时入口是 `uvicorn app.main:app`：

- `app` 是 Python 包。
- `app.main:app` 表示模块 `app.main` 里的变量 `app`，它是 `create_app()` 返回的 FastAPI 实例。
- FastAPI 建立在 Starlette 上；Uvicorn 按 [ASGI](https://asgi.readthedocs.io/) 协议调用它。

数据在进程内的分层：

```text
endpoints  只认 HTTP：路径、状态码、Pydantic 入参、调用 service
services   只认业务：规则、抛 AppError、不拼 SQL
repositories 只认表：CRUD、查询、分页
models     只认库表形状
schemas    只认对外 JSON 形状（与 models 分开，避免把 hashed_password 漏出去）
```

数据库结构不跟着 Python 进程「自动变」，而由 Alembic 脚本版本化。测试用内存 SQLite + `create_all`，生产用迁移，这是两条故意分开的路。

## 最佳实践

- **入口用工厂** `create_app()`，测试和未来多 worker 都能拿到同一套装配逻辑。
- **一个请求一个 Session**：`get_db` yield 会话，成功 commit、失败 rollback。
- **规范与教材分离**：`docs/` 约束日常提交；`learn/` 讲原理。不要把长教程写进 `docs/`。
- **本地降低摩擦、生产收紧**：默认 SQLite + DEBUG 开文档；`ENVIRONMENT=production` 禁止弱密钥和 DEBUG。

## 本项目落地

| 路径 | 角色 |
|------|------|
| `app/main.py` | 装配应用、中间件、异常处理 |
| `app/core/` | 配置、JWT、日志、错误码 |
| `app/api/v1/` | 版本化路由 |
| `app/services/`、`app/repositories/` | 业务与数据 |
| `alembic/` | 表结构历史 |
| `tests/` | 接口测试 |
| `docs/` | 团队规范 |
| `Dockerfile` + `docker-compose.yml` | 运行形态 |

对照一次登录：`POST /api/v1/auth/login` → `endpoints/auth.py` → `AuthService.login` → `UserRepository.get_by_email` → 校验 Argon2 → 签发 JWT → `ok(TokenPair)`。

## 动手

1. 画一张自己的请求路径图（纸或注释均可），标出 commit 发生在哪一层。
2. 读 `app/api/v1/router.py`，数一数现在挂了几个 router。

## 下一章

[01 Python](../01-python/)：异步和类型是后面所有章节的语言基础。
