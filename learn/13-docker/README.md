# 13 · Docker 与 Compose

## 本章目标

能解释 Dockerfile 每一层为什么那样排，以及 Compose 里 API 为什么要等 Postgres healthy。

## 原理

镜像是只读层叠加。一条 `RUN`/`COPY` 一层。**越少变的越靠前**，才能命中缓存：先装依赖，再拷经常改的 `alembic/`。

`python:3.12-slim`：Debian 精简 + Python。`build-essential` 给需要编译的 C 扩展（如 Argon2 绑定）。装完删 apt 列表，必须和 `apt-get install` 同一 `RUN`，否则删列表减不掉上一层体积。

环境变量：`PYTHONUNBUFFERED=1` 让日志立刻到 `docker logs`；`PYTHONDONTWRITEBYTECODE=1` 不写 pyc。

`EXPOSE` 只是文档；真正映射看 `-p` 或 compose `ports`。

Compose 把 **API 容器 + Postgres 容器** 放同一网络。服务名 `postgres` 就是 DNS 主机名，所以 `DATABASE_URL` 里是 `@postgres:5432`。`depends_on` + `condition: service_healthy` 等 `pg_isready` 成功再启 API，避免迁移打到还在初始化的库。

数据放 named volume `postgres_data`，删容器不删数据；要空库就 `docker compose down -v`。

API 的 `command` 覆盖镜像 `CMD`：先 `alembic upgrade head` 再 uvicorn。镜像默认 CMD 不含迁移，方便单独跑；编排时补上。

## 最佳实践

- `.dockerignore` 排除 `.venv`、`.git`、测试、`.env`，减小上下文、避免把密钥打进构建上下文。
- 生产镜像不装 `.[dev]`。
- 密钥用 `env_file` 运行时注入，不要 `COPY .env`。
- 健康检查给依赖方用，不只是给人看。
- 以非 root 用户跑进程是后续加固（本模板尚未做，升级时补 `USER`）。

## 本项目落地

- `Dockerfile`、`.dockerignore`、`docker-compose.yml`
- 命令：`make docker-up` / `make docker-down`
- 逐行说明曾写在对话里，和 [02](../02-asgi-uvicorn/) 的 `0.0.0.0` 一起看

## 动手

1. 只改一个 Python 文件后 `docker compose build`，观察是否「Installing dependencies」整层重来（不该）。
2. 读 Docker 文档 [layer caching](https://docs.docker.com/build/cache/)。

## 下一章

[14 Git 与 CI](../14-git-ci/)
