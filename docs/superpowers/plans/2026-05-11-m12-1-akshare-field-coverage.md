# M12-1 AkShare Field Coverage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete AkShareProvider coverage for trading calendar, index constituents, valuation, and financial metrics using mock-based tests only.

**Architecture:** Keep the public `DataProvider` interface unchanged and extend only the AkShare adapter internals. Add small column-normalization helpers in `backend/app/data/providers.py` so AkShare field drift is handled in one place, while all business logic continues to consume existing record dataclasses.

**Tech Stack:** Python 3.12, pandas-like AkShare DataFrames, pytest monkeypatch, ruff, existing backend data record dataclasses.

---

## File Structure

- Modify `backend/tests/test_data_providers.py`
  - Add failing tests for AkShare trading calendar, index constituents, valuation, financial metrics, and unsupported response schemas.
  - Tests must monkeypatch `sys.modules["akshare"]`; no network access.
- Modify `backend/app/data/providers.py`
  - Implement `AkShareProvider.get_trading_calendar`.
  - Implement `AkShareProvider.get_index_constituents`.
  - Implement `AkShareProvider.get_valuations`.
  - Implement `AkShareProvider.get_financial_metrics`.
  - Add helper functions for column lookup, date formatting, stock-code normalization, and optional numeric conversion.
- Modify `docs/DATA_SOURCE_PLAN.md`
  - Update current implementation status after M12-1 completes.
- Modify `docs/TASK_PLAN.md`
  - Mark M12-1 as `Done` after implementation and set earliest unfinished task to M12-2.
- Modify `docs/CURRENT_ITERATION.md`
  - Record M12-1 completion and next task.
- Modify `docs/CHANGELOG.md`
  - Add M12-1 change summary.
- Modify `docs/TEST_CASES.md`
  - Ensure AkShare mock-only field coverage is documented.

## Task 1: AkShare Trading Calendar

**Files:**
- Modify: `backend/tests/test_data_providers.py`
- Modify: `backend/app/data/providers.py`

- [ ] **Step 1: Write the failing test**

Append this test to `backend/tests/test_data_providers.py`:

```python
def test_akshare_provider_converts_trading_calendar(monkeypatch) -> None:
    """测试 AkShare 数据源转换交易日历。"""
    import pandas as pd

    from app.data.providers import AkShareProvider

    fake_akshare = SimpleNamespace(
        tool_trade_date_hist_sina=lambda: pd.DataFrame(
            [
                {"trade_date": "2026-05-08"},
                {"trade_date": "2026-05-11"},
                {"trade_date": "2026-05-12"},
            ]
        )
    )
    monkeypatch.setitem(sys.modules, "akshare", fake_akshare)

    records = AkShareProvider().get_trading_calendar("2026-05-09", "2026-05-12")

    assert [record.trade_date for record in records] == ["2026-05-11", "2026-05-12"]
    assert all(record.is_open for record in records)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
cd /Users/jinwu/work/hub/quant-stock/backend
uv run pytest tests/test_data_providers.py::test_akshare_provider_converts_trading_calendar -q
```

Expected result: FAIL with `NotImplementedError: AkShare trading calendar adapter is not implemented yet`.

- [ ] **Step 3: Implement minimal code**

In `backend/app/data/providers.py`, replace `AkShareProvider.get_trading_calendar` and add `_date_text` near helper functions:

```python
    def get_trading_calendar(self, start_date: str, end_date: str) -> list[TradingCalendarRecord]:
        akshare = _import_akshare()
        frame = akshare.tool_trade_date_hist_sina()
        records: list[TradingCalendarRecord] = []
        for _, row in frame.iterrows():
            trade_date = _date_text(_pick(row, ("trade_date", "交易日", "日期")))
            if start_date <= trade_date <= end_date:
                records.append(TradingCalendarRecord(trade_date=trade_date, is_open=True))
        return records
```

