# Python 编码规范

## 采用的外部规范

以这些文档为默认约定，本页只写本仓库的差异和强制项：

- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)
- [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
- [PEP 8 中文整理（PEP 8 官方为准）](https://peps.python.org/pep-0008/)
- 格式化以 [Ruff Formatter](https://docs.astral.sh/ruff/formatter/) 为准（兼容 Black）

不单独再维护一份「Google Python Style」全文。若 PEP 8 未覆盖，可参考 [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)，但与 Ruff / 本页冲突时以本页为准。

## 本仓库与 PEP 8 的差异

| 项 | PEP 8 | 本项目 |
|----|-------|--------|
| 行宽 | 79 | **88**（Ruff / Black 默认） |
| 引号 | 无强制 | **双引号**（`ruff format`） |
| 类型注解 | 建议 | **公共函数必须有** |
| 风格检查 | 人工 / flake8 | **Ruff**，见 `pyproject.toml` |

运行：

```bash
make format    # 自动修
make lint      # 只检查
```

当前 Ruff 规则集：`E`（pycodestyle）、`F`（pyflakes）、`I`（isort）、`UP`（pyupgrade）、`B`（bugbear）、`SIM`（simplify）。目标版本 `py312`。

## 命名

| 对象 | 风格 | 示例 |
|------|------|------|
| 模块、包 | snake_case，短名 | `user.py`、`repositories` |
| 类 | PascalCase | `UserService`、`AppError` |
| 函数、变量、方法 | snake_case | `get_current_user` |
| 常量 | UPPER_SNAKE | `REQUEST_ID_HEADER` |
| 环境变量 / Settings 字段 | UPPER_SNAKE | `DATABASE_URL` |
| 类型参数 | 简短 PascalCase | `Response[T]`、`ModelT` |
| 私有实现 | 单前导下划线 | `_hasher`、`_issue_tokens` |

避免用 `l`、`O`、`I` 单字母；不要用 Python 关键字做名字。

## 类型与现代语法

- 运行时 Python **3.12+**。
- 用内置泛型：`list[str]`、`dict[str, Any]`，不要 `List` / `Dict`。
- 联合类型用 `X | None`，不要 `Optional[X]`。
- 泛型类用 PEP 695：`class Response[T](BaseModel)`、`class BaseRepository[ModelT: Base]`。
- FastAPI 依赖用 `Annotated`：`CurrentUser = Annotated[User, Depends(get_current_user)]`。

## 异步

- I/O（数据库、HTTP）一律 `async` / `await`。
- 不要在协程里调用阻塞函数（同步文件大读写、`time.sleep`、同步 HTTP 库）。CPU 密集或阻塞调用放到线程池，或换异步实现。
- SQLAlchemy 使用 `AsyncSession`，禁止在请求路径里用同步 `Session`。

## 导入

- 标准库 → 第三方 → 本项目（`app`），组之间空一行。由 Ruff `I` 保证。
- 本项目包名是 `app`，不要用相对导入跨层（`from ..models` 可以，但优先绝对：`from app.models.user import User`）。

## 注释与 docstring

- 代码本身能说清的，不写注释。
- 注释写「为什么」，不写「做了什么」。
- 模块/公开异常/非显而易见的公共函数可写一句话 docstring，中英文均可，本仓库默认中文。
- 不要为每个 getter 写 docstring。

## 错误处理

- 业务失败抛 `AppError` 子类（`NotFoundError` 等），不要在路由里手写 `JSONResponse`。
- 不要裸 `except:`。捕获时尽量收窄类型，需要记录时用 `logger.exception`。
- 不要吞掉异常后返回成功。
