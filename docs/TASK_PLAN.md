# 任务规划

本文档用于跟踪项目进度。每次迭代都要更新。

状态说明：

- Not Started：未开始
- In Progress：进行中
- Blocked：阻塞
- Done：已完成

## 当前里程碑

当前应优先推进的最早未完成任务：M12-1 完善 AkShare 数据源字段覆盖。

说明：2026-05-10 检查时发现外部终端已提前完成 M8/M9 的部分任务。已完成并通过验证的任务按真实状态记录为 Done；仍未完成的任务保持 Not Started。后续继续按最早未完成任务补齐，不再随机跳跃。

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
| M3-2 | 实现 ST 过滤 | Done | 已支持从股票列表中过滤 ST 和 *ST 股票，基于 is_st 字段判断 |
| M3-3 | 实现上市时间过滤 | Done | 已支持从股票列表中过滤上市不足一年的股票，基于 list_date 字段判断，支持配置上市月数阈值 |
| M3-4 | 实现停牌过滤 | Done | 已支持从股票列表中过滤停牌股票，基于 daily_prices 表的 is_suspended 字段判断，支持按日期判断停牌状态 |
| M3-5 | 实现流动性过滤 | Done | 已支持从股票列表中过滤流动性不足的股票，基于近 20 日平均成交额判断，支持配置成交额阈值 |
| M3-6 | 实现估值异常过滤 | Done | 已支持从股票列表中过滤估值异常的股票，剔除负数、零或过大的 PE/PB，允许指标为 null，支持配置 PE/PB 上限 |
| M3-7 | 添加股票池接口和测试 | Done | 已新增 /api/universe 接口，支持全量过滤、分页和参数配置 |

## 里程碑 4：因子计算

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M4-1 | 实现因子输入数据对齐 | Done | 已实现日行情、估值、财务数据对齐，只使用评分日已生效数据 |
| M4-2 | 实现估值因子 | Done | 已实现 PE、PB、股息率估值因子计算，支持权重配置 |
| M4-3 | 实现质量因子 | Done | 已实现 ROE、毛利率、现金流质量因子计算，支持权重配置 |
| M4-4 | 实现成长因子 | Done | 已实现营收增速、净利润增速成长因子计算，支持权重配置 |
| M4-5 | 实现动量因子 | Done | 已实现 60 日和 120 日涨跌幅动量因子计算，支持权重配置 |
| M4-6 | 实现风险因子 | Done | 已实现波动率和最大回撤风险因子计算，支持权重配置 |
| M4-7 | 实现流动性因子 | Done | 已实现近 20 日平均成交额流动性因子计算，支持权重配置 |
| M4-8 | 实现去极值和排名 | Done | 已实现可复用去极值和 0-1 排名工具 |
| M4-9 | 实现加权总分 | Done | 已实现多因子加权总分计算，使用第一版初始权重 |

## 里程碑 5：组合构建

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M5-1 | 选择排名靠前候选股 | Done | 已实现按总分选择排名靠前候选股 |
| M5-2 | 应用单票仓位上限 | Done | 已实现等权目标仓位和单票仓位上限裁剪 |
| M5-3 | 应用行业仓位上限 | Done | 已实现行业累计仓位上限裁剪 |
| M5-4 | 生成买入、卖出、持有、观察列表 | Done | 每周调仓输出 |
| M5-5 | 添加交易可用性提示 | Done | 涨停、跌停、停牌 |
| M5-6 | 添加调仓接口和测试 | Done | 前端数据来源 |

