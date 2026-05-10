# 当前迭代

本文档记录当前正在执行或即将执行的一轮任务。每轮迭代开始时更新，完成后保留结果或清空为下一轮准备。

## 当前状态

- 当前阶段：前端工作台
- 当前任务：M7-9 添加前端测试
- 任务来源：按 `docs/TASK_PLAN.md` 的最早未完成任务顺序推进
- 对任务顺序的影响：补齐 M7 最后一个任务后，下一轮进入 M8-3
- 当前结果：已完成，新增 Vitest + Testing Library 测试环境，覆盖工作台导航和 API 失败兜底状态

## 本轮验收标准

本轮完成必须满足：

- 添加前端测试运行脚本。
- 接入 Vitest、jsdom、Testing Library。
- 添加工作台导航测试，确保默认展示总览并可切换到本周调仓页。
- 添加 API 失败兜底测试，确保接口失败时返回稳定空状态。
- `docs/TASK_PLAN.md` 将 M7-9 标记为 `Done`。
- `docs/CHANGELOG.md` 记录本轮核验和修复结果。
- Git 工作区提交后保持干净。

## 本轮验证方式

本轮验证方式：

- 运行 `npm test`。
- 运行 `npm run lint`。
- 使用 Node.js 20.19 或更高版本运行 `npm run build`。
- 运行 `uv run pytest`。
- 运行 `uv run ruff check app tests`。
- 运行 `uv run ruff format --check app tests`。
- 检查任务规划、当前迭代和更新日志是否同步。
- 检查 Git 状态。

## 下一轮建议

下一轮按最早未完成任务继续：

- M8-3 添加一键运行本周策略。
- 然后补 M9-4 添加模拟运行页面区域。
