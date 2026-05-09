# Test Cases

This document defines the expected test coverage. Update it whenever functionality changes.

## 1. Testing Principles

- Prefer deterministic tests with fixed fixture data.
- Do not depend on live market data in unit tests.
- Mock external data providers.
- Test A-share trading rules explicitly.
- Test data effective dates to prevent lookahead bias.
- Keep strategy tests explainable; avoid opaque expected values.

## 2. Backend Unit Tests

### Configuration

- Loads default strategy configuration.
- Rejects invalid holding count.
- Rejects factor weights that do not sum to 1.
- Rejects negative transaction cost values.

### Storage

- Creates required SQLite tables.
- Inserts and updates stock basic info.
- Inserts daily price rows without duplicates.
- Queries prices by stock and date range.
- Queries latest available data date.

### Data Provider

- Converts raw provider fields into internal schema.
- Handles missing optional fields.
- Fails clearly when required fields are missing.
- Does not write partial data when a batch fails validation.

## 3. Universe Tests

- Excludes ST and *ST stocks.
- Excludes stocks listed for less than one year as of scoring date.
- Excludes suspended stocks on the rebalance date.
- Excludes stocks below the liquidity threshold.
- Excludes invalid PE or PB values.
- Keeps valid CSI 800 members that pass all filters.
- Produces a reason list for excluded stocks when debug mode is enabled.

## 4. Factor Tests

### Valuation

- Lower PE receives a better valuation rank when PE is positive and valid.
- Lower PB receives a better valuation rank when PB is positive and valid.
- Higher dividend yield receives a better valuation rank.
- Invalid or negative PE values are excluded or marked unusable according to configuration.

### Quality

- Higher ROE receives a better quality score.
- Higher gross margin receives a better quality score.
- Higher operating cash flow to net profit receives a better quality score.

### Growth

- Higher revenue growth receives a better growth score.
- Higher net profit growth receives a better growth score.
- Missing growth data reduces usability without crashing scoring.

### Momentum

- 60-day and 120-day returns are calculated from adjusted prices.
- Stocks without enough price history do not receive misleading momentum scores.

### Risk and Liquidity

- Lower volatility receives a better risk score.
- Lower max drawdown receives a better risk score.
- Higher 20-day average trading amount passes liquidity scoring.

### Scoring Pipeline

- Winsorization caps extreme values.
- Percentile ranking returns scores in a stable range.
- Reverse-scored factors are handled correctly.
- Weighted total score matches the configured weights.

## 5. Portfolio Tests

- Selects the top N stocks after filters.
- Applies single-stock maximum weight.
- Applies industry maximum weight.
- Generates buy list for new target holdings.
- Generates sell list for current holdings missing from target holdings.
- Generates hold list for overlapping current and target holdings.
- Generates watch list for high-scoring stocks outside the final portfolio.
- Skips buy orders for limit-up or suspended stocks.
- Flags sell orders blocked by limit-down or suspension.

## 6. Backtest Tests

- Generates weekly rebalance dates from the trading calendar.
- Uses next trading day open price for execution in MVP.
- Applies commission on buy and sell.
- Applies stamp duty only on sells.
- Applies slippage to execution prices.
- Rounds orders to 100-share board lots.
- Prevents same-day buy then sell behavior that violates T+1.
- Blocks buys on limit-up days.
- Blocks sells on limit-down days.
- Keeps suspended holdings unchanged.
- Updates cash and positions after each transaction.
- Calculates net asset value correctly.
- Calculates total return, annualized return, max drawdown, Sharpe ratio, win rate, and turnover.
- Compares performance against CSI 300 and CSI 500 benchmark series.

## 7. API Tests

- `GET /api/overview` returns overview metrics.
- `GET /api/rebalance/latest` returns buy, sell, hold, and watch lists.
- `GET /api/factors/scores` supports pagination and sorting.
- `GET /api/factors/scores/{stock_code}` returns stock details or 404.
- `GET /api/backtest/summary` returns core metrics.
- `GET /api/backtest/equity-curve` returns ordered time series.
- `GET /api/backtest/drawdown` returns ordered drawdown series.
- `GET /api/config/strategy` returns current strategy configuration.
- `GET /api/data/status` returns latest data dates and task status.

## 8. Frontend Tests

- App shell renders navigation.
- Dashboard shows overview metrics and chart placeholders.
- Weekly Rebalance page renders buy, sell, hold, and watch lists.
- Factor Scores page supports search, sorting, and empty state.
- Backtest Analysis page renders metric cards and charts.
- Strategy Config page renders current configuration.
- Data Status page highlights stale or incomplete data.
- API loading, empty, and error states are visible and clear.

## 9. Integration Tests

- Runs a full fixture-based weekly strategy pipeline.
- Produces deterministic factor scores.
- Produces deterministic rebalance suggestions.
- Produces deterministic backtest metrics.
- Frontend can load mock API data for all pages.

## 10. Manual Verification

Before calling a milestone complete:

1. Run backend unit tests.
2. Run frontend tests.
3. Start backend locally.
4. Start frontend locally.
5. Open the dashboard.
6. Verify every page has data or a clear empty state.
7. Export the latest rebalance report.
8. Confirm task plan and changelog are updated.
