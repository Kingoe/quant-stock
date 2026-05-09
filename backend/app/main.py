from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Query
from pydantic import BaseModel

from app.data import (
    get_stock,
    get_universe_stock_codes,
)
from app.storage import open_sqlite_connection

app = FastAPI(title="Quant Stock Backend")


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int


class Meta(BaseModel):
    request_id: str
    generated_at: str
    pagination: PaginationMeta | None = None


class UniverseStockItem(BaseModel):
    stock_code: str
    stock_name: str
    list_date: str
    industry: str
    pe: float | None = None
    pb: float | None = None
    avg_amount: float | None = None
    is_suspended: bool = False


@app.get("/api/health")
def health_check() -> dict[str, dict[str, str]]:
    return {
        "data": {
            "status": "ok",
            "service": "quant-stock-backend",
        },
        "meta": {
            "request_id": "local-dev",
            "generated_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        },
    }


@app.get("/api/universe")
def get_universe(
    index_code: str = Query("000906", description="指数代码"),
    trade_date: str = Query(..., description="调仓日期"),
    database_url: str = Query(..., description="数据库 URL"),
    min_list_months: int = Query(12, description="最小上市月数"),
    min_avg_amount: float = Query(5000000, description="最小平均成交额"),
    max_pe: float = Query(1000, description="最大 PE"),
    max_pb: float = Query(100, description="最大 PB"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页大小"),
) -> dict[str, Any]:
    from app.data import (
        filter_stocks,
        filter_stocks_by_abnormal_valuation,
        filter_stocks_by_liquidity,
        filter_stocks_by_listing_date,
        filter_stocks_by_suspension,
        get_prices_by_trade_date,
        get_valuation_by_trade_date,
    )

    with open_sqlite_connection(database_url) as connection:
        # 获取基础股票池
        stock_codes = get_universe_stock_codes(connection, index_code, trade_date)

        if not stock_codes:
            return {
                "data": [],
                "meta": Meta(
                    request_id="local-dev",
                    generated_at=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
                    pagination=PaginationMeta(page=page, page_size=page_size, total=0),
                ).model_dump(),
            }

        # 应用过滤器
        stock_codes = filter_stocks(connection, stock_codes)
        stock_codes = filter_stocks_by_listing_date(connection, stock_codes, trade_date, min_list_months)
        stock_codes = filter_stocks_by_suspension(connection, stock_codes, trade_date)
        stock_codes = filter_stocks_by_liquidity(connection, stock_codes, trade_date, min_avg_amount)
        stock_codes = filter_stocks_by_abnormal_valuation(
            connection, stock_codes, trade_date, max_pe, max_pb
        )

        # 分页
        total = len(stock_codes)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paged_codes = stock_codes[start_idx:end_idx]

        # 获取股票详情
        price_rows = {row["stock_code"]: row for row in get_prices_by_trade_date(connection, trade_date)}
        valuation_rows = {row["stock_code"]: row for row in get_valuation_by_trade_date(connection, trade_date)}

        items = []
        for stock_code in paged_codes:
            stock = get_stock(connection, stock_code)
            if stock:
                price_row = price_rows.get(stock_code)
                valuation_row = valuation_rows.get(stock_code)
                items.append(
                    UniverseStockItem(
                        stock_code=stock["stock_code"],
                        stock_name=stock["stock_name"],
                        list_date=stock["list_date"],
                        industry=stock["industry"] if stock["industry"] else "",
                        pe=valuation_row["pe"] if valuation_row and valuation_row["pe"] is not None else None,
                        pb=valuation_row["pb"] if valuation_row and valuation_row["pb"] is not None else None,
                        avg_amount=price_row["amount"] if price_row and price_row["amount"] is not None else None,
                        is_suspended=bool(price_row["is_suspended"]) if price_row else False,
                    )
                )

        return {
            "data": items,
            "meta": Meta(
                request_id="local-dev",
                generated_at=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
                pagination=PaginationMeta(page=page, page_size=page_size, total=total),
            ).model_dump(),
        }

