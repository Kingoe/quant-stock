# Project Constraints

This document defines what the project should and should not do. Update it when project boundaries change.

## 1. Product Constraints

### Allowed

- Build an A-share multi-factor stock selection assistant.
- Generate weekly stock rankings.
- Generate buy, sell, hold, and watch lists.
- Run historical backtests.
- Run paper trading simulation.
- Show dashboard pages for analysis and review.
- Export reports for manual trading review.
- Add higher-quality data sources later.
- Add notification channels later.

### Not Allowed in MVP

- No automatic broker order placement.
- No direct live trading.
- No high-frequency trading.
- No intraday scalping strategy.
- No black-box machine learning model before the rule-based baseline is stable.
- No strategy optimization that only chases historical returns without out-of-sample validation.
- No use of future financial data before disclosure date.
- No trading recommendations without visible factor and risk explanation.

## 2. Investment and Risk Constraints

- The system is an assistant, not financial advice.
- Real trades must be manually reviewed.
- Backtest results must not be presented as guaranteed future performance.
- Risk warnings must be visible when data is stale, incomplete, or a trade is blocked.
- The system must model A-share constraints instead of assuming ideal execution.
- The first stable strategy should run in simulation for 1-3 months before real money is considered.

## 3. Strategy Constraints

MVP strategy:

- Base universe: CSI 800.
- Frequency: weekly rebalance.
- Style: balanced factor model.
- Holdings: 10-20 stocks.
- Factors: valuation, quality, growth, momentum, risk, liquidity.
- Portfolio controls: single-stock cap, industry cap, cash buffer.

Avoid in MVP:

- Minute-level signals.
- Leveraged exposure.
- Short selling.
- Futures, options, margin trading, or securities lending.
- Complex ensemble models.
- Overly large factor library.

## 4. Data Constraints

- Unit tests must not depend on live data.
- External data provider calls must be isolated behind interfaces.
- Store raw provider data separately when useful for debugging.
- Track latest data date and source.
- Financial data must use disclosure or effective date logic.
- Missing data should be explicit, not silently filled in a way that changes strategy meaning.

## 5. Engineering Constraints

- Keep modules small and focused.
- Prefer clear rule-based logic over clever abstractions.
- Every milestone needs tests.
- Every iteration updates documentation.
- Avoid unrelated refactors.
- Avoid adding services that are not needed for the MVP.
- SQLite is the default database until there is a real need to migrate.
- FastAPI is the default backend API framework.
- React + TypeScript is the default frontend stack.

## 6. Frontend Style

The UI should feel like a personal research workstation:

- Calm.
- Dense but readable.
- Professional.
- Fast to scan.
- Focused on data, risk, and decisions.

Do:

- Use tables, filters, sorting, compact metric cards, and charts.
- Use red and green carefully for financial changes.
- Show data freshness.
- Show warnings clearly.
- Keep navigation predictable.
- Make empty and error states useful.

Do not:

- Build a marketing landing page.
- Use decorative finance "big screen" effects.
- Hide important assumptions behind pretty charts.
- Use overly large hero sections.
- Use vague labels like "AI score" without explanation.
- Let charts or tables overflow on common laptop widths.

## 7. Documentation Constraints

Required documents:

- `README.md`
- `docs/TECHNICAL_ARCHITECTURE.md`
- `docs/TASK_PLAN.md`
- `docs/TEST_CASES.md`
- `docs/PROJECT_CONSTRAINTS.md`
- `docs/CHANGELOG.md`

Update rule:

- Architecture change: update `TECHNICAL_ARCHITECTURE.md`.
- Task progress: update `TASK_PLAN.md`.
- New or changed behavior: update `TEST_CASES.md`.
- Boundary or style change: update `PROJECT_CONSTRAINTS.md`.
- Completed user-visible or architectural change: update `CHANGELOG.md`.

## 8. Naming and Code Style

- Use descriptive names.
- Keep financial terms explicit.
- Prefer `rebalance_date`, `trade_date`, `score_date`, and `effective_date` over vague names like `date`.
- Prefer `stock_code` over `code` in public interfaces.
- Prefer `factor_score` and `total_score` over vague names like `score`.
- Keep API response fields stable and documented once the frontend depends on them.
