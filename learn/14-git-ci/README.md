# 14 · Git-flow 与 GitHub Actions

## 本章目标

能独立开 `feature/*`、对 `develop` 提 PR，并看懂 CI 在何时跑。

## 原理

### git-flow

长期分支：`main`（已上线）、`develop`（下一版集成）。短分支：

- `feature/<任务>` 从 develop 来，合回 develop——**一个任务一条**，用来跟踪该任务所有提交
- `release/<版本>` 发版冻结（尚未天天用）
- `hotfix/<问题>` 从 main 来，合回 main 和 develop

合入 develop 不等于上线。上线走 release 进 main。这就是为什么 `adopt-git-flow` 合进 develop 之后不必再推一次已经推过的 develop，也**不会自动出现在 main**。

提交信息用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/v1.0.0/)：`feat:` / `fix:` / `docs:`，方便以后打 changelog。

### GitHub Actions

仓库里 `.github/workflows/*.yml` 在 GitHub 的 runner 上执行。本项目 `ci.yml`：

- `push` 到 `main` / `develop` 时跑
- 任意 `pull_request` 时跑（所以 feature → develop 的 PR 会跑）

步骤：checkout → Python 3.12 → `pip install -e ".[dev]"` → ruff → pytest。Runner 是干净 Ubuntu，用的是内存 SQLite 测试，不启 Docker 里的 Postgres。

PR 模板提醒 base 选 develop。

## 最佳实践

- 不要在 `main`/`develop` 上直接 commit。
- `make feature n=短名` 从最新 develop 拉分支。
- 不要 force push 长期分支。
- CI 失败不要合并。
- `.env` 永不入库。

## 本项目落地

- 约定：`docs/git.md`
- 命令：`make feature`、`make hotfix`
- 工作流：`.github/workflows/ci.yml`
- 模板：`.github/PULL_REQUEST_TEMPLATE.md`

## 动手

1. `git log develop --oneline --graph -10` 看 merge commit。
2. 打开仓库 Actions 页，对照 yaml 看一次绿色构建。

## 下一章

[15 配置与 Makefile](../15-config/)
