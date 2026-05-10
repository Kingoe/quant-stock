import axios from 'axios'

const API_BASE_URL = '/api'

type ApiMeta = Record<string, unknown>

interface DataStatus {
  daily_prices: { latest_date: string | null; has_data: boolean }
  valuation_metrics: { latest_date: string | null; has_data: boolean }
  financial_metrics: { latest_date: string | null; has_data: boolean }
  stock_info: { latest_date: string | null; has_data: boolean }
}

interface StrategyConfig {
  index_code: string
  min_listing_months: number
  limit: number
  single_stock_max_weight: number
  industry_max_weight: number
}

interface RebalanceData {
  buy: RebalanceItem[]
  hold: RebalanceItem[]
  sell: RebalanceItem[]
  watch: RebalanceItem[]
}

interface RebalanceItem {
  stock_code: string
  stock_name: string | null
  action: string
  target_weight: number | null
  total_score: number
  rank: number | null
  reason: string
  risk_note: string | null
}

interface BacktestMetrics {
  total_return: number
  annual_return: number
  max_drawdown: number
  sharpe_ratio: number | null
  turnover_rate: number
  win_rate: number | null
}

interface EquityCurveData {
  date: string
  value: number
}

interface DrawdownData {
  date: string
  drawdown: number
}

export const getDataStatus = async (): Promise<{ data: DataStatus; meta: ApiMeta }> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/data/status`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch data status:', error)
    return {
      data: {
        daily_prices: { latest_date: null, has_data: false },
        valuation_metrics: { latest_date: null, has_data: false },
        financial_metrics: { latest_date: null, has_data: false },
        stock_info: { latest_date: null, has_data: false },
      },
      meta: {},
    }
  }
}

export const getStrategyConfig = async (): Promise<{ data: StrategyConfig; meta: ApiMeta }> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/config/strategy`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch strategy config:', error)
    return {
      data: {
        index_code: '000906',
        min_listing_months: 12,
        limit: 15,
        single_stock_max_weight: 0.08,
        industry_max_weight: 0.3,
      },
      meta: {},
    }
  }
}

export const getRebalanceLatest = async (): Promise<{ data: RebalanceData; meta: ApiMeta }> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/rebalance/latest`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch rebalance latest:', error)
    return {
      data: {
        buy: [],
        hold: [],
        sell: [],
        watch: [],
      },
      meta: {},
    }
  }
}

export const getBacktestSummary = async (): Promise<{ data: BacktestMetrics; meta: ApiMeta }> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/backtest/summary`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch backtest summary:', error)
    return {
      data: {
        total_return: 0,
        annual_return: 0,
        max_drawdown: 0,
        sharpe_ratio: null,
        turnover_rate: 0,
        win_rate: null,
      },
      meta: {},
    }
  }
}

export const getEquityCurve = async (): Promise<{ data: EquityCurveData[]; meta: ApiMeta }> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/backtest/equity-curve`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch equity curve:', error)
    return {
      data: [],
      meta: {},
    }
  }
}

export const getDrawdownCurve = async (): Promise<{ data: DrawdownData[]; meta: ApiMeta }> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/backtest/drawdown-curve`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch drawdown curve:', error)
    return {
      data: [],
      meta: {},
    }
  }
}
