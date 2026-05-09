# 任务规划

本文档用于跟踪项目进度。每次迭代都要更新。

状态说明：

- Not Started：未开始
- In Progress：进行中
- Blocked：阻塞
- Done：已完成

## 当前里程碑

里程碑 0：项目基础与文档。

## 里程碑 0：项目基础

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M0-1 | 创建项目目录 | Done | 项目根目录：`/Users/jinwu/work/hub/quant-stock` |
| M0-2 | 创建技术架构文档 | Done | 见 `docs/TECHNICAL_ARCHITECTURE.md` |
| M0-3 | 创建任务规划文档 | Done | 本文档 |
| M0-4 | 创建测试用例文档 | Done | 见 `docs/TEST_CASES.md` |
| M0-5 | 创建项目约束文档 | Done | 见 `docs/PROJECT_CONSTRAINTS.md` |
| M0-6 | 创建更新日志 | Done | 见 `docs/CHANGELOG.md` |
| M0-7 | 初始化 Git 仓库 | Done | 已在项目根目录初始化 |
| M0-8 | 将文档调整为中文优先 | Done | 保留必要英文技术术语 |
| M0-9 | 创建迭代流程文档 | Done | 见 `docs/ITERATION_WORKFLOW.md` |
| M0-10 | 明确任务必须按规划顺序执行 | Done | 默认按里程碑和任务 ID 顺序推进 |
| M0-11 | 明确开发环境和启动方式 | Done | 见 `docs/DEVELOPMENT_SETUP.md` |
| M0-12 | 明确代码质量和测试工具 | Done | 见 `docs/DEVELOPMENT_SETUP.md` |
| M0-13 | 新增架构决策记录 | Done | 见 `docs/DECISIONS.md` |
| M0-14 | 新增当前迭代验收模板 | Done | 见 `docs/CURRENT_ITERATION.md` |
| M0-15 | 新增数据源预研计划 | Done | 见 `docs/DATA_SOURCE_PLAN.md` |
| M0-16 | 明确 API 响应约定 | Done | 见 `docs/API_CONVENTIONS.md` |

## 里程碑 1：后端基础

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M1-1 | 创建 Python 项目结构 | Done | 已创建 `backend/app`、`backend/tests` 和后端说明文档 |
| M1-2 | 添加后端依赖配置 | Done | 已创建 `backend/pyproject.toml`，配置运行依赖、开发依赖、pytest 和 ruff |
| M1-3 | 添加配置读取模块 | Done | 已支持 TOML 配置读取、默认配置和基础校验 |
| M1-4 | 添加 SQLite 连接层 | Done | 已支持 SQLite URL 解析、连接创建、目录创建、提交和关闭 |
| M1-5 | 添加健康检查接口 | Done | 已新增 FastAPI 应用入口和 `GET /api/health` |

## 里程碑 2：数据底座

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M2-1 | 定义数据库表结构 | Done | 已定义 stocks、trading_calendar、index_constituents、daily_prices、valuation_metrics、financial_metrics、strategy_runs、rebalance_recommendations |
| M2-2 | 实现交易日历加载 | Done | 已支持交易日历入库、更新、开市日期查询和下一交易日查询 |
| M2-3 | 实现股票基础信息加载 | Done | 已支持股票基础信息入库、更新、按代码查询和 active 股票代码查询 |
| M2-4 | 实现中证 800 成分股加载 | Done | 已支持指数成分入库、权重更新、按日期查询和按目标日期查询最新可用成分 |
| M2-5 | 实现日行情加载 | Done | 已支持日行情入库、更新、按股票区间查询和按交易日查询 |
| M2-6 | 实现估值数据加载 | Done | 已支持估值数据入库、更新、按股票区间查询和按交易日查询，允许部分字段为空 |
| M2-7 | 实现财务数据加载 | Done | 已支持财务数据入库、更新、按股票代码和报告期区间查询，允许部分字段为空 |
| M2-8 | 实现数据状态检查 | Done | 已支持查询各数据类型最新日期和数据状态汇总，支持日行情、估值、财务数据 |

## 里程碑 3：股票池过滤

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M3-1 | 实现中证 800 基础股票池查询 | Done | 已支持按调仓日期查询基础股票池，使用最新可用指数成分，过滤非活跃股票 |
| M3-2 | 实现 ST 过滤 | Not Started | 剔除 ST 和 *ST |
| M3-3 | 实现上市时间过滤 | Not Started | 剔除上市不足一年 |
| M3-4 | 实现停牌过滤 | Not Started | 剔除不可交易股票 |
| M3-5 | 实现流动性过滤 | Not Started | 基于近 20 日平均成交额 |
| M3-6 | 实现估值异常过滤 | Not Started | 剔除无效 PE/PB |
| M3-7 | 添加股票池接口和测试 | Not Started | 方便页面和调试使用 |

