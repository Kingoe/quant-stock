# 技术架构

## 1. 项目定位

Quant Stock 是一个个人 A 股多因子选股辅助系统。

第一阶段目标不是自动交易，而是形成一个可解释、可回测、可复盘的辅助决策流程：

1. 更新行情、估值、财务、指数成分等数据。
2. 构建可交易股票池。
3. 计算多因子评分。
4. 生成周频目标组合。
5. 运行历史回测。
6. 输出每周调仓建议。
7. 通过本地 Web 页面展示结果。
8. 由用户人工确认真实交易。

## 2. 技术栈

### 后端

- 语言：Python
- API 框架：FastAPI
- 数据处理：pandas、numpy
- 数据库：SQLite
- 定时任务：APScheduler 或系统定时任务
- 导出：CSV、Excel
- 测试：pytest

### 前端

- 框架：React
- 语言：TypeScript
- 构建工具：Vite
- 图表：ECharts
- 表格：TanStack Table 或轻量自定义表格
- 样式：Tailwind CSS 或 CSS modules

### 数据源

- 第一版：akshare
- 后续可选：tushare、聚宽、米筐、付费数据源、券商数据

## 3. 目录结构

```text
quant-stock/
  README.md
  docs/
    TECHNICAL_ARCHITECTURE.md
    TASK_PLAN.md
    TEST_CASES.md
    PROJECT_CONSTRAINTS.md
    CHANGELOG.md

  backend/
    pyproject.toml
    config/
      default.toml
    app/
      main.py
      api/          # API 接口
      config/       # 配置读取
      data/         # 数据加载和数据源接入
      storage/      # SQLite 读写
      universe/     # 股票池过滤
      factors/      # 因子计算
      scoring/      # 因子打分
      portfolio/    # 组合构建
      backtest/     # 回测引擎
      reports/      # 报告导出
      risk/         # 风控规则
      scheduler/    # 定时任务
    tests/

  frontend/
    package.json
    src/
      pages/
      components/
      api/
      styles/
    tests/

  data/
    quant.db
    exports/
    raw/

  scripts/
```

## 4. 系统流程

```text
数据源
  -> SQLite 本地存储
  -> 股票池过滤
  -> 因子计算
  -> 因子打分
  -> 组合构建
  -> 回测引擎
  -> 报告和 API
  -> 前端工作台
```

## 5. 核心数据

第一版需要存储或计算：

- 股票基础信息：代码、名称、交易所、上市日期、行业、状态
- 指数成分：沪深 300、中证 500、中证 800
- 日行情：开盘价、最高价、最低价、收盘价、成交量、成交额、复权价
- 估值数据：PE、PB、PS、股息率
- 财务数据：ROE、毛利率、营收增速、净利润增速、经营现金流
- 交易状态：停牌、涨停、跌停、ST 状态
- 交易日历
- 策略运行记录
- 调仓建议
- 回测持仓、交易流水、绩效指标

第一版 SQLite schema 已包含：

- `stocks`：股票基础信息。
- `trading_calendar`：交易日历。
- `index_constituents`：指数成分。
- `daily_prices`：日行情和交易状态。
- `valuation_metrics`：估值数据。
- `financial_metrics`：财务数据和披露日期。
- `strategy_runs`：策略运行记录。
- `rebalance_recommendations`：调仓建议。

当前已实现的数据加载能力：

- 交易日历加载：写入 `trading_calendar` 表，维护上一/下一开市日，支持开市日期查询。
- 股票基础信息加载：写入 `stocks` 表，支持更新和 active 非 ST 股票代码查询。
- 指数成分加载：写入 `index_constituents` 表，支持权重更新、按日期查询和最新可用成分查询。
- 日行情加载：写入 `daily_prices` 表，支持行情更新、按股票区间查询和按交易日查询。

当前已实现的因子计算能力：

- 数据对齐：按评分日对齐日行情、估值和已披露财务数据。
- 估值因子：基于 PE、PB、股息率计算。
- 质量因子：基于 ROE、毛利率、现金流质量计算。
- 成长因子：基于营收增速、净利润增速计算。
- 动量因子：基于 60 日和 120 日涨跌幅计算，优先使用复权收盘价。
- 风险因子：基于评分日前 120 天内的波动率和最大回撤计算，低风险得分更高。
- 流动性因子：基于评分日前近 20 日平均成交额计算，成交额越高得分越高。
- 因子工具：支持分位数去极值、0-1 排名、高值/低值方向配置和缺失值中性处理。
- 加权总分：按估值 25%、质量 25%、成长 20%、动量 20%、风险 5%、流动性 5% 合成总分。

