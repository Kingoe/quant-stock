from __future__ import annotations

from io import BytesIO

import xlsxwriter

from app.portfolio import RebalanceRecommendation


def generate_rebalance_excel(recommendations: list[RebalanceRecommendation]) -> BytesIO:
    """生成调仓建议 Excel 文件。

    Args:
        recommendations: 调仓建议列表

    Returns:
        Excel 文件的 BytesIO
    """
    output = BytesIO()

    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    worksheet = workbook.add_worksheet("调仓建议")

    headers = [
        ("股票代码", 10),
        ("股票名称", 12),
        ("操作", 8),
        ("目标仓位", 12),
        ("总分", 10),
        ("排名", 8),
        ("原因", 20),
        ("风险提示", 20),
    ]

    header_format = workbook.add_format(
        {
            "bold": True,
            "bg_color": "#4a90e2",
            "font_color": "white",
            "border": 1,
        }
    )

    buy_format = workbook.add_format({"font_color": "#22c55e", "border": 1})
    sell_format = workbook.add_format({"font_color": "#ef4444", "border": 1})
    hold_format = workbook.add_format({"font_color": "#3b82f6", "border": 1})
    watch_format = workbook.add_format({"font_color": "#f59e0b", "border": 1})

    for col, (header, width) in enumerate(headers):
        worksheet.write(0, col, header, header_format)
        worksheet.set_column(col, col, width)

    for row, item in enumerate(recommendations, start=1):
        if item.action == "buy":
            cell_format = buy_format
        elif item.action == "sell":
            cell_format = sell_format
        elif item.action == "hold":
            cell_format = hold_format
        else:
            cell_format = watch_format

        worksheet.write(row, 0, item.stock_code, cell_format)
        worksheet.write(row, 1, item.stock_name or "—", cell_format)
        worksheet.write(row, 2, item.action, cell_format)
        worksheet.write(
            row, 3, f"{item.target_weight:.2%}" if item.target_weight else "—", cell_format
        )
        worksheet.write(row, 4, f"{item.total_score:.4f}", cell_format)
        worksheet.write(row, 5, item.rank or "—", cell_format)
        worksheet.write(row, 6, item.reason, cell_format)
        worksheet.write(row, 7, item.risk_note or "—", cell_format)

    workbook.close()
    output.seek(0)
    return output


def generate_rebalance_csv(recommendations: list[RebalanceRecommendation]) -> str:
    """生成调仓建议 CSV 文件。

    Args:
        recommendations: 调仓建议列表

    Returns:
        CSV 内容字符串
    """
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(
        ["股票代码", "股票名称", "操作", "目标仓位", "总分", "排名", "原因", "风险提示"]
    )

    for item in recommendations:
        writer.writerow(
            [
                item.stock_code,
                item.stock_name or "—",
                item.action,
                f"{item.target_weight:.2%}" if item.target_weight else "—",
                f"{item.total_score:.4f}",
                item.rank or "—",
                item.reason,
                item.risk_note or "—",
            ]
        )

    return output.getvalue()
