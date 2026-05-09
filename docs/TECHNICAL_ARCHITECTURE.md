# Technical Architecture

## 1. Product Positioning

Quant Stock is a personal A-share multi-factor stock selection assistant.

The system should support a disciplined workflow:

1. Update market, valuation, financial, and index constituent data.
2. Build a tradable stock universe.
3. Calculate factor scores.
4. Construct a weekly portfolio.
5. Run historical backtests.
6. Generate weekly rebalance suggestions.
7. Display results in a local web dashboard.
8. Let the user manually confirm real trades.

The first stage deliberately avoids automatic broker order placement.

## 2. Recommended Tech Stack

### Backend

- Language: Python
- API framework: FastAPI
- Data processing: pandas, numpy
- Database: SQLite for MVP
- Scheduling: APScheduler or system scheduler
- Export: CSV and Excel
- Testing: pytest

### Frontend

- Framework: React
- Language: TypeScript
- Build tool: Vite
- Charts: ECharts
- Tables: TanStack Table or a lightweight custom table
- Styling: Tailwind CSS or focused CSS modules

### Data Source

- MVP: akshare
- Future options: tushare, JoinQuant, RiceQuant, paid vendor data, broker data

## 3. Target Directory Structure

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
    app/
      main.py
      api/
      config/
      data/
      storage/
      universe/
      factors/
      scoring/
      portfolio/
      backtest/
      reports/
      risk/
      scheduler/
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

## 4. System Flow

```text
Data Provider
  -> SQLite Storage
  -> Universe Filter
  -> Factor Calculation
  -> Factor Scoring
  -> Portfolio Construction
  -> Backtest Engine
  -> Reports and API
  -> Frontend Dashboard
```

## 5. Core Data

The MVP should store or derive:

- Stock basic info: code, name, exchange, listing date, industry, status
- Index constituents: CSI 300, CSI 500, CSI 800
- Daily price data: open, high, low, close, volume, amount, adjusted close
- Valuation data: PE, PB, PS, dividend yield
- Financial data: ROE, gross margin, revenue growth, net profit growth, operating cash flow
- Trading status: suspension, limit up, limit down, ST status
- Trading calendar
- Strategy runs and generated rebalance suggestions
- Backtest positions, transactions, and performance metrics

## 6. Stock Universe Rules

MVP base universe: CSI 800.

Filters:

- Exclude ST and *ST stocks.
- Exclude stocks listed for less than one year.
- Exclude suspended stocks.
- Exclude low-liquidity stocks based on average trading amount.
- Exclude abnormal PE and PB values.
- Exclude companies with obvious financial distress when reliable data exists.
- Exclude stocks that cannot be traded on the rebalance execution day.

## 7. Factor Model

MVP model: balanced multi-factor scoring.

Factor groups:

- Valuation: PE, PB, dividend yield
- Quality: ROE, gross margin, operating cash flow to net profit
- Growth: revenue growth, net profit growth
- Momentum: 60-day return, 120-day return
- Risk: volatility, max drawdown
- Liquidity: 20-day average trading amount

Initial weights:

- Valuation: 25%
- Quality: 25%
- Growth: 20%
- Momentum: 20%
- Risk and liquidity: 10%

Scoring pipeline:

1. Align data by effective date.
2. Remove unusable rows.
3. Winsorize extreme values.
4. Standardize or percentile-rank each factor.
5. Reverse factors where lower is better.
6. Calculate weighted total score.
7. Apply risk and portfolio constraints.

## 8. Portfolio Rules

MVP portfolio:

- Weekly rebalance.
- Hold 10-20 stocks.
- Single-stock maximum weight: 5%-10%.
- Single-industry maximum weight: 25%-30%.
- Keep a small cash buffer.
- Skip stocks that cannot be bought.
- Keep or defer stocks that cannot be sold because of suspension or limit down.
- Generate buy, sell, hold, and watch lists.

## 9. Backtest Rules

The backtest must model A-share constraints:

- Weekly signal generation after market close.
- Execute on the next trading day open price in MVP.
- T+1 selling restriction.
- Limit up cannot be bought.
- Limit down cannot be sold.
- Suspended stocks cannot be traded.
- Commission.
- Stamp duty on sells.
- Slippage.
- 100-share board lot.
- Financial data must become usable only after disclosure date to avoid lookahead bias.

Metrics:

- Total return
- Annualized return
- Maximum drawdown
- Sharpe ratio
- Win rate
- Turnover
- Monthly returns
- Benchmark comparison with CSI 300 and CSI 500

## 10. API Design

Initial endpoints:

```text
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

## 11. Frontend Pages

### Dashboard

Shows portfolio net value, year-to-date return, maximum drawdown, current holdings, weekly buy and sell counts, equity curve, and drawdown curve.

### Weekly Rebalance

Shows buy, sell, hold, and watch lists, with recommended weights, factor score explanations, and trading availability warnings.

### Factor Scores

Shows stock-level total score, group scores, industry ranking, historical score trend, and searchable stock details.

### Backtest Analysis

Shows equity curve, drawdown, annualized return, Sharpe ratio, win rate, turnover, monthly return heatmap, and benchmark comparison.

### Strategy Config

Shows stock universe, rebalance frequency, holding count, factor weights, transaction costs, slippage, and risk limits.

### Data Status

Shows latest market date, latest financial data date, last run time, data completeness, and recent task logs.

## 12. Documentation Rule

Every meaningful iteration must update:

- `docs/TASK_PLAN.md` for task status.
- `docs/CHANGELOG.md` for completed changes.
- `docs/TECHNICAL_ARCHITECTURE.md` when architecture changes.
- `docs/TEST_CASES.md` when behavior or coverage changes.
- `docs/PROJECT_CONSTRAINTS.md` when project boundaries or style rules change.
