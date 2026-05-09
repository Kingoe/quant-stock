# 当前迭代

本文档记录当前正在执行或即将执行的一轮任务。每轮迭代开始时更新，完成后保留结果或清空为下一轮准备。

## 当前状态

- 当前阶段：后端基础
- 当前任务：M1-3 添加配置读取模块
- 任务来源：按 `docs/TASK_PLAN.md` 的里程碑和任务 ID 顺序推进
- 对任务顺序的影响：正常进入里程碑 1 的第三个任务

## 本轮验收标准

本轮完成必须满足：

- 创建 `backend/app/config/` 配置模块。
- 支持从 TOML 文件读取应用运行配置。
- 支持从 TOML 文件读取第一版策略配置。
- 对持仓数量、仓位上限、行业上限、因子权重、交易成本做基础校验。
- 提供默认配置文件 `backend/config/default.toml`。
- 先写失败测试，再实现代码。
- 不接入数据库、API 或数据源。
- `docs/TASK_PLAN.md` 将 M1-3 标记为 `Done`。
- `docs/CHANGELOG.md` 记录本轮变更。
- Git 工作区提交后保持干净。

## 本轮验证方式

本轮验证方式：

- 运行 `uv run pytest backend/tests/test_config_loader.py`。
- 运行 `uv run ruff check backend/app backend/tests`。
- 检查任务规划和更新日志是否同步。
- 检查 Git 状态。

## 下一轮建议

下一轮开始 M1-4：添加 SQLite 连接层。

开始前应先更新本文档：

- 当前阶段改为：后端基础
- 当前任务改为：M1-4 添加 SQLite 连接层
- 明确 M1-4 验收标准和验证命令
