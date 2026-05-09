# Quant Stock

个人 A 股多因子选股辅助系统。

这个项目第一阶段**不做自动下单**，而是先帮助你完成数据更新、股票池过滤、因子评分、历史回测、每周调仓建议和前端可视化展示。真实交易仍然由你人工确认。

## 项目目标

把个人股票交易流程整理成一个可复盘、可测试、可迭代的系统：

- 自动更新 A 股相关数据
- 从中证 800 等股票池中筛选可交易股票
- 根据估值、质量、成长、动量、风险、流动性等因子打分
- 每周生成买入、卖出、持有、观察列表
- 回测历史表现
- 在本地前端页面中清晰展示结果
- 导出报告，辅助人工交易决策

## 项目文档

- [技术架构](docs/TECHNICAL_ARCHITECTURE.md)
- [任务规划](docs/TASK_PLAN.md)
- [测试用例](docs/TEST_CASES.md)
- [项目约束](docs/PROJECT_CONSTRAINTS.md)
- [迭代流程](docs/ITERATION_WORKFLOW.md)
- [开发环境](docs/DEVELOPMENT_SETUP.md)
- [当前迭代](docs/CURRENT_ITERATION.md)
- [架构决策记录](docs/DECISIONS.md)
- [数据源计划](docs/DATA_SOURCE_PLAN.md)
- [API 约定](docs/API_CONVENTIONS.md)
- [更新日志](docs/CHANGELOG.md)

## 第一版范围

- 股票池：中证 800
- 调仓频率：每周一次
- 策略风格：均衡型多因子
- 持仓数量：10-20 只股票
- 数据库：SQLite
- 后端：Python + FastAPI
- 前端：React + TypeScript
- 图表：ECharts
- 输出：回测结果、每周调仓建议、Excel 或 CSV 导出
- 明确不做：自动下单、实盘交易接口、高频交易

## 文档维护规则

后续每次迭代都要同步更新文档：

- 任务有进展：更新 [任务规划](docs/TASK_PLAN.md)
- 架构有变化：更新 [技术架构](docs/TECHNICAL_ARCHITECTURE.md)
- 行为或测试范围变化：更新 [测试用例](docs/TEST_CASES.md)
- 项目边界或风格变化：更新 [项目约束](docs/PROJECT_CONSTRAINTS.md)
- 迭代流程变化：更新 [迭代流程](docs/ITERATION_WORKFLOW.md)
- 开发环境变化：更新 [开发环境](docs/DEVELOPMENT_SETUP.md)
- 当前任务验收标准变化：更新 [当前迭代](docs/CURRENT_ITERATION.md)
- 关键技术选择变化：更新 [架构决策记录](docs/DECISIONS.md)
- 数据源变化：更新 [数据源计划](docs/DATA_SOURCE_PLAN.md)
- API 响应格式变化：更新 [API 约定](docs/API_CONVENTIONS.md)
- 完成了可见变更：更新 [更新日志](docs/CHANGELOG.md)

文档是项目方向和进度的准绳，后续迭代不能脱离这些约束随意扩散。