当前已实现的组合构建能力：

- 候选股选择：按总分从高到低选择排名靠前股票，支持数量限制和同分稳定排序。
- 目标仓位生成：按候选股等权生成目标仓位，并应用单票仓位上限。

## 6. 股票池规则

第一版基础股票池：中证 800。

过滤规则：

- 剔除 ST 和 *ST 股票。
- 剔除上市不足一年的股票。
- 剔除停牌股票。
- 剔除成交额过低的股票。
- 剔除 PE、PB 异常的股票。
- 在可靠数据可用时，剔除财务明显异常的公司。
- 剔除调仓执行日无法正常交易的股票。

## 7. 因子模型

第一版采用均衡型多因子模型。

因子分组：

- 估值：PE、PB、股息率
- 质量：ROE、毛利率、经营现金流 / 净利润
- 成长：营收增速、净利润增速
- 动量：近 60 日涨跌幅、近 120 日涨跌幅
- 风险：波动率、最大回撤
- 流动性：近 20 日平均成交额

初始权重：

- 估值：25%
- 质量：25%
- 成长：20%
- 动量：20%
- 风险和流动性：10%

当前实现中，风险和流动性各占 5%，合计对应第一版 10% 的风险和流动性权重。

打分流程：

1. 按有效日期对齐数据。
2. 删除不可用数据。
3. 对极端值做 winsorize 去极值处理。
4. 对每个因子做标准化或分位数排名。
5. 对“越低越好”的因子做反向处理。
6. 按权重计算总分。
7. 应用风控和组合约束。

## 8. 组合规则

第一版组合规则：

- 每周调仓一次。
- 持仓 10-20 只股票。
- 单只股票最高仓位 5%-10%。
- 单个行业最高仓位 25%-30%。
- 保留少量现金缓冲。
- 无法买入的股票跳过。
- 因停牌或跌停无法卖出的股票保留并标记风险。
- 生成买入、卖出、持有、观察列表。

## 9. 回测规则

回测必须尽量贴近 A 股真实限制：

- 每周收盘后生成信号。
- 第一版假设下一个交易日开盘价成交。
- 处理 T+1 限制。
- 涨停无法买入。
- 跌停无法卖出。
- 停牌无法交易。
- 计入佣金。
- 卖出计入印花税。
- 计入滑点。
- 买卖数量按 100 股整数手处理。
- 财务数据只能在披露日之后使用，避免未来函数。

绩效指标：

- 总收益
- 年化收益
- 最大回撤
- 夏普比率
- 胜率
- 换手率
- 月度收益
- 与沪深 300、中证 500 对比

## 10. API 设计

第一版接口：

```text
GET  /api/health
GET  /api/overview
GET  /api/rebalance/latest
GET  /api/factors/scores
GET  /api/factors/scores/{stock_code}
GET  /api/backtest/summary
GET  /api/backtest/equity-curve
GET  /api/backtest/drawdown
GET  /api/config/strategy
GET  /api/data/status
POST /api/jobs/update-data
POST /api/jobs/run-weekly-strategy
GET  /api/exports/latest
```

## 11. 前端页面

### 总览页

展示组合净值、今年收益、最大回撤、当前持仓、本周买入和卖出数量、收益曲线、回撤曲线。

### 本周调仓页

展示买入、卖出、持有、观察列表，并显示建议仓位、因子解释、交易可用性提示。

### 因子评分页

展示股票总分、分组得分、行业排名、历史得分变化，并支持搜索股票。

### 回测分析页

展示收益曲线、回撤曲线、年化收益、夏普比率、胜率、换手率、月度收益热力图、基准对比。

### 策略配置页

展示股票池、调仓频率、持仓数量、因子权重、交易成本、滑点、风控限制。第一版可以先只读。

### 数据状态页

展示最新行情日期、最新财务数据日期、最近运行时间、数据完整性和任务日志。

## 12. 文档同步规则

每次有实质迭代时必须同步更新：

- `docs/TASK_PLAN.md`：任务状态
- `docs/CHANGELOG.md`：已完成变更
- `docs/TECHNICAL_ARCHITECTURE.md`：架构变化
- `docs/TEST_CASES.md`：行为或测试范围变化
- `docs/PROJECT_CONSTRAINTS.md`：边界、风格或约束变化
