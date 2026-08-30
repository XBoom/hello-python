# 09 · API 设计（REST、信封、错误码、分页）

## 本章目标

能按本仓库约定设计一个新资源的 URL、状态码和 `code`，而不是随手 `POST /getXxx`。

## 原理

REST 把**资源**当名词、用 HTTP 方法表达动作。版本放在前缀 `/api/v1`，破坏性变更才升 v2。参考 [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)。

本项目额外选了**统一信封**，而不是 RFC 7807 Problem Details：

```json
{ "code": 0, "message": "success", "data": {} }
```

前端用 `code === 0` 判断业务成功；HTTP 状态仍表示类别（401 未登录、409 冲突），便于网关和缓存。`code` 细分为 `40101`、`40402` 这种 `{HTTP}{两位序号}`。

分页用 `page` + `page_size`（offset 模式），`data` 里带 `items/total/page/page_size`。实现简单，深翻页会变慢；超大表以后可改 cursor，现有接口保持稳定。

时间对外 ISO 8601 带时区，来自 `DateTime(timezone=True)`。

## 最佳实践

- URL 复数名词：`/users`、`/users/{id}`；动作放在 `/auth/login` 这类子资源，而不是 `doLogin`。
- 创建 201，校验失败 422，冲突 409。
- 错误码写在 `ErrorCode` 常量，禁止路由里魔法数字。
- `page_size` 必须有上限（本项目 100），防止一次拉全表。
- OpenAPI `tags` 与资源名一致。

## 本项目落地

- 约定全文：`docs/api.md`
- 常量：`app/core/constants.py`
- 异常类：`app/core/exceptions.py`
- `ok()`：`app/schemas/common.py`
- 用户列表分页：`app/api/v1/endpoints/users.py`

## 动手

1. 对照 `ErrorCode` 与 `exceptions.py`，画「HTTP 状态 ↔ 异常类 ↔ code」表。
2. 设计 `GET /api/v1/articles` 的信封（只写 JSON 示例，先不写代码）。

## 下一章

[10 日志](../10-logging/)