## 里程碑 6：回测引擎

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M6-1 | 实现周频调仓调度 | Done | 收盘后生成信号，下个交易日执行，已实现 generate_weekly_rebalance_dates 和 get_next_trade_date_after，覆盖 Friday 选择、非交易日过滤、空数据处理、排序和下一个交易日查询 |
| M6-2 | 实现订单生成 | Done | 处理目标仓位和 100 股整数手，已实现 generate_orders 函数，支持买入、卖出、调仓场景，股数按 100 股取整，差异小于 50 股时不交易，按股票代码排序 |
| M6-3 | 实现交易成本 | Done | 佣金、印花税、滑点，已实现 TradingCost 和 TradeResult 数据结构，calculate_trading_cost 函数支持买入/卖出成本计算，佣金含最低值规则，印花税仅卖出收取，滑点影响执行价格，新增 11 项测试覆盖全部场景 |
| M6-4 | 实现 A 股交易限制 | Done | T+1、涨跌停、停牌，已实现 TradingConstraints 和 TradingDayStatus 数据结构，filter_orders_by_trading_constraints 函数支持订单过滤，T+1 阻止当日买入当日卖出，涨停阻止买入，跌停阻止卖出，停牌阻止所有交易，新增 14 项测试覆盖全部约束场景 |
| M6-5 | 实现持仓和现金记账 | Done | 组合流水，已实现 Portfolio 和 PortfolioSnapshot 数据结构，apply_trade 函数支持买入/卖出更新持仓和现金，calculate_portfolio_value/calculate_position_value 计算组合总价值和持仓市值，create_snapshot 创建组合快照，create_initial_portfolio 创建初始组合，新增 17 项测试覆盖交易、价值计算和快照 |
| M6-6 | 实现绩效指标 | Done | 收益、回撤、夏普、换手，已实现 PerformanceMetrics 和 DailyReturn 数据结构，calculate_total_return/calculate_annual_return 计算总收益率和年化收益率，calculate_max_drawdown 计算最大回撤，calculate_sharpe_ratio 计算夏普比率，calculate_turnover_rate 计算换手率，calculate_win_rate 计算胜率，calculate_performance_metrics 串联全部指标计算，新增 18 项测试覆盖全部指标和边界条件 |
| M6-7 | 实现基准对比 | Done | 沪深 300 和中证 500，已实现 calculate_benchmark_return 计算基准收益率，calculate_cumulative_returns 计算累计收益率序列，calculate_benchmark_cumulative_returns 计算基准累计收益率，align_strategy_and_benchmark_dates 对齐策略和基准日期，新增 13 项测试覆盖基准收益计算、累计收益率、日期对齐和边界条件 |
| M6-8 | 添加回测接口和测试 | Done | 概览和图表数据，已实现 get_backtest_summary 获取回测概览（核心指标），get_equity_curve 获取净值曲线，get_drawdown_curve 获取回撤曲线，遵循 data + meta API 响应约定，新增 portfolio_snapshots 表存储组合快照，新增 7 项测试覆盖空数据、API 约定和参数配置 |

## 里程碑 7：前端工作台

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M7-1 | 创建 React 项目 | Done | Vite + TypeScript，已创建 frontend 目录，配置 Tailwind CSS 和 Vite 代理，创建 6 个页面组件（总览、本周调仓、因子评分、回测分析、策略配置、数据状态）和导航布局 |
| M7-2 | 创建整体布局和导航 | Done | 专业投研工作台风格，已创建左侧导航栏和主内容区域，支持 6 个页面切换，使用 Tailwind CSS 样式，侧边栏固定宽度，主内容区域自适应 |
| M7-3 | 实现总览页 | Done | 核心指标和图表，已创建 6 项核心指标卡片（总收益率、年化收益率、最大回撤、夏普比率、换手率、胜率）和净值曲线占位区域，使用 Grid 布局响应式设计 |
| M7-4 | 实现本周调仓页 | Done | 买入、卖出、持有、观察表格，已创建 4 个卡片布局，每个包含列表数量和占位区域，使用 Grid 布局响应式设计 |
| M7-5 | 实现因子评分页 | Done | 可搜索、可排序的评分表，已创建搜索框和占位区域，使用 Flex 布局 |
| M7-6 | 实现回测分析页 | Done | 收益、回撤、指标，已创建 3 个区域（指标、净值曲线、回撤曲线），每个包含占位区域 |
| M7-7 | 实现策略配置页 | Done | 第一版只读，已创建占位区域 |
| M7-8 | 实现数据状态页 | Done | 数据新鲜度和任务日志，已创建占位区域 |
| M7-9 | 添加前端测试 | Done | 已接入 Vitest + Testing Library，覆盖工作台导航和 API 失败兜底状态 |

