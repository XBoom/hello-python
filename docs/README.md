# 项目规范

本目录是本仓库的**约定文档**，开发时以这里为准。

写法：

- **外部成熟规范只引用，不整篇抄录。** 例如 PEP 8、Conventional Commits、十二要素。
- **本仓库落地规则写清楚。** 包括与上游规范的差异、目录约定、错误码、迁移流程等。
- 代码与文档冲突时，先改到一致，再合并。

## 文档索引

| 文档 | 覆盖范围 |
|------|----------|
| [Python 编码](./python.md) | 风格、命名、类型、异步、Ruff |
| [项目与工程](./project.md) | 分层、目录、新增模块、配置 |
| [API 设计](./api.md) | REST、版本、响应体、错误码、分页 |
| [数据库](./database.md) | 命名、主键、迁移、索引 |
| [日志](./logging.md) | 级别、请求 ID、敏感信息 |
| [安全](./security.md) | 密钥、鉴权、密码、CORS |
| [Git 与协作](./git.md) | git-flow、feature 任务分支、提交信息 |
| [测试](./testing.md) | pytest、夹具、覆盖范围 |

## 工具如何卡住规范

| 约定 | 执行方式 |
|------|----------|
| Python 风格 | `make lint` / `make format`（Ruff） |
| 接口行为 | `make test` |
| 表结构变更 | Alembic，禁止在生产用 `create_all` |
| 密钥与调试 | `ENVIRONMENT=production` 时启动校验 |

新增规范时：补对应 markdown，并在本页表格加一行。
