# 当前迭代

本文档记录当前正在执行或即将执行的一轮任务。每轮迭代开始时更新，完成后保留结果或清空为下一轮准备。

## 当前状态

- 当前阶段：后端基础
- 当前任务：M1-5 添加健康检查接口
- 任务来源：按 `docs/TASK_PLAN.md` 的里程碑和任务 ID 顺序推进
- 对任务顺序的影响：正常进入里程碑 1 的第五个任务

## 本轮验收标准

本轮完成必须满足：

- 创建 FastAPI 应用入口 `backend/app/main.py`。
- 新增 `GET /api/health` 健康检查接口。
- 健康检查响应遵守 `docs/API_CONVENTIONS.md` 的 `data` + `meta` 格式。
- 响应 `data.status` 为 `ok`。
- 响应 `data.service` 为 `quant-stock-backend`。
- 响应 `meta.generated_at` 为带时区的 ISO 日期时间。
- 先写失败测试，再实现代码。
- 不接入业务数据、数据库表结构或外部数据源。
- `docs/TASK_PLAN.md` 将 M1-5 标记为 `Done`。
- `docs/CHANGELOG.md` 记录本轮变更。
- Git 工作区提交后保持干净。

## 本轮验证方式

本轮验证方式：

- 运行 `uv run pytest tests/test_health_api.py`。
- 运行 `uv run pytest`。
- 运行 `uv run ruff check app tests`。
- 检查任务规划和更新日志是否同步。
- 检查 Git 状态。

## 下一轮建议

下一轮开始 M2-1：定义数据库表结构。

开始前应先更新本文档：

- 当前阶段改为：数据底座
- 当前任务改为：M2-1 定义数据库表结构
- 明确 M2-1 验收标准和验证命令
