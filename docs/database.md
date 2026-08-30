# 数据库规范

## 采用的外部规范

- [SQLAlchemy 2.0 映射风格](https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html)（`Mapped[]` + `mapped_column`）
- [Constraint Naming Conventions](https://docs.sqlalchemy.org/en/20/core/constraints.html#constraint-naming-conventions)
- [Alembic 教程](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

生产库是 **PostgreSQL**；本地和测试可用 SQLite，但不要在 SQLite 上依赖 Postgres 独有类型/函数（如 `JSONB`、部分索引表达式）而不做分支。

## 命名

| 对象 | 规则 | 示例 |
|------|------|------|
| 表 | 复数，snake_case | `users`、`order_items` |
| 列 | snake_case | `full_name`、`created_at` |
| 模型类 | 单数 PascalCase | `User` |
| 主键 | `id`，UUID | `UUIDPrimaryKeyMixin` |
| 外键列 | `{单数表名}_id` | `user_id` |
| 布尔 | `is_` / `has_` 前缀 | `is_active` |

不要用复数当类名（`Users`），不要用驼峰当列名（`fullName`）。

## 主键、时间、软删除

- 主键用 UUID，不要自增整数对外暴露（避免枚举、合并表冲突）。
- 每张业务表带 `created_at`、`updated_at`，`DateTime(timezone=True)`，沿用 `TimestampMixin`。
- 时间存 UTC。应用层用 `datetime.now(UTC)`，不要 `datetime.now()`。
- 需要「删除仍可查」时用 `deleted_at` 软删，查询默认过滤未删除行；不要物理删审计相关数据。

## 约束命名

`Base.metadata` 已配置命名约定，Alembic 自动生成的约束名必须稳定、跨库一致：

| 类型 | 格式 |
|------|------|
| 主键 | `pk_<table>` |
| 唯一 | `uq_<table>_<column>` |
| 索引 | `ix_<column_label>` |
| 外键 | `fk_<table>_<column>_<referred_table>` |
| Check | `ck_<table>_<name>` |

`unique=True` 已包含唯一约束/索引，**不要再同时写 `index=True`**（历史表 `users.email` 的迁移名是 `ix_users_email`，新表不要照抄这个重复写法）。

## 类型与完整性

- 字符串必须带长度：`String(255)`，不要无界 `Text` 当普通字段（正文、日志另说）。
- 邮箱、状态等有限值在库层也要有约束（`unique`、`nullable`、必要时 Check）。
- 外键要建 FK，删除策略显式写清：`ondelete="CASCADE"` 或 `RESTRICT`，不要依赖默默失败。
- 密码只存哈希列（`hashed_password`），见 [安全规范](./security.md)。
- 金额用整数分或 `Numeric`，不要 `float`。

## 查询

- 列表必须分页，见 [API 规范](./api.md)。
- 按什么过滤/排序就建什么索引；不要无差别给所有列加索引。
- 异步会话里避免触发隐式 IO 的懒加载：关系查询用 `selectinload` / `joinedload`，或禁止在 schema 里顺手访问未加载关系。
- 写操作在 Repository `flush`；请求成功由 `get_db` 统一 `commit`，失败 `rollback`。Service 不要自行 `commit`（脚本除外，如 `scripts/create_superuser.py`）。

## 迁移

- **表结构变更必须走 Alembic**，生产禁止 `Base.metadata.create_all`。
- 改模型后：

```bash
make migrate-new m="add articles table"
# 人工检查 alembic/versions/ 下脚本
make migrate
```

- 检查清单：升级/降级是否对称；有无误删列；Postgres 与 SQLite 是否都能执行（若 CI 只用 SQLite，避免 Postgres 专用 DDL，或拆环境）。
- 数据迁移（回填、改值）与结构迁移分开，脚本要可重入。
- 不要手改已合并到主分支的旧 revision；再出新 revision。

## 连接串

- 异步驱动：Postgres 用 `postgresql+asyncpg://...`，SQLite 用 `sqlite+aiosqlite://...`。
- 凭证只放环境变量，见 [项目规范](./project.md)。
