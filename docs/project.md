# 项目与工程规范

## 分层

请求只允许按这个方向依赖，禁止反向或跨层乱调：

```text
endpoint（路由）
    → service（业务）
        → repository（数据访问）
            → model / session
```

| 层 | 目录 | 允许做 | 禁止做 |
|----|------|--------|--------|
| 路由 | `app/api/v1/endpoints/` | 校验入参、取依赖、调 service、组装响应 | 写 SQL、拼密码哈希、直接 `session.execute` |
| 业务 | `app/services/` | 规则、鉴权后的领域操作、抛 `AppError` | 依赖 FastAPI 的 `Request` / `Query` |
| 仓储 | `app/repositories/` | CRUD、查询、分页 | 业务规则（例如「邮箱已注册」文案） |
| 模型 | `app/models/` | 表结构映射 | Pydantic 校验、HTTP 细节 |
| Schema | `app/schemas/` | 入参 / 出参 / 统一信封 | SQLAlchemy 对象当响应模型直接返回（需 `UserRead.model_validate`） |

`app/core/` 放配置、安全、异常、日志、常量，不放具体业务。

`app/api/deps.py` 只放可复用依赖（`get_db`、`CurrentUser`、各 service 工厂）。

## 目录约定

```text
app/                  运行时代码
alembic/              迁移脚本
tests/                测试，目录与行为对齐即可
scripts/              一次性/运维脚本，不进请求路径
docs/                 本规范
.env.example          环境变量清单（可提交）
.env                  本地密钥（禁止提交）
```

模块文件用**单数领域名**：`user.py`、`auth.py`。表名用复数，见 [数据库规范](./database.md)。

## 新增一个业务模块

以「文章 articles」为例，按顺序做，不要跳层先写路由：

1. `app/models/article.py`：模型，并在 `app/models/__init__.py` 导出（Alembic 才能发现）。
2. `make migrate-new m="create articles table"`，检查生成脚本后 `make migrate`。
3. `app/schemas/article.py`：`ArticleCreate` / `ArticleUpdate` / `ArticleRead`。
4. `app/repositories/article.py`：继承 `BaseRepository[Article]`。
5. `app/services/article.py`：业务规则。
6. `app/api/v1/endpoints/articles.py`：路由。
7. 在 `app/api/v1/router.py` 的 `include_router`。
8. `tests/test_articles.py`。

## 配置（十二要素）

配置规范采用 [The Twelve-Factor App：配置](https://12factor.net/zh_cn/config)：

- **只通过环境变量注入**，由 `pydantic-settings` 读取，可选 `.env` 仅限本地。
- 新配置：先加 `app/core/config.py` 字段，再补 `.env.example`，不要在代码里写死主机、密码。
- 生产：`ENVIRONMENT=production` 时禁止默认 `SECRET_KEY`，禁止 `DEBUG=true`。
- 本地默认可 SQLite；生产必须 PostgreSQL，见 [数据库规范](./database.md)。

布尔、列表等复杂类型以 `.env.example` 的写法为准（CORS 用 JSON 数组）。

## 依赖

- 运行时依赖写在 `pyproject.toml` 的 `dependencies`。
- 测试 / Ruff 写在 `optional-dependencies.dev`。
- 不要另维护一份会过期的 `requirements.txt`，除非部署系统强制要求。
- 升级大版本前先跑 `make test` 与 `make lint`。

## 应用入口

- 工厂函数 `create_app()`，全局实例 `app = create_app()` 给 Uvicorn。
- 启动/关闭逻辑只放 `lifespan`，不要用已弃用的 `on_event`。
- 生产关闭 OpenAPI：`DEBUG=false` 时 `docs` / `redoc` / `openapi.json` 为 `None`。
