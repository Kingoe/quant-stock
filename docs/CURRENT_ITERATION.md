# 当前迭代

本文档记录当前正在执行或即将执行的一轮任务。每轮迭代开始时更新，完成后保留结果或清空为下一轮准备。

## 当前状态

- 当前阶段：前端运营化页面
- 当前任务：M11-1 添加实验记录 API
- 任务来源：按 `docs/TASK_PLAN.md` 的最早未完成任务顺序推进
- 对任务顺序的影响：M11-1 已补齐，下一轮进入 M11-2
- 当前结果：已完成，新增实验记录列表和详情 API

## 本轮验收标准

本轮完成必须满足：

- 新增 `GET /api/experiments`，返回最近参数实验列表。
- `GET /api/experiments` 支持 `limit` 参数并进行范围校验。
- 新增 `GET /api/experiments/{experiment_id}`，返回单条实验详情。
- 不存在的实验返回 404。
- API 遵守 `data + meta` 响应约定。
- 新增后端 API 测试覆盖列表、详情、404 和参数校验。
- `docs/TASK_PLAN.md` 将 M11-1 标记为 `Done`。
- `docs/CHANGELOG.md` 记录本轮核验和修复结果。
- Git 工作区提交后保持干净。

## 本轮验证方式

本轮验证方式：

- 运行 `uv run pytest`。
- 运行 `uv run ruff check app tests`。
- 运行 `uv run ruff format --check app tests`。
- 运行 `npm test`。
- 运行 `npm run lint`。
- 使用 Node.js 20.19 或更高版本运行 `npm run build`。
- 检查任务规划、当前迭代和更新日志是否同步。
- 检查 Git 状态。

## 下一轮建议

下一轮按最早未完成任务继续：

- M11-2 添加实验记录页面。
