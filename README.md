# FastAPI 后端服务框架模板

分层清晰、可直接二次开发的异步 FastAPI 脚手架。本地默认 SQLite，生产使用 PostgreSQL。

编码、API、数据库、日志等约定见 [docs/](./docs/README.md)。技术原理与最佳实践见 [learn/](./learn/README.md)（按章节学本仓库用到的栈）。

日常开发采用 [git-flow](./docs/git.md)：长期分支为 `main`（生产）与 `develop`（集成）。**每个任务从 `develop` 新开 `feature/<任务名>`**，合入 `develop`，不要直接在 `main` / `develop` 上提交。

```bash
make feature n=<任务短名>
```

## 能力

- FastAPI 应用工厂 + 生命周期管理
- `pydantic-settings` 环境配置，生产环境安全校验
- 统一响应 `{code, message, data}` 与业务异常
- 请求 ID 贯穿日志与响应头
- JWT 登录 / 刷新，Argon2 密码哈希
- SQLAlchemy 2.0 异步 + Repository / Service 分层
- Alembic 迁移
- pytest 接口测试
- Docker Compose（API + PostgreSQL）

## 目录

```text
app/
  main.py                 # 应用入口（工厂、中间件、异常处理）
  core/                   # 配置、安全、日志、异常、常量
  api/v1/endpoints/       # 路由，只做参数校验与调用 service
  services/               # 业务逻辑
  repositories/           # 数据访问
  models/                 # SQLAlchemy 模型
  schemas/                # Pydantic 入参 / 出参
  db/                     # 引擎与 Session
alembic/                  # 数据库迁移
tests/                    # 接口测试
scripts/                  # 运维脚本（创建超管等）
```

新增业务模块时按这个顺序加文件，然后把 router 挂到 `app/api/v1/router.py`：

`model → schema → repository → service → endpoint`

## 快速开始

需要 Python 3.12+（建议 3.12，不要用系统自带的 3.14 直接 `pip install`）。

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
make dev
```

若已安装 [uv](https://docs.astral.sh/uv/)：

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
make dev
```

- 文档：http://localhost:8000/docs（仅 `DEBUG=true` 时开启）
- 健康检查：`GET /api/v1/health`
- 就绪检查：`GET /api/v1/ready`

创建超级管理员：

```bash
python -m scripts.create_superuser --email admin@example.com --password password123
```

## 主要接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 注册 |
| POST | `/api/v1/auth/login` | 登录，返回 access / refresh |
| POST | `/api/v1/auth/refresh` | 刷新令牌 |
| GET  | `/api/v1/users/me` | 当前用户 |
| PATCH| `/api/v1/users/me` | 更新当前用户 |
| GET  | `/api/v1/users` | 用户分页（超管） |

请求头：`Authorization: Bearer <access_token>`。

## 常用命令

```bash
make dev            # 启动开发服务
make test           # 跑测试
make lint           # ruff 检查
make format         # ruff 格式化
make migrate        # alembic upgrade head
make migrate-new m="add xxx table"
make docker-up      # PostgreSQL + API
make feature n=xxx  # 从 develop 新开 feature/xxx
make hotfix n=xxx   # 从 main 新开 hotfix/xxx
```

生成新迁移前确保模型已改好，再执行 `make migrate-new m="说明"`。

## 配置

复制 `.env.example` 为 `.env`。生产必须：

- `ENVIRONMENT=production`
- `DEBUG=false`
- 使用随机 `SECRET_KEY`（可用 `python -c "import secrets; print(secrets.token_urlsafe(64))"`）
- `DATABASE_URL` 指向 PostgreSQL，例如  
  `postgresql+asyncpg://user:pass@host:5432/dbname`

## Docker

```bash
cp .env.example .env
# 修改 SECRET_KEY 与 ENVIRONMENT
make docker-up
```

Compose 会覆盖 `DATABASE_URL` 为容器内 PostgreSQL，并在启动时执行迁移。
