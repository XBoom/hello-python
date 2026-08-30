# 日志规范

## 采用的外部规范

- [Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- [十二要素：日志](https://12factor.net/zh_cn/logs)：进程写 stdout，由采集器处理，不自己轮转文件

本仓库用标准库 `logging`，不引入第二套日志框架，除非全组统一换成结构化 JSON（如 structlog）并改本页。

## 获取 logger

每个模块：

```python
import logging

logger = logging.getLogger(__name__)
```

不要用 `print` 打运行时信息。不要 `logging.basicConfig` 散落在业务里；只在 `setup_logging()`（应用 `lifespan` 启动时）配置一次。

## 格式与请求 ID

当前格式：

```text
%(asctime)s | %(levelname)s | %(request_id)s | %(name)s | %(message)s
```

- `X-Request-ID`：请求可自带；否则服务端生成 UUID，并写回响应头。
- `request_id` 存在 `contextvars`（`app.core.context`），由 `RequestContextMiddleware` 注入，Filter 写进日志。
- 下游调用、异步任务若要贯通，继续传同一 ID，不要另起一套 trace 字段名（以后接 OpenTelemetry 时再用 `trace_id`）。

中间件已记录：`METHOD path -> status (耗时ms)`。路由里不要再打一条完全相同的 access log。

## 级别

| 级别 | 何时用 |
|------|--------|
| DEBUG | 仅本地排障，例如 SQL echo（由 `DEBUG` 控制 sqlalchemy 引擎日志） |
| INFO | 正常审计：启动、关键业务成功节点、请求结束 |
| WARNING | 可恢复异常：重试、降级、配置将废弃 |
| ERROR | 失败且需人看：外部依赖失败、业务无法完成 |
| EXCEPTION | 未捕获异常用 `logger.exception(...)`，自动带堆栈 |

生产默认 `LOG_LEVEL=INFO`。不要把 DEBUG 日志长期开在生产。

## 写什么、不写什么

要写：

- 关键 ID（用户 ID、资源 ID、request_id）
- 外部调用失败原因（状态码、超时）
- 未处理异常（全局 handler 已 `logger.exception`）

禁止写：

- 密码、`SECRET_KEY`、JWT 原文、Cookie
- 银行卡、身份证等敏感 PII
- 完整请求 body（容易含密码）；需要排障时只打字段名或脱敏后的摘要

消息用可 grep 的短句，变量用 `%s` 延迟格式化：

```python
logger.info("created user %s", user.id)
```

不要用 f-string 打日志（异常路径下拼字符串也有开销，且风格不统一）。

## 输出

- 只打 **stdout**（`StreamHandler(sys.stdout)`），Docker / K8s / systemd 负责收集。
- 不要在应用内写 `logs/app.log` 再自己 rotate。
- `uvicorn.access` 已关掉，避免和中间件 access 日志重复。

## SQL 日志

- `DEBUG=true` 时 SQLAlchemy engine 可为 INFO（echo）。
- 生产必须关闭 echo，避免日志爆炸和参数泄露。
