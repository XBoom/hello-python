# API 设计规范

## 采用的外部规范

资源风格与 HTTP 语义参考：

- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines/blob/vNext/azure/Guidelines.md)（资源、动词、分页、版本）
- [RFC 9110 – HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)（状态码含义）

本项目**不采用** [RFC 7807 Problem Details](https://www.rfc-editor.org/rfc/rfc7807) 作为响应体。统一信封见下文，便于前端用 `code` 做分支。

## 版本与路径

- 前缀：`/api/v1`，由 `API_V1_PREFIX` 配置。
- 破坏性变更（删字段、改含义、改鉴权）才升 `v2`，并保留旧路由一段时间。
- 路径用**复数名词**，不用动词：

| 推荐 | 不推荐 |
|------|--------|
| `GET /api/v1/users` | `GET /api/v1/getUsers` |
| `POST /api/v1/auth/login` | `POST /api/v1/doLogin` |
| `GET /api/v1/users/{user_id}` | `GET /api/v1/user` |

嵌套不超过一层：`/articles/{id}/comments` 可以；`/users/{id}/articles/{id}/comments/{id}` 避免。

鉴权类动作用子资源：`/auth/login`、`/auth/refresh`，而不是 `POST /users` 兼登录。

## HTTP 方法

| 方法 | 用途 | 成功状态码 |
|------|------|------------|
| GET | 读，无副作用 | 200 |
| POST | 创建，或登录等非幂等操作 | 创建 201，其余 200 |
| PATCH | 部分更新 | 200 |
| PUT | 本项目默认不用整表替换 | — |
| DELETE | 删除 | 204 或 200 + 信封，新接口优先 200 + `{code,message,data:null}` |

列表过滤用 query，不要用 `POST /users/search`，除非查询体非常复杂。

## 统一响应

成功与失败都是：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- 成功：`code = 0`，用 `ok(...)` 返回。
- 失败：`data` 一般为 `null`；校验失败时 `data` 可以是 Pydantic 的 `errors()` 列表。
- 路由声明 `response_model=Response[T]` 或 `Response[PageResult[T]]`。

时间字段用带时区的 ISO 8601（Pydantic / SQLAlchemy `DateTime(timezone=True)`），不要返回天真本地时间。

## 错误码

HTTP 状态码表示类别；`code` 表示业务细分。格式：`{HTTP状态}{两位序号}`，例如 40101。

定义写在 `app/core/constants.py` 的 `ErrorCode`，**不要在路由里写魔法数字**。

| HTTP | code 段 | 含义 |
|------|---------|------|
| 200 | 0 | 成功 |
| 400 | 400xx | 通用客户端错误（凭证错、账号禁用等） |
| 401 | 401xx | 未认证、令牌过期/无效 |
| 403 | 403xx | 已认证但无权限 |
| 404 | 404xx | 资源不存在 |
| 409 | 409xx | 冲突（邮箱占用等） |
| 422 | 422xx | 参数校验 |
| 500 | 500xx | 未处理异常 |

新增错误：先加常量，再在 service 里 `raise NotFoundError(ErrorCode.XXX, "中文说明")`。同类资源用相邻序号（`USER_NOT_FOUND = 40402`）。

消息给调用方看，用中文短句，不要堆栈。

## 分页

- Query：`page`（从 1 起）、`page_size`（默认 20，最大 100）。
- `data` 为：

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

不要用一页打满全表。超大列表后续可加 cursor，但现有接口保持 offset 分页。

## 鉴权

- 访问令牌：`Authorization: Bearer <access_token>`。
- 刷新：`POST /api/v1/auth/refresh`，JSON body `{ "refresh_token": "..." }`，不要把 refresh 放进 query。
- 需要登录：依赖 `CurrentUser`；需要超管：`SuperUser`。
- 匿名接口不要误加 Bearer 依赖。

## OpenAPI

- 每个路由设 `tags`，与资源名一致（`auth`、`users`、`health`）。
- 入参用 Pydantic schema，字段加 `Field(min_length=...)` 等约束，让文档和校验一致。
- 生产关闭 `/docs`，见 [项目规范](./project.md)。