## 里程碑 8：报告与自动运行

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M8-1 | 生成每周 HTML 报告 | Done | 已新增 `/api/rebalance/html` 和 HTML 周报生成测试 |
| M8-2 | 生成 Excel 或 CSV 导出 | Done | 已新增 `/api/rebalance/excel`、`/api/rebalance/csv` 和导出测试 |
| M8-3 | 添加一键运行本周策略 | Done | 已新增 `POST /api/jobs/run-weekly-strategy`、运行日志记录和前端手动运行按钮 |
| M8-4 | 添加定时数据更新 | Done | 已新增 APScheduler 本地调度封装和测试 |
| M8-5 | 添加运行日志 | Done | 已新增 run_logs 记录、状态更新、最近日志查询和测试 |

## 里程碑 9：模拟运行

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M9-1 | 添加模拟交易账本 | Done | 已新增 SimulationLedger、模拟账户、订单、持仓和测试 |
| M9-2 | 跟踪策略建议 | Done | 已新增策略信号、执行记录、待执行信号和执行摘要测试 |
| M9-3 | 跟踪模拟组合净值 | Done | 已新增组合快照、收益、回撤、夏普、波动率分析和测试 |
| M9-4 | 添加模拟运行页面区域 | Done | 已新增 `/api/simulation/summary` 和总览页模拟运行区域，展示资产、收益、回撤和信号执行 |

## 里程碑 10：后续增强

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M10-1 | 接入更高质量数据源 | Done | 已新增统一 DataProvider、LocalCsvProvider 和 AkShareProvider 基础适配，单元测试不访问网络 |
| M10-2 | 添加因子有效性分析 | Done | 已新增未来收益、IC、Rank IC 和分层收益分析工具 |
| M10-3 | 添加行业中性化 | Done | 已新增行业内排名中性化工具，降低无意行业暴露 |
| M10-4 | 添加参数实验跟踪 | Done | 已新增参数实验记录表和查询工具，记录参数、指标、备注和创建时间 |
| M10-5 | 添加通知渠道 | Done | 已新增通知消息模型、本地数据库通知通道和通知历史查询 |
| M10-6 | 评估券商接口 | Done | 已新增券商准入评估工具和评估文档，只允许进入人工试点评审，不开放自动下单 |

## 里程碑 11：前端运营化页面

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M11-1 | 添加实验记录 API | Done | 已新增 `/api/experiments` 和 `/api/experiments/{experiment_id}` |
| M11-2 | 添加实验记录页面 | Done | 已新增实验记录导航和页面，展示列表、指标、参数详情、空状态和接口失败兜底 |
| M11-3 | 添加通知历史 API | Done | 已新增 `/api/notifications`，支持通道过滤和数量限制 |
| M11-4 | 添加通知历史页面 | Done | 已新增通知历史导航和页面，展示通道、级别、状态、时间、失败原因和元数据摘要 |
| M11-5 | 添加券商准入评估 API | Done | 已新增 `/api/broker/readiness`，返回准入状态、失败原因、只读动作边界和非实盘入口提示 |
| M11-6 | 添加券商准入评估页面 | Done | 已新增券商准入导航和页面，明确展示不自动下单、准入条件、失败原因和只读动作 |

## 里程碑 12：数据运营增强

| ID | 任务 | 状态 | 备注 |
| --- | --- | --- | --- |
| M12-1 | 完善 AkShare 数据源字段覆盖 | Not Started | 补齐指数成分、估值、财务、交易日历等适配能力，单元测试使用 mock |
| M12-2 | 增加数据更新任务入口 | Not Started | 支持按数据类型手动触发更新，并写入运行日志 |
| M12-3 | 增加数据更新日志 API | Not Started | 查询数据更新任务状态、错误和结果摘要 |
| M12-4 | 增加数据更新日志页面 | Not Started | 在前端展示更新任务列表、状态和错误信息 |
| M12-5 | 增加数据质量检查报告 | Not Started | 检查数据新鲜度、缺失字段、异常字段和财务披露日期 |
| M12-6 | 增加策略运行前置检查 | Not Started | 运行策略前检查关键数据质量，不满足条件时阻止运行并说明原因 |
| M12-7 | 增加一键生成本周完整报告流程 | Not Started | 串联前置检查、策略运行、通知和报告导出 |

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
