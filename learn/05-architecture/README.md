# 05 · 分层架构

## 本章目标

能独立加一个资源（例如 articles），且不把 SQL 写进路由、不把 FastAPI 写进 service。

## 原理

分层是为了**依赖单向**和**可替换**：

- HTTP 会变（换 GraphQL、换 CLI），业务规则不该跟着变。
- 数据库会变（换查询、加缓存），HTTP 契约不该被 SQL 细节绑死。

本项目四层：

```text
endpoint  →  service  →  repository  →  model/session
                ↑
            schemas 只在边界转换
```

**Repository** 封装「怎么存」：get、list、create。可以换实现（内存、别的库）而不改 service 签名。  
**Service** 封装「准不准」：邮箱是否占用、密码对不对、发不发 token。抛 `AppError`，不返回随意 dict。  
**Endpoint** 封装「HTTP 是什么」：状态码 201、`response_model`、鉴权依赖。

`deps.py` 是组合根（composition root）的一部分：把 `AsyncSession` 收成 `UserService`，路由只声明 `svc: UserSvc`。

## 最佳实践

- 禁止 endpoint 里 `session.execute`；禁止 service 里 `Request`、`Query`。
- 一个聚合根（User、未来的 Order）配一套 model / schema / repo / service / endpoint。
- 事务边界在请求级 `get_db`，service 里 `flush` 即可；脚本（创建超管）自己 `commit`。
- 新增模块顺序固定：model → 迁移 → schema → repository → service → endpoint → 测试（见 `docs/project.md`）。

## 本项目落地

- `app/repositories/base.py`：通用 get/list/create/update/delete
- `app/repositories/user.py`：`get_by_email`、`list_ordered`
- `app/services/user.py`、`auth.py`
- `app/api/deps.py` 工厂函数
- 路由不出现密码哈希调用，哈希只在 service + `app.core.security`

## 动手

1. 按 `docs/project.md` 的「文章」清单在纸上列出要建的文件名（先不必真写完）。
2. 找一条「分层被打破」的坏味道：如果有人在 endpoint 里 `hash_password`，指出应下沉到哪一层。

## 下一章

[06 SQLAlchemy](../06-sqlalchemy/)