## 里程碑 4：因子计算

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M4-1 | 实现因子输入数据对齐 | Not Started | 只使用评分日已生效数据 |
| M4-2 | 实现估值因子 | Not Started | PE、PB、股息率 |
| M4-3 | 实现质量因子 | Not Started | ROE、毛利率、现金流质量 |
| M4-4 | 实现成长因子 | Not Started | 营收和利润增长 |
| M4-5 | 实现动量因子 | Not Started | 60 日和 120 日涨跌幅 |
| M4-6 | 实现风险因子 | Not Started | 波动率和最大回撤 |
| M4-7 | 实现流动性因子 | Not Started | 20 日平均成交额 |
| M4-8 | 实现去极值和排名 | Not Started | 降低极端值影响 |
| M4-9 | 实现加权总分 | Not Started | 使用初始均衡权重 |

## 里程碑 5：组合构建

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M5-1 | 选择排名靠前候选股 | Not Started | 目标持仓 10-20 只 |
| M5-2 | 应用单票仓位上限 | Not Started | 5%-10% |
| M5-3 | 应用行业仓位上限 | Not Started | 25%-30% |
| M5-4 | 生成买入、卖出、持有、观察列表 | Not Started | 每周调仓输出 |
| M5-5 | 添加交易可用性提示 | Not Started | 涨停、跌停、停牌 |
| M5-6 | 添加调仓接口和测试 | Not Started | 前端数据来源 |

## 里程碑 6：回测引擎

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M6-1 | 实现周频调仓调度 | Not Started | 收盘后生成信号，下个交易日执行 |
| M6-2 | 实现订单生成 | Not Started | 处理目标仓位和 100 股整数手 |
| M6-3 | 实现交易成本 | Not Started | 佣金、印花税、滑点 |
| M6-4 | 实现 A 股交易限制 | Not Started | T+1、涨跌停、停牌 |
| M6-5 | 实现持仓和现金记账 | Not Started | 组合流水 |
| M6-6 | 实现绩效指标 | Not Started | 收益、回撤、夏普、换手 |
| M6-7 | 实现基准对比 | Not Started | 沪深 300 和中证 500 |
| M6-8 | 添加回测接口和测试 | Not Started | 概览和图表数据 |

## 里程碑 7：前端工作台

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M7-1 | 创建 React 项目 | Not Started | Vite + TypeScript |
| M7-2 | 创建整体布局和导航 | Not Started | 专业投研工作台风格 |
| M7-3 | 实现总览页 | Not Started | 核心指标和图表 |
| M7-4 | 实现本周调仓页 | Not Started | 买入、卖出、持有、观察表格 |
| M7-5 | 实现因子评分页 | Not Started | 可搜索、可排序的评分表 |
| M7-6 | 实现回测分析页 | Not Started | 收益、回撤、指标 |
| M7-7 | 实现策略配置页 | Not Started | 第一版只读 |
| M7-8 | 实现数据状态页 | Not Started | 数据新鲜度和任务日志 |
| M7-9 | 添加前端测试 | Not Started | 组件和接口状态测试 |

## 里程碑 8：报告与自动运行

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M8-1 | 生成每周 HTML 报告 | Not Started | 人可读的周报 |
| M8-2 | 生成 Excel 或 CSV 导出 | Not Started | 调仓和因子明细 |
| M8-3 | 添加一键运行本周策略 | Not Started | 手动触发后端任务 |
| M8-4 | 添加定时数据更新 | Not Started | 本地定时运行 |
| M8-5 | 添加运行日志 | Not Started | 便于排查和审计 |

## 里程碑 9：模拟运行

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M9-1 | 添加模拟交易账本 | Not Started | 不产生真实订单 |
| M9-2 | 跟踪策略建议 | Not Started | 对比信号和模拟结果 |
| M9-3 | 跟踪模拟组合净值 | Not Started | 连续观察 1-3 个月 |
| M9-4 | 添加模拟运行页面区域 | Not Started | 展示偏差和结果 |

## 里程碑 10：后续增强

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M10-1 | 接入更高质量数据源 | Not Started | 替换或补充 akshare |
| M10-2 | 添加因子有效性分析 | Not Started | IC、Rank IC、分层收益 |
| M10-3 | 添加行业中性化 | Not Started | 降低无意行业暴露 |
| M10-4 | 添加参数实验跟踪 | Not Started | 避免随意调参 |
| M10-5 | 添加通知渠道 | Not Started | 邮件、飞书、企业微信 |
| M10-6 | 评估券商接口 | Not Started | 仅在模拟稳定后考虑 |

## 迭代更新规则

每次迭代必须遵守 `docs/ITERATION_WORKFLOW.md`。

默认执行顺序：

- 按里程碑顺序推进。
- 同一里程碑内按任务 ID 顺序推进。
- 不随机选择任务。
- 跳过或提前任务必须记录原因。

迭代结束时：

1. 将完成的任务标记为 Done。
2. 将当前任务标记为 In Progress 或 Blocked。
3. 把新发现的任务加入对应里程碑。
4. 更新 `docs/CHANGELOG.md`。
5. 如果行为、架构、测试或约束发生变化，同步更新对应文档。
