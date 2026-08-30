# 12 · Ruff 与工程配置（pyproject）

## 本章目标

知道 Ruff 替代了 flake8+isort+黑的哪一部分，以及规则写在哪里。

## 原理

Python 项目的单一事实来源越来越是 **`pyproject.toml`**（PEP 518/621）：依赖、构建后端、工具配置都在一个文件。

本项目构建后端是 **hatchling**，`packages = ["app"]`，所以 `pip install .` 会把 `app` 装进 site-packages。`pip install -e .` 可编辑模式，源码仍是仓库里的 `app/`。

**Ruff** 用 Rust 写，把 linter + formatter 合成一个命令，速度远快于 pylint 全家桶。本仓库：

- formatter：行宽 88、双引号（对齐 Black）
- lint：`E` pycodestyle、`F` pyflakes、`I` isort、`UP` pyupgrade、`B` bugbear、`SIM` simplify
- `known-first-party = ["app"]` 保证 `from app...` 分在第一方组

PEP 8 默认行宽 79；本项目有意用 88，差异写在 `docs/python.md`。以 Ruff 输出为准，不要用编辑器各套规则打架。

## 最佳实践

- CI 跑 `ruff check`，不要只在本地格式化。
- 提交前 `make format`，避免「纯空格 diff」。
- 少关规则；要关就写明文件级 `# noqa` 并注释原因。
- 依赖版本用 `>=` 下限即可，锁文件（uv.lock）可按团队以后再加。

## 本项目落地

- 全部工具配置：`pyproject.toml`
- 命令：`make lint`、`make format`
- CI：`.github/workflows/ci.yml` 里先 lint 再 pytest

## 动手

1. 故意写一行超过 88 字符，跑 `make lint` 看报错。
2. 打开 [Ruff 规则目录](https://docs.astral.sh/ruff/rules/) 查 `UP046` 为什么要求 PEP 695 泛型写法。

## 下一章

[13 Docker](../13-docker/)
