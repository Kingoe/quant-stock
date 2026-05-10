# 当前迭代

本文档记录当前正在执行或即将执行的一轮任务。每轮迭代开始时更新，完成后保留结果或清空为下一轮准备。

## 当前状态

- 当前阶段：后续增强
- 当前任务：M10-1 接入更高质量数据源
- 任务来源：按 `docs/TASK_PLAN.md` 的最早未完成任务顺序推进
- 对任务顺序的影响：M10 的第一项能力已补齐，下一轮进入 M10-2
- 当前结果：已完成，新增统一数据源接口、本地 CSV 数据源和 AkShare 基础适配

## 本轮验收标准

本轮完成必须满足：

- 添加统一 `DataProvider` 接口。
- 添加 `LocalCsvProvider`，支持本地 CSV 转换为内部数据记录。
- 添加 `AkShareProvider`，先支持股票基础信息和日行情基础适配。
- 单元测试 mock AkShare，不访问真实网络。
- 缺失 CSV 必需字段时显式报错。
- `docs/TASK_PLAN.md` 将 M10-1 标记为 `Done`。
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

- M10-2 添加因子有效性分析。
