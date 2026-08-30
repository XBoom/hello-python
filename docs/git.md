# Git 与协作规范

## 采用的外部规范

- 分支模型：[A successful Git branching model](https://nvie.com/posts/a-successful-git-branching-model/)（git-flow）
- 提交说明：[Conventional Commits](https://www.conventionalcommits.org/zh-hans/v1.0.0/)

日常开发以本页为准：长期分支只有 `main` 和 `develop`；**每个任务必须从 `develop` 拉一条 `feature/*` 分支**，不要在 `develop` / `main` 上直接改。

## 分支模型

```text
main        生产，只接受 release / hotfix
  ↑
release/*   发版准备（可选）
  ↑
develop     集成分支，功能合入点
  ↑
feature/*   一个任务一条，从 develop 拉出，合回 develop
hotfix/*    生产紧急修复，从 main 拉出，合回 main 和 develop
```

| 分支 | 从哪拉 | 合回哪里 | 用途 |
|------|--------|----------|------|
| `main` | — | — | 已发布、可上线 |
| `develop` | `main`（仓库初始化时） | 经 release 进 `main` | 下一步要发的集成代码 |
| `feature/<任务名>` | `develop` | `develop`（PR） | **一个任务一条**，跟踪该任务全部提交 |
| `release/<版本>` | `develop` | `main` + `develop` | 锁版本、改 changelog、修发版 bug |
| `hotfix/<问题>` | `main` | `main` + `develop` | 生产紧急修复 |

`main` 与 `develop` 禁止 force push。不要把 feature 直接合进 `main`。

## 新开任务（feature）

每接到一个独立任务（需求、重构、文档、技术债），都新开一条 feature，用分支名跟踪任务，不要把无关改动塞进同一条分支。

```bash
git fetch origin
git checkout develop
git pull --ff-only origin develop
git checkout -b feature/<任务短名>
```

或：

```bash
make feature n=<任务短名>
```

命名：`feature/` + 小写短横线，能看出任务即可。

```text
feature/user-profile
feature/jwt-refresh-rotate
feature/adopt-git-flow
```

不要：`feature/new`、`feature/fix`、在 `feature/user-profile` 上继续做下一个需求。

任务做完：

1. `make lint` 与 `make test`
2. `git push -u origin HEAD`
3. 向 **`develop`** 开 Pull Request（不要选 `main`）
4. 合并后删除远程 feature 分支

本地可用 `--no-ff` 合并以保留「这一任务」的汇合点（git-flow 传统做法）；GitHub 用 squash 也可以，但一个 PR 只对应一个任务。

## 发版与热修

发版（有需要时）：

```bash
git checkout develop
git pull --ff-only origin develop
git checkout -b release/0.2.0
# 只改版本号、changelog、发版修复
# PR 合入 main，打 tag，再把 main 合回 develop
```

生产热修：

```bash
make hotfix n=<问题短名>
# 从 main 拉出 hotfix/*，修完合入 main 与 develop
```

## 提交信息

格式：

```text
<type>(<scope>): <description>
```

`type` 常用：

| type | 用途 |
|------|------|
| feat | 新功能 |
| fix | 修 bug |
| docs | 只改文档 |
| refactor | 重构（不改行为） |
| test | 加或改测试 |
| chore | 构建、依赖、杂项 |
| perf | 性能 |

`scope` 可选，用模块名：`auth`、`users`、`db`。

描述用中文或英文均可，**说原因或结果**，不要只列文件名。

```text
feat(auth): 登录失败时统一错误文案，避免枚举邮箱
fix(users): 禁止通过 /users/me 修改 is_active
docs: 补充数据库约束命名约定
```

一条提交只做一件事。不要把格式化全仓库和业务改动混在一次 commit。

## 禁止提交

- `.env`、密钥、证书、本地 `*.db`
- `__pycache__`、`.venv`、编辑器目录（已在 `.gitignore`）
- 无意义的大二进制；生成物（覆盖率 HTML 等）

不确定时先 `git status`，不要 `git add .` 把本地数据库加进去。

## 合并前检查

- `make lint`
- `make test`
- 有表结构变更则包含 Alembic revision，并在说明里写清
- 改了配置则同步 `.env.example` 与 [项目规范](./project.md) / 相关 docs
- PR 的 base 是 `develop`（hotfix 除外，hotfix 的 base 是 `main`，并另合 `develop`）