```python
def _date_text(value: object) -> str:
    text = str(value)
    if " " in text:
        text = text.split(" ", maxsplit=1)[0]
    return text.replace("/", "-")
```

Also add `_pick`:

```python
def _pick(row, names: tuple[str, ...]):
    for name in names:
        if name in row and row[name] is not None:
            return row[name]
    raise DataProviderError(f"missing required AkShare columns: {', '.join(names)}")
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_data_providers.py::test_akshare_provider_converts_trading_calendar -q
```

Expected result: PASS.

## Task 2: AkShare Index Constituents

**Files:**
- Modify: `backend/tests/test_data_providers.py`
- Modify: `backend/app/data/providers.py`

- [ ] **Step 1: Write the failing test**

Append:

```python
def test_akshare_provider_converts_index_constituents(monkeypatch) -> None:
    """测试 AkShare 数据源转换指数成分。"""
    import pandas as pd

    from app.data.providers import AkShareProvider

    calls = {}

    def index_stock_cons(symbol):
        calls["symbol"] = symbol
        return pd.DataFrame(
            [
                {"品种代码": "000001", "纳入日期": "2026-05-01", "权重": 0.5},
                {"品种代码": "600000", "纳入日期": "2026-05-01", "权重": 0.3},
            ]
        )

    fake_akshare = SimpleNamespace(index_stock_cons=index_stock_cons)
    monkeypatch.setitem(sys.modules, "akshare", fake_akshare)

    records = AkShareProvider().get_index_constituents("000906", "2026-05-11")

    assert calls["symbol"] == "000906"
    assert len(records) == 2
    assert records[0].index_code == "000906"
    assert records[0].stock_code == "000001"
    assert records[0].trade_date == "2026-05-11"
    assert records[0].weight == 0.5
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_data_providers.py::test_akshare_provider_converts_index_constituents -q
```

Expected result: FAIL with `NotImplementedError: AkShare index constituents adapter is not implemented yet`.

- [ ] **Step 3: Implement minimal code**

Replace `AkShareProvider.get_index_constituents`:

```python
    def get_index_constituents(
        self,
        index_code: str,
        trade_date: str,
    ) -> list[IndexConstituentRecord]:
        akshare = _import_akshare()
        frame = akshare.index_stock_cons(symbol=index_code)
        return [
            IndexConstituentRecord(
                index_code=index_code,
                stock_code=_stock_code_text(_pick(row, ("品种代码", "成分券代码", "stock_code", "代码"))),
                trade_date=trade_date,
                weight=_optional_float_value(_pick_optional(row, ("权重", "weight"))),
            )
            for _, row in frame.iterrows()
        ]
```

Add helpers:

```python
def _pick_optional(row, names: tuple[str, ...]):
    for name in names:
        if name in row and row[name] is not None:
            return row[name]
    return None
```

```python
def _stock_code_text(value: object) -> str:
    return str(value).zfill(6)
```

```python
def _optional_float_value(value: object | None) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "" or text.lower() == "nan":
        return None
    return float(text)
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_data_providers.py::test_akshare_provider_converts_index_constituents -q
```

Expected result: PASS.

## Task 3: AkShare Valuations

**Files:**
- Modify: `backend/tests/test_data_providers.py`
- Modify: `backend/app/data/providers.py`

- [ ] **Step 1: Write the failing test**

Append:

