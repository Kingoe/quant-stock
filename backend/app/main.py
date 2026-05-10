from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from app.data import (
    get_stock,
    get_universe_stock_codes,
)
from app.portfolio import generate_weekly_rebalance
from app.reports import (
    generate_rebalance_csv,
    generate_rebalance_excel,
    generate_weekly_html_report,
)
from app.run_log import RunStatus, create_run_log, update_run_log_status
from app.scheduler import scheduler
from app.simulation import PortfolioSnapshot, analyze_performance, get_execution_summary
from app.storage import initialize_schema, open_sqlite_connection

app = FastAPI(title="Quant Stock Backend")


@app.on_event("startup")
def startup_event() -> None:
    """应用启动时初始化调度器。"""
    scheduler.start()


@app.on_event("shutdown")
def shutdown_event() -> None:
    """应用关闭时停止调度器。"""
    scheduler.shutdown()


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


class RebalanceRecommendationItem(BaseModel):
    stock_code: str
    stock_name: str | None
    action: str
    target_weight: float | None
    total_score: float
    rank: int | None
    reason: str
    risk_note: str | None


class RunWeeklyStrategyResult(BaseModel):
    log_id: int | None
    status: str
    recommendations_count: int
    action_counts: dict[str, int]
    error_message: str | None = None


class SimulationAccountSummary(BaseModel):
    latest_value: float
    cash: float
    total_return: float


class SimulationPerformanceSummary(BaseModel):
    max_drawdown: float
    daily_volatility: float


class SimulationSummary(BaseModel):
    latest_date: str | None
    account: SimulationAccountSummary
    performance: SimulationPerformanceSummary
    execution: dict[str, Any]


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
        stock_codes = filter_stocks_by_listing_date(
            connection, stock_codes, trade_date, min_list_months
        )
        stock_codes = filter_stocks_by_suspension(connection, stock_codes, trade_date)
        stock_codes = filter_stocks_by_liquidity(
            connection, stock_codes, trade_date, min_avg_amount
        )
        stock_codes = filter_stocks_by_abnormal_valuation(
            connection, stock_codes, trade_date, max_pe, max_pb
        )

        # 分页
        total = len(stock_codes)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paged_codes = stock_codes[start_idx:end_idx]

        # 获取股票详情
        price_rows = {
            row["stock_code"]: row for row in get_prices_by_trade_date(connection, trade_date)
        }
        valuation_rows = {
            row["stock_code"]: row for row in get_valuation_by_trade_date(connection, trade_date)
        }

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
                        pe=valuation_row["pe"]
                        if valuation_row and valuation_row["pe"] is not None
                        else None,
                        pb=valuation_row["pb"]
                        if valuation_row and valuation_row["pb"] is not None
                        else None,
                        avg_amount=price_row["amount"]
                        if price_row and price_row["amount"] is not None
                        else None,
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


@app.get("/api/rebalance/latest")
def get_latest_rebalance(
    index_code: str = Query("000906", description="指数代码"),
    score_date: str = Query(..., description="评分日期"),
    database_url: str = Query(..., description="数据库 URL"),
    limit: int = Query(15, ge=1, le=50, description="候选股数量"),
    single_stock_max_weight: float = Query(0.08, gt=0, le=1, description="单票最大仓位"),
    industry_max_weight: float = Query(0.3, gt=0, le=1, description="行业最大仓位"),
) -> dict[str, Any]:
    """获取最新调仓建议。"""
    with open_sqlite_connection(database_url) as connection:
        recommendations = generate_weekly_rebalance(
            connection,
            index_code,
            score_date,
            limit=limit,
            single_stock_max_weight=single_stock_max_weight,
            industry_max_weight=industry_max_weight,
            current_positions=None,
        )

        items = [
            RebalanceRecommendationItem(
                stock_code=r.stock_code,
                stock_name=r.stock_name,
                action=r.action,
                target_weight=r.target_weight,
                total_score=r.total_score,
                rank=r.rank,
                reason=r.reason,
                risk_note=r.risk_note,
            )
            for r in recommendations
        ]

        return {
            "data": items,
            "meta": Meta(
                request_id="local-dev",
                generated_at=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
            ).model_dump(),
        }


@app.get("/api/rebalance/html")
def get_rebalance_html(
    index_code: str = Query("000906", description="指数代码"),
    score_date: str = Query(..., description="评分日期"),
    database_url: str = Query(..., description="数据库 URL"),
    limit: int = Query(15, ge=1, le=50, description="候选股数量"),
    single_stock_max_weight: float = Query(0.08, gt=0, le=1, description="单票最大仓位"),
    industry_max_weight: float = Query(0.3, gt=0, le=1, description="行业最大仓位"),
):
    """生成 HTML 周报。"""
    html = generate_weekly_html_report(
        database_url,
        index_code,
        score_date,
        limit=limit,
        single_stock_max_weight=single_stock_max_weight,
        industry_max_weight=industry_max_weight,
    )
    from fastapi.responses import HTMLResponse

    return HTMLResponse(content=html)


@app.get("/api/rebalance/excel")
def get_rebalance_excel(
    index_code: str = Query("000906", description="指数代码"),
    score_date: str = Query(..., description="评分日期"),
    database_url: str = Query(..., description="数据库 URL"),
    limit: int = Query(15, ge=1, le=50, description="候选股数量"),
    single_stock_max_weight: float = Query(0.08, gt=0, le=1, description="单票最大仓位"),
    industry_max_weight: float = Query(0.3, gt=0, le=1, description="行业最大仓位"),
):
    """生成 Excel 调仓报告。"""
    with open_sqlite_connection(database_url) as connection:
        recommendations = generate_weekly_rebalance(
            connection,
            index_code,
            score_date,
            limit=limit,
            single_stock_max_weight=single_stock_max_weight,
            industry_max_weight=industry_max_weight,
            current_positions=None,
        )

    excel_file = generate_rebalance_excel(recommendations)

    from fastapi.responses import Response

    return Response(
        content=excel_file.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=rebalance_{score_date}.xlsx",
        },
    )


