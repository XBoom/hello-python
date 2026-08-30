# Git 与协作规范

## 采用的外部规范

提交说明遵循 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/v1.0.0/)。

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

## 分支

- `main`：可发布。
- 功能：`feat/<short-name>`；修复：`fix/<short-name>`。
- 不要直接 force push `main`。

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
