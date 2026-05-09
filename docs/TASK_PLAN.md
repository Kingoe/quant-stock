# Task Plan

This document tracks project progress. Update it during every iteration.

Status values:

- Not Started
- In Progress
- Blocked
- Done

## Current Milestone

Milestone 0: Project foundation and documentation.

## Milestone 0: Project Foundation

| ID | Task | Status | Notes |
| --- | --- | --- | --- |
| M0-1 | Create project directory | Done | Project root: `/Users/jinwu/work/hub/quant-stock` |
| M0-2 | Create architecture document | Done | See `docs/TECHNICAL_ARCHITECTURE.md` |
| M0-3 | Create task plan | Done | This document |
| M0-4 | Create test case document | Done | See `docs/TEST_CASES.md` |
| M0-5 | Create project constraints document | Done | See `docs/PROJECT_CONSTRAINTS.md` |
| M0-6 | Create changelog | Done | See `docs/CHANGELOG.md` |
| M0-7 | Initialize Git repository | Done | Initialized Git repository in project root |

## Milestone 1: Backend Foundation

| ID | Task | Status | Notes |
| --- | --- | --- | --- |
| M1-1 | Create Python project structure | Not Started | `backend/app`, `backend/tests` |
| M1-2 | Add backend dependency configuration | Not Started | FastAPI, pandas, numpy, pytest |
| M1-3 | Add app configuration loader | Not Started | Strategy config and runtime settings |
| M1-4 | Add SQLite connection layer | Not Started | Simple repository pattern |
| M1-5 | Add health check API | Not Started | Confirms backend runs |

## Milestone 2: Data Foundation

| ID | Task | Status | Notes |
| --- | --- | --- | --- |
| M2-1 | Define database schema | Not Started | Stocks, prices, fundamentals, index constituents, strategy runs |
| M2-2 | Implement trading calendar loader | Not Started | Required by weekly rebalance and backtest |
| M2-3 | Implement stock basic info loader | Not Started | Include listing date, status, industry |
| M2-4 | Implement CSI 800 constituent loader | Not Started | Base universe for MVP |
| M2-5 | Implement daily price loader | Not Started | Open, high, low, close, volume, amount |
| M2-6 | Implement valuation data loader | Not Started | PE, PB, PS, dividend yield |
| M2-7 | Implement financial data loader | Not Started | ROE, margins, growth, cash flow |
| M2-8 | Implement data status checks | Not Started | Latest dates and completeness |

## Milestone 3: Stock Universe

| ID | Task | Status | Notes |
| --- | --- | --- | --- |
| M3-1 | Implement CSI 800 base universe query | Not Started | Rebalance date aware |
| M3-2 | Implement ST filter | Not Started | Exclude ST and *ST |
| M3-3 | Implement listing age filter | Not Started | Exclude listed less than one year |
| M3-4 | Implement suspension filter | Not Started | Exclude unavailable stocks |
| M3-5 | Implement liquidity filter | Not Started | Based on 20-day average amount |
| M3-6 | Implement valuation abnormal filter | Not Started | Remove invalid PE/PB rows |
| M3-7 | Add universe API and tests | Not Started | Debuggable filtered universe |

## Milestone 4: Factor Calculation

| ID | Task | Status | Notes |
| --- | --- | --- | --- |
| M4-1 | Implement factor input alignment | Not Started | Use only data effective on scoring date |
| M4-2 | Implement valuation factors | Not Started | PE, PB, dividend yield |
| M4-3 | Implement quality factors | Not Started | ROE, gross margin, cash flow quality |
| M4-4 | Implement growth factors | Not Started | Revenue and profit growth |
| M4-5 | Implement momentum factors | Not Started | 60-day and 120-day return |
| M4-6 | Implement risk factors | Not Started | Volatility and max drawdown |
| M4-7 | Implement liquidity factor | Not Started | 20-day average amount |
| M4-8 | Implement winsorization and ranking | Not Started | Avoid extreme factor distortion |
| M4-9 | Implement weighted total score | Not Started | Initial balanced weights |

## Milestone 5: Portfolio Construction

