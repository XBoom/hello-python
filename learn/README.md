# 学习计划

对照本仓库真实代码，按「**原理 → 最佳实践 → 本项目怎么落地**」学习全部技术栈。  
`docs/` 是团队规范（怎么做）；`learn/` 是学习材料（为什么、怎么用对）。

建议顺序就是目录编号。每章读完后，打开右侧「对照代码」把文件过一遍，再做「动手」。不必一次读完。

## 技术栈地图

一次 HTTP 请求在本项目中的路径：

```text
客户端
  → Uvicorn（ASGI 服务器）
    → Starlette 中间件（CORS、Request ID）
      → FastAPI 路由 + Pydantic 校验
        → Depends（DB Session、CurrentUser）
          → Service（业务）
            → Repository（SQLAlchemy AsyncSession）
              → PostgreSQL / SQLite
```

横切能力：JWT/Argon2 鉴权、统一错误码、logging、Alembic 迁表、pytest、Ruff、Docker、git-flow、CI。

## 章节

| 章 | 目录 | 覆盖技术 | 建议 |
|----|------|----------|------|
| 00 | [全景](./00-overview/) | 仓库结构、请求链路 | 先读，建立地图 |
| 01 | [Python](./01-python/) | 3.12、类型、async、venv/uv | 不熟异步必读 |
| 02 | [ASGI 与 Uvicorn](./02-asgi-uvicorn/) | ASGI、Starlette、Uvicorn | 理解「为什么不是 Flask 同步」 |
| 03 | [FastAPI](./03-fastapi/) | 路由、DI、lifespan、异常 | 核心框架 |
| 04 | [Pydantic](./04-pydantic/) | v2 模型、settings、校验 | Schema 与配置 |
| 05 | [分层架构](./05-architecture/) | endpoint/service/repository | 怎么加业务 |
| 06 | [SQLAlchemy](./06-sqlalchemy/) | 2.0 映射、异步引擎、Session | 数据访问 |
| 07 | [Alembic](./07-alembic/) | 迁移版本、autogenerate | 表结构演进 |
| 08 | [鉴权与安全](./08-auth-security/) | JWT、Argon2、CORS、OWASP | 登录链路 |
| 09 | [API 设计](./09-api-design/) | REST、信封、错误码、分页 | 接口契约 |
| 10 | [日志](./10-logging/) | logging、contextvars、stdout | 可观测 |
| 11 | [测试](./11-testing/) | pytest、httpx、依赖覆盖 | 如何锁行为 |
| 12 | [代码质量](./12-ruff/) | Ruff、pyproject | 风格自动化 |
| 13 | [Docker](./13-docker/) | 镜像分层、Compose、健康检查 | 部署形态 |
| 14 | [Git 与 CI](./14-git-ci/) | git-flow、Actions | 协作与流水线 |
| 15 | [配置与工具](./15-config/) | 十二要素、Makefile、hatchling | 环境与命令 |

## 怎么学

1. 先读该章「原理」，能用自己的话复述。
2. 对照「最佳实践」看本仓库有没有做到；冲突时以 `docs/` 为准。
3. 打开列出的源码文件，对着读。
4. 做「动手」：改一小处、跑 `make test` / `make lint`。

不要求背 API，要求能回答：这条请求进了哪一层、Session 何时 commit、令牌过期会返回哪个 code。
