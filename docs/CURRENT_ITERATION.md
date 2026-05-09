# 当前迭代

本文档记录当前正在执行或即将执行的一轮任务。每轮迭代开始时更新，完成后保留结果或清空为下一轮准备。

## 当前状态

- 当前阶段：后端基础
- 当前任务：M1-2 添加后端依赖配置
- 任务来源：按 `docs/TASK_PLAN.md` 的里程碑和任务 ID 顺序推进
- 对任务顺序的影响：正常进入里程碑 1 的第二个任务

## 本轮验收标准

本轮完成必须满足：

- 创建 `backend/pyproject.toml`。
- 配置项目基础信息。
- 配置运行依赖：FastAPI、uvicorn、pandas、numpy。
- 配置开发依赖：pytest、ruff。
- 配置 pytest 测试发现规则。
- 配置 ruff 检查和格式化规则。
- 不实现业务逻辑。
- `docs/TASK_PLAN.md` 将 M1-2 标记为 `Done`。
- `docs/CHANGELOG.md` 记录本轮变更。
- Git 工作区提交后保持干净。

## 本轮验证方式

本轮验证方式：

- 检查 `backend/pyproject.toml` 是否存在。
- 使用 Python 标准库解析 `backend/pyproject.toml`，确认 TOML 格式有效。
- 检查依赖配置包含 FastAPI、uvicorn、pandas、numpy、pytest、ruff。
- 检查任务规划和更新日志是否同步。
- 检查 Git 状态。

## 下一轮建议

下一轮开始 M1-3：添加配置读取模块。

开始前应先更新本文档：

- 当前阶段改为：后端基础
- 当前任务改为：M1-3 添加配置读取模块
- 明确 M1-3 验收标准和验证命令
