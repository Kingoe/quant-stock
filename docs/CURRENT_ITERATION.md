# 当前迭代

本文档记录当前正在执行或即将执行的一轮任务。每轮迭代开始时更新，完成后保留结果或清空为下一轮准备。

## 当前状态

- 当前阶段：报告与自动运行
- 当前任务：M8-3 添加一键运行本周策略
- 任务来源：按 `docs/TASK_PLAN.md` 的最早未完成任务顺序推进
- 对任务顺序的影响：补齐 M8 中被跳过的手动触发任务后，下一轮进入 M9-4
- 当前结果：已完成，新增手动运行策略 API、运行日志审计和前端一键运行入口

## 本轮验收标准

本轮完成必须满足：

- 添加 `POST /api/jobs/run-weekly-strategy`。
- 接口复用 `generate_weekly_rebalance`，返回建议数量和买入、持有、卖出、观察统计。
- 接口创建 `weekly_strategy` 运行日志，成功标记 success，失败标记 failed。
- 前端“本周调仓”页添加“运行本周策略”按钮。
- 前端展示运行中、运行成功、运行失败状态。
- `docs/TASK_PLAN.md` 将 M8-3 标记为 `Done`。
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

- M9-4 添加模拟运行页面区域。
