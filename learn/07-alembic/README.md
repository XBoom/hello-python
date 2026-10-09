# 07 · Alembic 数据库迁移

## 本章目标

能解释为什么改 model 之后还要生成 revision，以及 autogenerate 为什么必须人工检查。

## 原理

ORM 只描述「代码认为表长什么样」。数据库是另一份持久状态。两边靠 **迁移脚本** 对齐：每份脚本有 `revision` / `down_revision`，串成链表。表 `alembic_version` 记下当前节点。

`alembic upgrade head`：沿链表执行还没跑过的 `upgrade()`。`downgrade` 反向。

`alembic revision --autogenerate`：把 `Base.metadata` 和**当前连上的库**做 diff，生成 `op.create_table` 等。它看不见的东西包括：数据回填、部分索引、重命名 vs 删建、服务端默认值细节。所以 autogenerate 是草稿，不是法律。

异步工程里，Alembic 内部仍用同步 `Connection.run_sync` 跑迁移；`env.py` 用 `async_engine_from_config` + `asyncio.run` 包一层。URL 来自应用 `settings.DATABASE_URL`，密码里的 `%` 要写成 `%%`，因为 configparser 把 `%` 当插值。

`target_metadata = Base.metadata` 且必须 import 所有模型，否则 autogenerate 会以为表被删了。

`create_all` 只适合空库/测试：对已有表不会 ALTER。生产只用 Alembic。

## 最佳实践

- 一条 revision 只做一类事（加表、加列、回填数据尽量拆开）。
- 已合进 `develop`/`main` 的 revision 不要改文件内容，再出新 revision。
- 提交前看生成的 `upgrade`/`downgrade` 是否对称。
- Docker 启动先 `alembic upgrade head` 再起 Uvicorn，避免代码比表新。
- 本地 SQLite 与生产 Postgres 的 DDL 不完全一样；能共用的用通用类型（`Uuid`、`DateTime(timezone=True)`），Postgres 专用能力要有意识。

## 本项目落地

- 配置：`alembic.ini`（URL 实际被 `env.py` 覆盖）
- 环境：`alembic/env.py`
- 首迁：`alembic/versions/001_create_users.py`
- 命令：`make migrate`、`make migrate-new m="说明"`
- compose 里 API 的 command 先迁移后启动

## 动手

1. 打开 `001_create_users.py`，对照 `User` 模型每一列。
2. 故意改 `User` 加一个可空列，跑 `make migrate-new m="add user nickname"`，看生成脚本，然后用 `alembic downgrade -1` 练回滚（确认无重要数据再做）。

## 下一章

[08 鉴权与安全](../08-auth-security/)