@app.get("/api/rebalance/csv")
def get_rebalance_csv(
    index_code: str = Query("000906", description="指数代码"),
    score_date: str = Query(..., description="评分日期"),
    database_url: str = Query(..., description="数据库 URL"),
    limit: int = Query(15, ge=1, le=50, description="候选股数量"),
    single_stock_max_weight: float = Query(0.08, gt=0, le=1, description="单票最大仓位"),
    industry_max_weight: float = Query(0.3, gt=0, le=1, description="行业最大仓位"),
):
    """生成 CSV 调仓报告。"""
    with open_sqlite_connection(database_url) as connection:
        recommendations = generate_weekly_rebalance(
            connection,
            index_code,
            score_date,
            limit=limit,
            single_stock_max_weight=single_stock_max_weight,
            industry_max_weight=industry_max_weight,
            current_positions=None,
        )

    csv_content = generate_rebalance_csv(recommendations)

    from fastapi.responses import Response

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=rebalance_{score_date}.csv",
        },
    )


@app.post("/api/jobs/run-weekly-strategy")
def run_weekly_strategy(
    index_code: str = Query("000906", description="指数代码"),
    score_date: str = Query(..., description="评分日期"),
    database_url: str = Query(..., description="数据库 URL"),
    limit: int = Query(15, ge=1, le=50, description="候选股数量"),
    single_stock_max_weight: float = Query(0.08, gt=0, le=1, description="单票最大仓位"),
    industry_max_weight: float = Query(0.3, gt=0, le=1, description="行业最大仓位"),
) -> dict[str, Any]:
    """手动运行本周策略。"""
    error_message: str | None = None
    data: RunWeeklyStrategyResult | None = None

    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        log = create_run_log(connection, "weekly_strategy")
        if log.id is None:
            raise HTTPException(status_code=500, detail="failed to create run log")

        update_run_log_status(connection, log.id, RunStatus.RUNNING)

        try:
            recommendations = generate_weekly_rebalance(
                connection,
                index_code,
                score_date,
                limit=limit,
                single_stock_max_weight=single_stock_max_weight,
                industry_max_weight=industry_max_weight,
                current_positions=None,
            )
        except Exception as exc:
            error_message = str(exc)
            update_run_log_status(
                connection,
                log.id,
                RunStatus.FAILED,
                error_message=error_message,
            )
        else:
            action_counts = {"buy": 0, "hold": 0, "sell": 0, "watch": 0}
            for item in recommendations:
                if item.action in action_counts:
                    action_counts[item.action] += 1

            result = {
                "recommendations_count": len(recommendations),
                "action_counts": action_counts,
            }
            update_run_log_status(connection, log.id, RunStatus.SUCCESS, result=result)
            data = RunWeeklyStrategyResult(
                log_id=log.id,
                status="success",
                recommendations_count=len(recommendations),
                action_counts=action_counts,
            )

    if error_message is not None:
        raise HTTPException(status_code=500, detail=error_message)

    return {
        "data": data.model_dump() if data else None,
        "meta": Meta(
            request_id="local-dev",
            generated_at=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        ).model_dump(),
    }


@app.get("/api/simulation/summary")
def get_simulation_summary(
    database_url: str = Query(..., description="数据库 URL"),
    run_date: str | None = Query(None, description="运行日期"),
) -> dict[str, Any]:
    """获取模拟运行摘要。"""
    with open_sqlite_connection(database_url) as connection:
        initialize_schema(connection)
        rows = connection.execute(
            """
            select snapshot_id, run_date, cash, total_value, created_at
            from portfolio_snapshots
            order by run_date
            """
        ).fetchall()

        snapshots = [
            PortfolioSnapshot(
                id=row["snapshot_id"],
                account_id="simulation",
                snapshot_date=row["run_date"],
                cash=row["cash"],
                total_value=row["total_value"],
                positions_value=max(row["total_value"] - row["cash"], 0),
                created_at=row["created_at"],
            )
            for row in rows
        ]

        execution = get_execution_summary(connection, run_date=run_date)

    if snapshots:
        performance = analyze_performance(snapshots)
        latest = snapshots[-1]
        data = SimulationSummary(
            latest_date=latest.snapshot_date,
            account=SimulationAccountSummary(
                latest_value=float(latest.total_value),
                cash=float(latest.cash),
                total_return=round(float(performance["total_return"]), 4),
            ),
            performance=SimulationPerformanceSummary(
                max_drawdown=round(float(performance["max_drawdown"]), 4),
                daily_volatility=round(float(performance["daily_volatility"]), 4),
            ),
            execution=execution,
        )
    else:
        data = SimulationSummary(
            latest_date=None,
            account=SimulationAccountSummary(
                latest_value=0,
                cash=0,
                total_return=0,
            ),
            performance=SimulationPerformanceSummary(
                max_drawdown=0,
                daily_volatility=0,
            ),
            execution=execution,
        )

    return {
        "data": data.model_dump(),
        "meta": Meta(
            request_id="local-dev",
            generated_at=datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        ).model_dump(),
    }
