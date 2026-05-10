from __future__ import annotations

from datetime import date

from app.portfolio import generate_weekly_rebalance
from app.storage import open_sqlite_connection


def generate_weekly_html_report(
    database_url: str,
    index_code: str,
    score_date: str,
    *,
    limit: int = 15,
    single_stock_max_weight: float = 0.08,
    industry_max_weight: float = 0.3,
) -> str:
    """生成每周 HTML 报告。

    Args:
        database_url: 数据库 URL
        index_code: 指数代码
        score_date: 评分日期
        limit: 候选股数量上限
        single_stock_max_weight: 单票最大仓位
        industry_max_weight: 单个行业最大仓位

    Returns:
        HTML 报告内容
    """
    with open_sqlite_connection(database_url) as connection:
        recommendations = generate_weekly_rebalance(
            connection,
            index_code,
            score_date,
            limit=limit,
            single_stock_max_weight=single_stock_max_weight,
            industry_max_weight=industry_max_weight,
        )

    html = _build_html_report(score_date, recommendations)
    return html


def _build_html_report(score_date: str, recommendations: list) -> str:
    """构建 HTML 报告。

    Args:
        score_date: 评分日期
        recommendations: 调仓建议列表

    Returns:
        HTML 报告内容
    """
    buy_list = [r for r in recommendations if r.action == "buy"]
    sell_list = [r for r in recommendations if r.action == "sell"]
    hold_list = [r for r in recommendations if r.action == "hold"]
    watch_list = [r for r in recommendations if r.action == "watch"]

    html_parts = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"<title>量化选股周报 - {score_date}</title>",
        "<style>",
        "body { "
        'font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; '
        "margin: 0; padding: 40px; background: #f5f5f5; "
        "}",
        ".container { "
        "max-width: 1200px; margin: 0 auto; background: white; "
        "border-radius: 8px; padding: 40px; "
        "box-shadow: 0 2px 8px rgba(0,0,0,0.1); "
        "}",
        "h1 { "
        "color: #333; border-bottom: 2px solid #4a90e2; "
        "padding-bottom: 10px; margin-bottom: 30px; "
        "}",
        "h2 { color: #555; margin-top: 30px; margin-bottom: 15px; }",
        ".section { margin-bottom: 30px; }",
        "table { width: 100%; border-collapse: collapse; }",
        "th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; }",
        "th { background: #f9f9f9; font-weight: 600; color: #333; }",
        ".buy { color: #22c55e; }",
        ".sell { color: #ef4444; }",
        ".hold { color: #3b82f6; }",
        ".watch { color: #f59e0b; }",
        ".risk { color: #dc2626; font-size: 12px; }",
        "</style>",
        "</head>",
        "<body>",
        '<div class="container">',
        f"<h1>量化选股周报 - {score_date}</h1>",
    ]

    if buy_list:
        html_parts.extend(
            [
                '<div class="section">',
                f"<h2>买入列表 ({len(buy_list)})</h2>",
                "<table>",
                "<thead><tr><th>股票代码</th><th>股票名称</th><th>目标仓位</th><th>总分</th><th>排名</th><th>原因</th><th>风险提示</th></tr></thead>",
                "<tbody>",
            ]
        )
        for item in buy_list:
            risk_note = f'<span class="risk">⚠ {item.risk_note}</span>' if item.risk_note else "—"
            html_parts.append(
                "<tr><td>{}</td><td>{}</td><td>{:.2%}</td><td>{:.4f}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                    item.stock_code,
                    item.stock_name or "—",
                    item.target_weight or 0,
                    item.total_score,
                    item.rank or "—",
                    item.reason,
                    risk_note,
                )
            )
        html_parts.extend(["</tbody>", "</table>", "</div>"])

    if sell_list:
        html_parts.extend(
            [
                '<div class="section">',
                f"<h2>卖出列表 ({len(sell_list)})</h2>",
                "<table>",
                "<thead><tr><th>股票代码</th><th>股票名称</th><th>总分</th><th>原因</th><th>风险提示</th></tr></thead>",
                "<tbody>",
            ]
        )
        for item in sell_list:
            risk_note = f'<span class="risk">⚠ {item.risk_note}</span>' if item.risk_note else "—"
            html_parts.append(
                "<tr><td>{}</td><td>{}</td><td>{:.4f}</td><td>{}</td><td>{}</td></tr>".format(
                    item.stock_code,
                    item.stock_name or "—",
                    item.total_score,
                    item.reason,
                    risk_note,
                )
            )
        html_parts.extend(["</tbody>", "</table>", "</div>"])

    if hold_list:
        html_parts.extend(
            [
                '<div class="section">',
                f"<h2>持有列表 ({len(hold_list)})</h2>",
                "<table>",
                "<thead><tr><th>股票代码</th><th>股票名称</th><th>目标仓位</th><th>总分</th><th>排名</th></tr></thead>",
                "<tbody>",
            ]
        )
        for item in hold_list:
            html_parts.append(
                "<tr><td>{}</td><td>{}</td><td>{:.2%}</td><td>{:.4f}</td><td>{}</td></tr>".format(
                    item.stock_code,
                    item.stock_name or "—",
                    item.target_weight or 0,
                    item.total_score,
                    item.rank or "—",
                )
            )
        html_parts.extend(["</tbody>", "</table>", "</div>"])

    if watch_list:
        html_parts.extend(
            [
                '<div class="section">',
                f"<h2>观察列表 ({len(watch_list)})</h2>",
                "<table>",
                "<thead><tr><th>股票代码</th><th>股票名称</th><th>总分</th><th>排名</th><th>原因</th></tr></thead>",
                "<tbody>",
            ]
        )
        for item in watch_list:
            html_parts.append(
                "<tr><td>{}</td><td>{}</td><td>{:.4f}</td><td>{}</td><td>{}</td></tr>".format(
                    item.stock_code,
                    item.stock_name or "—",
                    item.total_score,
                    item.rank or "—",
                    item.reason,
                )
            )
        html_parts.extend(["</tbody>", "</table>", "</div>"])

    html_parts.extend(
        [
            '<div class="section">',
            '<p style="color: #666; font-size: 14px;">',
            f"报告生成时间: {date.today().isoformat()}<br>",
            "本报告由量化选股辅助系统自动生成，仅供投研参考。",
            "</p>",
            "</div>",
            "</div>",
            "</body>",
            "</html>",
        ]
    )

    return "\n".join(html_parts)