```python
def test_akshare_provider_converts_valuations(monkeypatch) -> None:
    """测试 AkShare 数据源转换估值数据。"""
    import pandas as pd

    from app.data.providers import AkShareProvider

    fake_akshare = SimpleNamespace(
        stock_a_indicator_lg=lambda symbol="all": pd.DataFrame(
            [
                {
                    "代码": "000001",
                    "日期": "2026-05-11",
                    "市盈率": 5.1,
                    "市净率": 0.8,
                    "市销率": 2.1,
                    "股息率": 3.2,
                },
                {
                    "代码": "600000",
                    "日期": "2026-05-10",
                    "市盈率": 6.2,
                    "市净率": 0.9,
                    "市销率": 2.3,
                    "股息率": 2.8,
                },
            ]
        )
    )
    monkeypatch.setitem(sys.modules, "akshare", fake_akshare)

    records = AkShareProvider().get_valuations("2026-05-11")

    assert len(records) == 1
    assert records[0].stock_code == "000001"
    assert records[0].trade_date == "2026-05-11"
    assert records[0].pe == 5.1
    assert records[0].pb == 0.8
    assert records[0].ps == 2.1
    assert records[0].dividend_yield == 3.2
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_data_providers.py::test_akshare_provider_converts_valuations -q
```

Expected result: FAIL with `NotImplementedError: AkShare valuation adapter is not implemented yet`.

- [ ] **Step 3: Implement minimal code**

Replace `AkShareProvider.get_valuations`:

```python
    def get_valuations(self, trade_date: str) -> list[ValuationRecord]:
        akshare = _import_akshare()
        frame = akshare.stock_a_indicator_lg(symbol="all")
        records: list[ValuationRecord] = []
        for _, row in frame.iterrows():
            row_date = _date_text(_pick(row, ("日期", "trade_date", "date")))
            if row_date != trade_date:
                continue
            records.append(
                ValuationRecord(
                    stock_code=_stock_code_text(_pick(row, ("代码", "stock_code"))),
                    trade_date=row_date,
                    pe=_optional_float_value(_pick_optional(row, ("市盈率", "pe", "PE"))),
                    pb=_optional_float_value(_pick_optional(row, ("市净率", "pb", "PB"))),
                    ps=_optional_float_value(_pick_optional(row, ("市销率", "ps", "PS"))),
                    dividend_yield=_optional_float_value(
                        _pick_optional(row, ("股息率", "dividend_yield"))
                    ),
                )
            )
        return records
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_data_providers.py::test_akshare_provider_converts_valuations -q
```

Expected result: PASS.

## Task 4: AkShare Financial Metrics

**Files:**
- Modify: `backend/tests/test_data_providers.py`
- Modify: `backend/app/data/providers.py`

- [ ] **Step 1: Write the failing test**

Append:

```python
def test_akshare_provider_converts_financial_metrics(monkeypatch) -> None:
    """测试 AkShare 数据源转换财务指标。"""
    import pandas as pd

    from app.data.providers import AkShareProvider

    calls = {}

    def stock_financial_abstract(symbol):
        calls["symbol"] = symbol
        return pd.DataFrame(
            [
                {
                    "报告期": "2026-03-31",
                    "公告日期": "2026-04-25",
                    "净资产收益率": 0.12,
                    "销售毛利率": 0.31,
                    "营业收入同比增长率": 0.18,
                    "净利润同比增长率": 0.16,
                    "经营活动产生的现金流量净额": 1200000,
                    "净利润": 900000,
                },
                {
                    "报告期": "2025-12-31",
                    "公告日期": "2026-03-20",
                    "净资产收益率": 0.10,
                    "销售毛利率": 0.29,
                    "营业收入同比增长率": 0.12,
                    "净利润同比增长率": 0.11,
                    "经营活动产生的现金流量净额": 1000000,
                    "净利润": 800000,
                },
            ]
        )

    fake_akshare = SimpleNamespace(stock_financial_abstract=stock_financial_abstract)
    monkeypatch.setitem(sys.modules, "akshare", fake_akshare)

    records = AkShareProvider().get_financial_metrics("000001", "2026-01-01", "2026-12-31")

    assert calls["symbol"] == "000001"
    assert len(records) == 1
    assert records[0].stock_code == "000001"
    assert records[0].report_date == "2026-03-31"
    assert records[0].disclosure_date == "2026-04-25"
    assert records[0].roe == 0.12
    assert records[0].gross_margin == 0.31
    assert records[0].revenue_growth == 0.18
    assert records[0].net_profit_growth == 0.16
    assert records[0].operating_cash_flow == 1200000
    assert records[0].net_profit == 900000
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
uv run pytest tests/test_data_providers.py::test_akshare_provider_converts_financial_metrics -q
```

