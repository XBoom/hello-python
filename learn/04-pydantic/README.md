# 04 · Pydantic v2 与配置

## 本章目标

分清「请求/响应 Schema」和「环境配置 Settings」，理解校验失败为什么是 422。

## 原理

Pydantic 用类型注解在运行时校验和转换数据。v2 核心是 Rust 写的 `pydantic-core`，模型默认不可变策略与 v1 不同，常用 `model_validate`、`model_dump`。

三类用法在本项目里同时出现：

| 用途 | 基类 | 例子 |
|------|------|------|
| 入参/出参 | `BaseModel` | `UserCreate`、`UserRead`、`Response[T]` |
| 配置 | `BaseSettings`（pydantic-settings） | `Settings`，从环境变量和 `.env` 读 |
| ORM 转出参 | `ConfigDict(from_attributes=True)` | `UserRead.model_validate(user)` |

`EmailStr` 需要额外包 `email-validator`。`Field(min_length=8)` 会进入 OpenAPI 和校验错误详情。

`pydantic-settings`：字段名对应环境变量（默认大小写不敏感）。列表类型（如 `CORS_ORIGINS`）在 `.env` 里用 JSON 数组。`extra="ignore"` 避免未知环境变量导致启动失败。

`model_validator(mode="after")` 在字段都解析完后做跨字段规则：生产禁止弱 `SECRET_KEY` 和 `DEBUG=true`。

## 最佳实践

- **ORM 模型不要当 API 模型用**。表上有 `hashed_password`，对外必须是 `UserRead`。
- 入参用 Create/Update，出参用 Read；Update 字段全 Optional，部分更新用 `exclude_unset`。
- 配置只从环境来，代码里不写主机密码。示例值放 `.env.example`。
- 校验错误返回统一信封，不要把原始 422 细节在生产当成功路径依赖；本项目 `data` 里带 `exc.errors()` 方便开发，生产也可改为不返回明细。
- 泛型信封 `Response[T]` 让 OpenAPI 能展开 `data` 的形状。

## 本项目落地

- 信封与分页：`app/schemas/common.py` 的 `ok()`、`Response`、`PageResult`
- 用户：`app/schemas/user.py`
- 配置：`app/core/config.py`，进程内单例 `settings = Settings()`
- `.env.example` 是字段清单

注意：`settings` 在 import 时就创建。测试若要换 `DATABASE_URL`，应在 import `app.main` **之前** 改环境，或像本项目一样用 `dependency_overrides` 换 Session，而不依赖改全局 Settings。

## 动手

1. 用错误邮箱调注册接口，看 422 的 `data` 结构。
2. 读 [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)。

## 下一章

[05 分层架构](../05-architecture/)
