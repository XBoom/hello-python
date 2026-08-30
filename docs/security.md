# 安全规范

## 采用的外部规范

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- 密钥与配置：[十二要素：配置](https://12factor.net/zh_cn/config)

本页是本仓库必须落地的子集，不是 OWASP 全文替代。

## 密钥与环境

- `SECRET_KEY`、数据库密码、第三方 Token **只放环境变量**，`.env` 不入库。
- 提交 `.env.example`，用假值；生成密钥：

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

- `ENVIRONMENT=production` 时：禁止 `changeme` 开头的 `SECRET_KEY`，禁止 `DEBUG=true`（启动即失败）。
- 密钥泄露后轮换 JWT 密钥（用户需重新登录），并轮换数据库密码。

## 鉴权与令牌

- 密码哈希用 `pwdlib` 推荐算法（Argon2），不要 MD5/SHA1 存密码，不要可逆加密密码。
- Access token 短 TTL（默认 30 分钟），Refresh 更长（默认 7 天）。payload 含 `sub`、`type`、`exp`；`type` 必须校验，禁止 access 当 refresh 用。
- 令牌只放 `Authorization: Bearer`，不要放 URL query（会进代理日志）。
- 用户不存在或密码错误，对外同一句「邮箱或密码错误」，避免枚举账号（可在服务端打日志区分）。
- 禁用用户：`is_active=false` 后，access 与 refresh 均拒绝。

## 接口暴露

- 生产关闭 `/docs`、`/redoc`、`/openapi.json`。
- CORS：`CORS_ORIGINS` 写明确前端源，不要在带 Cookie / `allow_credentials=true` 时用 `*`。
- 注册接口上线前评估是否对公网开放；需要邀请制时关掉或加权限。
- 管理类接口必须 `SuperUser`，不能只靠「前端隐藏按钮」。

## 输入与数据

- 所有入参走 Pydantic，边界（长度、邮箱格式、分页上限）写在 schema 上。
- 更新当前用户时，忽略客户端传入的 `is_active` / `is_superuser` 等提权字段。
- SQL 只用 SQLAlchemy 参数化构造，禁止拼接用户字符串进 SQL。
- 响应不要返回 `hashed_password`；对外模型用 `UserRead` 这类 schema。

## 依赖与容器

- 定期看依赖 CVE，升级后跑测试。
- 镜像以非 root 跑为宜（后续加固 Dockerfile）；不要把 `.env` 打进镜像层（compose 用 `env_file` 注入）。

## 安全相关日志

失败登录可 INFO/WARNING，但不要记录密码。细则见 [日志规范](./logging.md)。
