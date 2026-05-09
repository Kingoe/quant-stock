# API 约定

本文档定义后端 API 的响应格式、字段命名和错误处理规则。前端依赖 API 后，这些约定应保持稳定。

## 1. 基本原则

- API 路径使用英文小写和连字符。
- JSON 字段使用 snake_case。
- 日期使用 ISO 格式：`YYYY-MM-DD`。
- 日期时间使用 ISO 格式：`YYYY-MM-DDTHH:mm:ss+08:00`。
- 股票代码字段统一使用 `stock_code`。
- 金额字段单位必须在字段名或接口文档中说明。
- 比例字段使用小数，例如 `0.12` 表示 12%。

## 2. 成功响应

普通成功响应：

```json
{
  "data": {
    "status": "ok"
  },
  "meta": {
    "request_id": "local-dev",
    "generated_at": "2026-05-09T10:30:00+08:00"
  }
}
```

列表响应：

```json
{
  "data": [
    {
      "stock_code": "600000",
      "stock_name": "浦发银行"
    }
  ],
  "meta": {
    "request_id": "local-dev",
    "generated_at": "2026-05-09T10:30:00+08:00",
    "pagination": {
      "page": 1,
      "page_size": 50,
      "total": 1
    }
  }
}
```

## 3. 错误响应

错误响应：

```json
{
  "error": {
    "code": "data_not_ready",
    "message": "行情数据尚未更新，无法生成本周调仓建议。",
    "details": {
      "required_date": "2026-05-08",
      "latest_date": "2026-05-07"
    }
  },
  "meta": {
    "request_id": "local-dev",
    "generated_at": "2026-05-09T10:30:00+08:00"
  }
}
```

错误信息要求：

- `code` 用于程序判断。
- `message` 用中文，便于页面展示。
- `details` 放调试信息，不保证每次都有。

## 4. 常用错误码

```text
invalid_request       请求参数错误
not_found             资源不存在
data_not_ready        数据未准备好
data_stale            数据过期
provider_error        外部数据源错误
calculation_failed    计算失败
export_failed         导出失败
internal_error        未预期错误
```

## 5. 股票代码格式

内部统一使用 6 位股票代码：

```text
600000
000001
300750
```

如果需要交易所信息，单独使用：

```json
{
  "stock_code": "600000",
  "exchange": "SH"
}
```

不在公共 API 中混用 `SH600000`、`600000.SH`、`sh.600000`。

## 6. 数值字段约定

收益率、权重、回撤：

```json
{
  "total_return": 0.18,
  "max_drawdown": -0.12,
  "target_weight": 0.05
}
```

金额：

```json
{
  "market_value": 100000.0,
  "amount_cny": 52300000.0
}
```

分数：

```json
{
  "valuation_score": 82.5,
  "quality_score": 76.0,
  "total_score": 79.4
}
```

## 7. 分页和排序

列表接口支持：

```text
page
page_size
sort_by
sort_order
```

示例：

```text
GET /api/factors/scores?page=1&page_size=50&sort_by=total_score&sort_order=desc
```

## 8. API 文档更新规则

新增或修改前端依赖的接口时，必须更新本文档或技术架构中的 API 章节。

如果字段被前端使用，不能无说明地改名或删除。
