# 15 · 配置、十二要素与 Makefile

## 本章目标

能新增一个环境变量（配置类 + `.env.example`），并用 Makefile 找到对应命令，而不是背一长串 CLI。

## 原理

[十二要素：配置](https://12factor.net/zh_cn/config) 要求配置与代码分离，用环境变量注入。同一份镜像在 staging/production 只换环境，不换构建。

本项目 `Settings` 在启动时读取环境 / `.env`。生产校验失败则进程起不来——宁可启动挂，不要拖着弱密钥跑。

`DATABASE_URL` 同时编码了：协议、驱动、账号、主机、库名。Compose 用环境覆盖为容器内 Postgres；本地默认 SQLite 降低上手成本。

**Makefile** 把「人要做什么」收成短目标：`make test` 不关心 pytest 参数细节。`make feature n=...` 把 git-flow 第一步固化，减少漏 `pull`。

`python-multipart` 给将来表单/文件上传预留；当前 JSON API 也会被部分依赖带到。`email-validator` 支撑 `EmailStr`。

## 最佳实践

- 新配置三处一起改：`config.py`、`.env.example`、必要时 docker-compose `environment`。
- 布尔在容器环境里是字符串 `"false"`，pydantic-settings 能解析；不要写成 Python `False` 当环境值。
- 密钥用 `secrets.token_urlsafe(64)` 生成。
- Makefile 目标应幂等、可文档化；复杂逻辑再放到 `scripts/`。
- `scripts/create_superuser.py` 自己 commit，因为它不走 HTTP、没有 `get_db`。

## 本项目落地

- `app/core/config.py`
- `.env.example`
- `Makefile`
- `scripts/create_superuser.py`
- 规范：`docs/project.md` 的配置一节、`docs/security.md`

## 动手

1. 增加一个假想配置 `APP_TIMEZONE`（只改 config 和 example，不必全用上），走一遍「三处同步」。
2. 对照 `make help`——若没有 help，读 Makefile 注释，考虑以后加 `.PHONY` + 自描述。

## 学完之后

回到 [学习计划](../README.md)，用「一次登录请求」把 00–15 串起来讲给自己听。讲不顺的章再读一遍对照代码。