| ID | Task | Status | Notes |
| --- | --- | --- | --- |
| M5-1 | Select top-ranked candidates | Not Started | Target 10-20 holdings |
| M5-2 | Apply single-stock weight cap | Not Started | 5%-10% |
| M5-3 | Apply industry weight cap | Not Started | 25%-30% |
| M5-4 | Generate buy, sell, hold, watch lists | Not Started | Weekly rebalance output |
| M5-5 | Add trading availability warnings | Not Started | Limit up, limit down, suspension |
| M5-6 | Add rebalance API and tests | Not Started | Frontend data source |

## Milestone 6: Backtest Engine

| ID | Task | Status | Notes |
| --- | --- | --- | --- |
| M6-1 | Implement weekly rebalance scheduler | Not Started | Signal after close, execute next trading day |
| M6-2 | Implement order generation | Not Started | Board lot and target weights |
| M6-3 | Implement transaction costs | Not Started | Commission, stamp duty, slippage |
| M6-4 | Implement A-share trade constraints | Not Started | T+1, limit up/down, suspension |
| M6-5 | Implement position and cash accounting | Not Started | Portfolio ledger |
| M6-6 | Implement performance metrics | Not Started | Return, drawdown, Sharpe, turnover |
| M6-7 | Implement benchmark comparison | Not Started | CSI 300 and CSI 500 |
| M6-8 | Add backtest API and tests | Not Started | Summary and chart data |

## Milestone 7: Frontend Dashboard

| ID | Task | Status | Notes |
| --- | --- | --- | --- |
| M7-1 | Create React project | Not Started | Vite + TypeScript |
| M7-2 | Create app shell and navigation | Not Started | Professional research-workbench layout |
| M7-3 | Implement Dashboard page | Not Started | Overview metrics and charts |
| M7-4 | Implement Weekly Rebalance page | Not Started | Buy, sell, hold, watch tables |
| M7-5 | Implement Factor Scores page | Not Started | Searchable score table |
| M7-6 | Implement Backtest Analysis page | Not Started | Equity, drawdown, metrics |
| M7-7 | Implement Strategy Config page | Not Started | Read-only in MVP |
| M7-8 | Implement Data Status page | Not Started | Data freshness and task logs |
| M7-9 | Add frontend tests | Not Started | Component and API-state tests |

## Milestone 8: Reports and Automation

| ID | Task | Status | Notes |
| --- | --- | --- | --- |
| M8-1 | Generate weekly HTML report | Not Started | Human-readable weekly summary |
| M8-2 | Generate Excel or CSV export | Not Started | Rebalance and factor details |
| M8-3 | Add one-click weekly strategy run | Not Started | Trigger backend job manually |
| M8-4 | Add scheduled data update | Not Started | Local scheduled run |
| M8-5 | Add run logs | Not Started | Debug and audit trail |

## Milestone 9: Simulation

| ID | Task | Status | Notes |
| --- | --- | --- | --- |
| M9-1 | Add paper trading ledger | Not Started | No real orders |
| M9-2 | Track suggested trades | Not Started | Compare signal vs simulated outcome |
| M9-3 | Track simulated net value | Not Started | 1-3 month observation |
| M9-4 | Add simulation dashboard section | Not Started | Show divergence and results |

## Milestone 10: Future Enhancements

| ID | Task | Status | Notes |
| --- | --- | --- | --- |
| M10-1 | Add higher-quality data source option | Not Started | Replace or supplement akshare |
| M10-2 | Add factor effectiveness analysis | Not Started | IC, rank IC, quantile returns |
| M10-3 | Add industry neutralization | Not Started | Reduce unintended industry exposure |
| M10-4 | Add parameter experiment tracking | Not Started | Avoid ad hoc optimization |
| M10-5 | Add notification channel | Not Started | Email, Feishu, or enterprise WeChat |
| M10-6 | Evaluate broker interface | Not Started | Only after stable simulation |

## Iteration Update Rule

At the end of each iteration:

1. Mark completed tasks as Done.
2. Mark active task as In Progress or Blocked.
3. Add new discovered tasks with IDs.
4. Update `docs/CHANGELOG.md`.
5. Update architecture, tests, or constraints when behavior changes.