Expected result: FAIL with `NotImplementedError: AkShare financial adapter is not implemented yet`.

- [ ] **Step 3: Implement minimal code**

Replace `AkShareProvider.get_financial_metrics`:

```python
    def get_financial_metrics(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
    ) -> list[FinancialRecord]:
        akshare = _import_akshare()
        frame = akshare.stock_financial_abstract(symbol=stock_code)
        records: list[FinancialRecord] = []
        for _, row in frame.iterrows():
            report_date = _date_text(_pick(row, ("报告期", "report_date")))
            if not (start_date <= report_date <= end_date):
                continue
            records.append(
                FinancialRecord(
                    stock_code=stock_code,
                    report_date=report_date,
                    disclosure_date=_date_text(_pick(row, ("公告日期", "disclosure_date"))),
                    roe=_optional_float_value(_pick_optional(row, ("净资产收益率", "roe", "ROE"))),
                    gross_margin=_optional_float_value(
                        _pick_optional(row, ("销售毛利率", "gross_margin"))
                    ),
                    revenue_growth=_optional_float_value(
                        _pick_optional(row, ("营业收入同比增长率", "revenue_growth"))
                    ),
                    net_profit_growth=_optional_float_value(
                        _pick_optional(row, ("净利润同比增长率", "net_profit_growth"))
                    ),
                    operating_cash_flow=_optional_float_value(
                        _pick_optional(row, ("经营活动产生的现金流量净额", "operating_cash_flow"))
                    ),
                    net_profit=_optional_float_value(_pick_optional(row, ("净利润", "net_profit"))),
                )
            )
        return records
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
uv run pytest tests/test_data_providers.py::test_akshare_provider_converts_financial_metrics -q
```

Expected result: PASS.

## Task 5: AkShare Schema Error

**Files:**
- Modify: `backend/tests/test_data_providers.py`
- Modify: `backend/app/data/providers.py`

- [ ] **Step 1: Write the failing test**

Append:

```python
def test_akshare_provider_reports_missing_required_columns(monkeypatch) -> None:
    """测试 AkShare 字段缺失时返回清晰错误。"""
    import pandas as pd

    from app.data.providers import AkShareProvider, DataProviderError

    fake_akshare = SimpleNamespace(
        stock_a_indicator_lg=lambda symbol="all": pd.DataFrame([{"未知字段": "000001"}])
    )
    monkeypatch.setitem(sys.modules, "akshare", fake_akshare)

    with pytest.raises(DataProviderError, match="missing required AkShare columns"):
        AkShareProvider().get_valuations("2026-05-11")
```

- [ ] **Step 2: Run test to verify it fails if helper error is unclear**

Run:

```bash
uv run pytest tests/test_data_providers.py::test_akshare_provider_reports_missing_required_columns -q
```

Expected result: PASS if `_pick` already raises `DataProviderError`; otherwise FAIL with a pandas/key error.

- [ ] **Step 3: Adjust implementation if needed**

Make sure `_pick` is exactly:

```python
def _pick(row, names: tuple[str, ...]):
    for name in names:
        if name in row and row[name] is not None:
            return row[name]
    raise DataProviderError(f"missing required AkShare columns: {', '.join(names)}")
```

- [ ] **Step 4: Run focused provider tests**

Run:

```bash
uv run pytest tests/test_data_providers.py -q
```

Expected result: all provider tests pass.

## Task 6: Documentation Sync

**Files:**
- Modify: `docs/DATA_SOURCE_PLAN.md`
- Modify: `docs/TASK_PLAN.md`
- Modify: `docs/CURRENT_ITERATION.md`
- Modify: `docs/CHANGELOG.md`
- Modify: `docs/TEST_CASES.md`

