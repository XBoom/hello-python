# 06 · SQLAlchemy 2.0 异步

## 本章目标

分清 Engine、Session、Connection；看懂 `Mapped[]` 模型和 `get_db` 的 commit/rollback。

## 原理

SQLAlchemy 2.0 推荐 **Declarative** + `Mapped` 注解风格，而不是 1.x 的 `Column` 堆在类体里。

核心对象：

| 对象 | 作用 |
|------|------|
| `Engine` | 连接池，进程级单例 |
| `Connection` | 池里借出的一条连接 |
| `Session` | 工作单元：跟踪对象改动，flush 发 SQL，commit 提交事务 |

异步栈：`create_async_engine` + `async_sessionmaker` + `AsyncSession`。驱动：Postgres 用 `postgresql+asyncpg://`，SQLite 用 `sqlite+aiosqlite://`。URL 里的 **+驱动** 决定 DBAPI。

`expire_on_commit=False`：commit 后不把对象属性过期，否则异步下再访问字段可能触发隐式 IO 甚至报错。

`autoflush=False`：查询前不自动 flush，行为更可预测；本项目在 repo 里显式 `flush`。

连接池：Postgres 设 `pool_pre_ping`（取连接先探测，避免被服务端踢掉的死连接）、`pool_size` / `max_overflow`。SQLite 文件库用 `check_same_thread=False` 以适配任意线程（ASGI 可能切线程）。

懒加载：在异步 Session 里访问未加载的 relationship 很容易翻车。列表接口应 `selectinload` / `joinedload`，或本项目这样先不建 relationship。

`MetaData(naming_convention=...)` 让主键/唯一/外键在 Alembic 里有稳定名字，换数据库时迁移脚本才可预期。见 [SQLAlchemy 约束命名](https://docs.sqlalchemy.org/en/20/core/constraints.html#constraint-naming-conventions)。

## 最佳实践

- 一个请求一个 Session，不要做成全局 Session。
- 成功路径 commit 放在依赖收尾，失败 rollback；不要在每个 service 方法里 commit（脚本除外）。
- 主键用 UUID 对外暴露，少用自增整数（可被遍历）。
- `DateTime(timezone=True)` + UTC。
- `unique=True` 已有唯一约束，不要再叠一个无意义的普通 `index=True`。
- 生产关掉 `echo`（本项目用 `DEBUG` 控制）。

## 本项目落地

- 引擎与 `get_db`：`app/db/session.py`
- 基类与 mixin：`app/models/base.py`
- 用户表：`app/models/user.py`
- 必须在 `app/models/__init__.py` 导出模型，Alembic 和测试 `create_all` 才能看到表

`get_db` 逻辑：yield 后若路由正常结束则 `commit`；若抛异常，生成器在 yield 处收到异常，走 `rollback` 再抛出。

## 动手

1. 读 `get_db`，用自己的话写「登录失败时会不会把半截 User 写进库」。
2. 浏览 [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)。

## 下一章

[07 Alembic](../07-alembic/)
