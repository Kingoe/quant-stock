# Quant Stock

A personal A-share multi-factor stock selection assistant.

The first-stage goal is not automated trading. The system should help update data, filter the stock universe, calculate factor scores, run weekly backtests, generate rebalance suggestions, and present everything in a clear local web dashboard so trading decisions can still be reviewed manually.

## Project Documents

- [Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md)
- [Task Plan](docs/TASK_PLAN.md)
- [Test Cases](docs/TEST_CASES.md)
- [Project Constraints](docs/PROJECT_CONSTRAINTS.md)
- [Changelog](docs/CHANGELOG.md)

## MVP Scope

- CSI 800 stock universe
- Weekly rebalance
- Balanced multi-factor model
- 10-20 stock portfolio
- SQLite local database
- Python backend
- React visualization frontend
- Backtest and weekly rebalance report
- Excel or CSV export
- No automatic broker order placement

## Operating Principle

Every iteration must update the task plan and, when needed, the architecture, test cases, and constraints documents. These documents are the source of truth for project direction and progress.