- [ ] **Step 1: Update `docs/DATA_SOURCE_PLAN.md`**

Change current implementation status to state:

```markdown
- `AkShareProvider` 已支持股票基础信息、日行情、交易日历、指数成分、估值和财务指标的基础映射。
- AkShare 单元测试使用 mock，不访问真实网络。
- AkShare 免费接口可能变化，字段缺失时会返回清晰错误，后续真实运行需要通过集成验证确认。
```

- [ ] **Step 2: Update `docs/TASK_PLAN.md`**

Change:

```markdown
当前应优先推进的最早未完成任务：M12-2 增加数据更新任务入口。
```

Change M12-1 row to:

```markdown
| M12-1 | 完善 AkShare 数据源字段覆盖 | Done | 已补齐交易日历、指数成分、估值和财务指标基础映射，单元测试使用 mock |
```

- [ ] **Step 3: Update `docs/CURRENT_ITERATION.md`**

Set:

```markdown
- 当前阶段：数据运营增强
- 当前任务：M12-1 完善 AkShare 数据源字段覆盖
- 任务来源：按 `docs/TASK_PLAN.md` 的最早未完成任务顺序推进
- 对任务顺序的影响：M12-1 已补齐，下一轮进入 M12-2
- 当前结果：已完成，AkShareProvider 补齐交易日历、指数成分、估值和财务指标基础映射
```

Set next recommendation:

```markdown
- M12-2 增加数据更新任务入口。
```

- [ ] **Step 4: Update `docs/CHANGELOG.md`**

Under `## 2026-05-11`, add:

```markdown
- 完成 M12-1 完善 AkShare 数据源字段覆盖。
- `AkShareProvider` 新增交易日历、指数成分、估值和财务指标基础映射。
- 新增 AkShare mock 测试，覆盖字段转换、日期过滤和字段缺失错误。
- 同步任务规划：M12-1 标记为 Done，下一轮进入 M12-2 增加数据更新任务入口。
```

- [ ] **Step 5: Update `docs/TEST_CASES.md`**

Ensure the data operations section contains:

```markdown
- AkShare 新增交易日历、指数成分、估值和财务指标映射必须使用 mock 覆盖。
- AkShare 字段缺失时必须返回清晰错误，不能暴露 pandas/key error。
```

## Task 7: Verification and Commit

**Files:**
- Verify all changed files.

- [ ] **Step 1: Run focused backend tests**

Run:

```bash
cd /Users/jinwu/work/hub/quant-stock/backend
uv run pytest tests/test_data_providers.py -q
```

Expected result: provider tests pass.

- [ ] **Step 2: Run full backend tests**

Run:

```bash
uv run pytest
```

Expected result: all backend tests pass.

- [ ] **Step 3: Run backend quality checks**

Run:

```bash
uv run ruff check app tests
uv run ruff format --check app tests
```

Expected result: both commands pass.

- [ ] **Step 4: Run repository diff check**

Run:

```bash
cd /Users/jinwu/work/hub/quant-stock
git diff --check
```

Expected result: no output.

- [ ] **Step 5: Commit**

Run:

```bash
git add backend/app/data/providers.py backend/tests/test_data_providers.py docs/DATA_SOURCE_PLAN.md docs/TASK_PLAN.md docs/CURRENT_ITERATION.md docs/CHANGELOG.md docs/TEST_CASES.md
git commit -m "feat: expand akshare provider coverage"
git push
```

Expected result: commit is created and pushed to `main`.

## Self-Review

- Spec coverage: M12-1 covers AkShare trading calendar, index constituents, valuation, financial metrics, mock-only tests, documentation sync, and verification.
- Placeholder scan: no placeholder tasks remain.
- Type consistency: all implementation snippets return existing `TradingCalendarRecord`, `IndexConstituentRecord`, `ValuationRecord`, and `FinancialRecord` dataclasses.
- Scope check: this plan only implements M12-1 and leaves data update tasks to M12-2.
