# 10 · 日志与请求 ID

## 本章目标

理解为什么日志打 stdout、为什么用 `getLogger(__name__)`、request_id 如何穿过一次请求。

## 原理

[十二要素：日志](https://12factor.net/zh_cn/logs) 把日志当事件流：进程只写 stdout/stderr，由 Docker/K8s/采集器去切分、索引。应用内自己写文件+轮转，在容器里又痛又难统一格式。

标准库 `logging` 是树：子 logger 把记录传给父，最后到 root。`logging.getLogger(__name__)` 用模块路径当名字，便于按包调级别。

`contextvars` 提供**任务/请求内**的隐式上下文，比线程局部更适合 asyncio（协程会在线程间切换）。本项目 `request_id_ctx` 存当前请求 ID；Filter 在每条 LogRecord 上写入 `request_id`。中间件从 `X-Request-ID` 读取或生成 UUID，响应原样带回，方便前端/网关串联。

级别：DEBUG 排障、INFO 正常审计、WARNING 可恢复、ERROR 失败、`logger.exception` 带堆栈。生产默认 INFO。SQL echo 只在 DEBUG。

敏感数据（密码、JWT 原文、密钥）不能进日志。用 `%s` 延迟格式化：`logger.info("created user %s", user.id)`。

## 最佳实践

- 只在启动时 `setup_logging()` 一次，业务里不要 `basicConfig`。
- 关掉与中间件重复的 uvicorn access log。
- 未处理异常在全局 handler 里 `logger.exception`，响应体生产不带堆栈。
- 以后接 OpenTelemetry 时，可把 request_id 与 trace_id 对齐，先不要两套字段名。

## 本项目落地

- 配置：`app/core/logging.py`
- 上下文：`app/core/context.py`
- 中间件：`app/core/middleware.py`
- 500：`app/main.py` 的 `unhandled_error_handler`
- 规范：`docs/logging.md`

## 动手

1. 调 `/api/v1/health`，看响应头 `X-Request-ID` 与控制台同一列是否一致。
2. 自己带 `X-Request-ID: test-123` 再调一次，确认被回显。

## 下一章

[11 测试](../11-testing/)
