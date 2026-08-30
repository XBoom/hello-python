# 08 · 鉴权与安全（JWT、Argon2、CORS）

## 本章目标

讲清 access/refresh 双令牌、密码哈希、以及 CORS 在浏览器里实际拦的是什么。

## 原理

### 密码

明文绝不能落库。哈希必须**慢且加盐**，抗彩虹表和暴力破解。本项目用 `pwdlib.PasswordHash.recommended()`，当前推荐 **Argon2**。校验用 `verify`，不要自己 `==` 哈希字符串时还绕过库的比较方式（库会处理算法前缀）。

### JWT

JWT 是三段 Base64：header.payload.signature。服务端用 `SECRET_KEY` 做 HMAC（本项目 HS256）。**任何人都能解码 payload**，只是不能伪造签名。所以 payload 里不要放密码、别放敏感 PII。

本项目 payload：`sub`（用户 UUID）、`type`（access|refresh）、`iat`、`exp`。解码时必须校验 `type`，否则 refresh 被当成 access 用。

Access 短 TTL（默认 30 分钟）降低失窃窗口；Refresh 较长（7 天）用来换新对。Refresh 仍是 JWT，**没有服务端黑名单**——这是权衡：实现简单，吊销只能等过期或改 `SECRET_KEY`（所有人下线）。生产若要「踢人」，需把 refresh 改成服务端存储或加 `jti` 黑名单。

### Bearer

`Authorization: Bearer <token>`。不要把 token 放 Query，代理和浏览器历史会留下。

错误处理：用户不存在和密码错误对外同一文案，防枚举；用户已删但 token 仍有效时当未认证，不要 404 泄露「这个 id 曾经存在」。

### CORS

浏览器跨域时：前端 `https://a.com` 调 `https://api.b.com`。CORS 是浏览器执行的策略，**Postman / 服务器之间调用不受 CORS 限制**。`allow_credentials=True` 时 `Allow-Origin` 不能是 `*`，必须写明源。

### 其它

生产关 `/docs`。`SECRET_KEY` 泄露等于谁都能签发令牌。参考 [OWASP API Security](https://owasp.org/www-project-api-security/)。

## 最佳实践

- 密码最小长度在 schema 上就限制。
- 用户自更新忽略 `is_superuser` / `is_active` 提权字段。
- 管理接口用 `SuperUser` 依赖，不要只靠前端藏按钮。
- 算法写死在配置里并在 `decode` 时传入 `algorithms=[...]`，禁止接受 header 里任意 alg（历史有 alg=none 攻击）。

## 本项目落地

- 哈希与 JWT：`app/core/security.py`
- 登录/刷新：`app/services/auth.py`
- 取当前用户：`app/api/deps.py`
- CORS：`app/main.py`
- 生产校验：`Settings.validate_production_safety`

## 动手

1. 登录后用 access 调 `/users/me`，再用 refresh 调 `/auth/refresh`。
2. 把 access 当 refresh 发给 `/auth/refresh`，确认 401 且 `TOKEN_INVALID`。

## 下一章

[09 API 设计](../09-api-design/)
