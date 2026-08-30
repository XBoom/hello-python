## 说明

本仓库使用 git-flow。功能与日常任务请将 base 设为 **`develop`**。

生产热修请将 base 设为 **`main`**，合并后再同步进 `develop`。

## 检查

- [ ] `make lint`
- [ ] `make test`
- [ ] 有表结构变更时已包含 Alembic revision
- [ ] 一个 PR 只对应一个任务 / 一条 `feature/*` 或 `hotfix/*`
