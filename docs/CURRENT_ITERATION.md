# 当前迭代

本文档记录当前正在执行或即将执行的一轮任务。每轮迭代开始时更新，完成后保留结果或清空为下一轮准备。

## 当前状态

- 当前阶段：数据运营增强
- 当前任务：M12-2 增加数据更新任务入口
- 任务来源：按 `docs/TASK_PLAN.md` 的最早未完成任务顺序推进
- 对任务顺序的影响：M12-2 已补齐，下一轮进入 M12-3
- 当前结果：已完成，新增 `POST /api/data/update` 手动数据更新入口，支持按数据类型触发更新并写入运行日志

## 本轮验收标准

本轮完成必须满足：

- 新增 `POST /api/data/update`，只提供手动触发入口，不做自动运行和前端页面。
- 支持 `stock_basics`、`trading_calendar`、`index_constituents`、`daily_prices`、`valuation_metrics`、`financial_metrics`。
- 支持 `local_csv` 数据源；允许 `akshare` 作为运行入口，但测试不访问真实网络。
- 成功时写入 `data_update` 运行日志，记录数据类型、数据源、更新数量和参数摘要。
- 失败时写入 `failed` 运行日志，并返回结构化错误响应。
- 空数据结果返回成功且 `records_count=0`，不把 loader 空列表限制暴露给用户。
- `docs/TASK_PLAN.md` 将 M12-2 标记为 Done，并把最早未完成任务更新为 M12-3。
- `docs/CHANGELOG.md` 记录本轮完成结果。
- `docs/TEST_CASES.md` 补充数据更新入口测试要求。
- Git 工作区提交后保持干净。

## 本轮验证方式

本轮验证方式：

- 运行 `uv run pytest tests/test_data_update_api.py -q`。
- 运行后端全量测试和 ruff 检查。
- 运行前端测试、lint 和构建，确认本轮未破坏前端。
- 运行 `git diff --check`。
- 检查任务规划、当前迭代和更新日志是否同步。
- 检查 Git 状态。

## 下一轮建议

下一轮按最早未完成任务继续：

- M12-3 增加数据更新日志 API。
