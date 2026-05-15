# 当前迭代

本文档记录当前正在执行或即将执行的一轮任务。每轮迭代开始时更新，完成后保留结果或清空为下一轮准备。

## 当前状态

- 当前阶段：数据运营增强
- 当前任务：M12-6 增加策略运行前置检查
- 任务来源：按 `docs/TASK_PLAN.md` 的最早未完成任务顺序推进
- 对任务顺序的影响：M12-6 已补齐，下一轮进入 M12-7
- 当前结果：已完成，新增 `GET /api/strategy/preflight`，并在手动运行本周策略前执行前置检查

## 本轮验收标准

本轮完成必须满足：

- 新增 `GET /api/strategy/preflight`，按评分日输出策略运行前置检查结果。
- 前置检查存在 error 时返回 `blocked` 并阻止策略运行。
- 前置检查只有 warning 时返回 `warning`，允许策略运行并返回风险提示。
- 前置检查完全通过时返回 `passed`。
- `POST /api/jobs/run-weekly-strategy` 运行前必须调用前置检查。
- 前置检查结果必须写入手动策略运行响应和运行日志。
- `docs/TASK_PLAN.md` 将 M12-6 标记为 Done，并把最早未完成任务更新为 M12-7。
- `docs/CHANGELOG.md` 记录本轮完成结果。
- `docs/TEST_CASES.md` 补充策略前置检查测试要求。
- Git 工作区提交后保持干净。

## 本轮验证方式

本轮验证方式：

- 运行 `uv run pytest tests/test_strategy_preflight.py tests/test_strategy_preflight_api.py tests/test_run_weekly_strategy_api.py -q`。
- 运行后端全量测试和 ruff 检查。
- 运行前端测试、lint 和构建，确认本轮未破坏前端。
- 运行 `git diff --check`。
- 检查任务规划、当前迭代和更新日志是否同步。
- 检查 Git 状态。

## 下一轮建议

下一轮按最早未完成任务继续：

- M12-7 增加一键生成本周完整报告流程。
