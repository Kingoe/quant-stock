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

interface RunWeeklyStrategyParams {
  index_code?: string
  score_date?: string
  database_url?: string
  limit?: number
  single_stock_max_weight?: number
  industry_max_weight?: number
}

interface RunWeeklyStrategyData {
  log_id: number | null
  status: 'success' | 'failed'
  recommendations_count: number
  action_counts: {
    buy: number
    hold: number
    sell: number
    watch: number
  }
  error_message?: string | null
}

interface SimulationSummaryData {
  latest_date: string | null
  account: {
    latest_value: number
    cash: number
    total_return: number
  }
  performance: {
    max_drawdown: number
    daily_volatility: number
  }
  execution: {
    total_signals: number
    executed_signals: number
    failed_signals: number
    pending_signals: number
    execution_rate: number
  }
}

export interface ParameterExperimentData {
  experiment_id: number
  name: string
  description: string | null
  parameters: Record<string, unknown>
  metrics: Record<string, unknown>
  notes: string | null
  created_at: string
}

export interface NotificationRecordData {
  id: number
  channel: string
  title: string
  content: string
  level: string
  metadata: Record<string, unknown>
  status: string
  error_message: string | null
  created_at: string
}

export interface BrokerReadinessData {
  status: string
  ready_for_manual_pilot: boolean
  failed_reasons: string[]
  allowed_actions: string[]
  trade_boundary: string
}

export interface DataUpdateLogData {
  id: number | null
  task_type: string
  status: string
  started_at: string | null
  finished_at: string | null
  error_message: string | null
  result: {
    data_type?: string
    source?: string
    records_count?: number
    skipped_count?: number
    [key: string]: unknown
  }
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

export const runWeeklyStrategy = async (
  params: RunWeeklyStrategyParams = {},
): Promise<{ data: RunWeeklyStrategyData; meta: ApiMeta }> => {
  const scoreDate = params.score_date ?? new Date().toISOString().slice(0, 10)

  try {
    const response = await axios.post(`${API_BASE_URL}/jobs/run-weekly-strategy`, null, {
      params: {
        index_code: params.index_code ?? '000906',
        score_date: scoreDate,
        database_url: params.database_url ?? 'sqlite:///../data/quant.db',
        limit: params.limit ?? 15,
        single_stock_max_weight: params.single_stock_max_weight ?? 0.08,
        industry_max_weight: params.industry_max_weight ?? 0.3,
      },
    })
    return response.data
  } catch (error) {
    console.error('Failed to run weekly strategy:', error)
    return {
      data: {
        log_id: null,
        status: 'failed',
        recommendations_count: 0,
        action_counts: {
          buy: 0,
          hold: 0,
          sell: 0,
          watch: 0,
        },
        error_message: '运行失败，请检查数据和后端服务',
      },
      meta: {},
    }
  }
}

export const getSimulationSummary = async (): Promise<{
  data: SimulationSummaryData
  meta: ApiMeta
}> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/simulation/summary`, {
      params: {
        database_url: 'sqlite:///../data/quant.db',
      },
    })
    return response.data
  } catch (error) {
    console.error('Failed to fetch simulation summary:', error)
    return {
      data: {
        latest_date: null,
        account: {
          latest_value: 0,
          cash: 0,
          total_return: 0,
        },
        performance: {
          max_drawdown: 0,
          daily_volatility: 0,
        },
        execution: {
          total_signals: 0,
          executed_signals: 0,
          failed_signals: 0,
          pending_signals: 0,
          execution_rate: 0,
        },
      },
      meta: {},
    }
  }
}

export const getExperiments = async (): Promise<{
  data: ParameterExperimentData[]
  meta: ApiMeta
}> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/experiments`, {
      params: {
        database_url: 'sqlite:///../data/quant.db',
        limit: 20,
      },
    })
    return response.data
  } catch (error) {
    console.error('Failed to fetch experiments:', error)
    return {
      data: [],
      meta: { fallback: true },
    }
  }
}

export const getNotifications = async (): Promise<{
  data: NotificationRecordData[]
  meta: ApiMeta
}> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/notifications`, {
      params: {
        database_url: 'sqlite:///../data/quant.db',
        limit: 20,
      },
    })
    return response.data
  } catch (error) {
    console.error('Failed to fetch notifications:', error)
    return {
      data: [],
      meta: { fallback: true },
    }
  }
}

export const getBrokerReadiness = async (): Promise<{
  data: BrokerReadinessData
  meta: ApiMeta
}> => {
  const fallbackData: BrokerReadinessData = {
    status: 'blocked',
    ready_for_manual_pilot: false,
    failed_reasons: ['接口不可用，请检查后端服务'],
    allowed_actions: ['read_account', 'read_positions', 'read_orders'],
    trade_boundary: '不是实盘交易入口，仅用于人工小资金试点评审。',
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/broker/readiness`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch broker readiness:', error)
    return {
      data: fallbackData,
      meta: { fallback: true },
    }
  }
}

export const getDataUpdateLogs = async (
  status?: string,
): Promise<{
  data: DataUpdateLogData[]
  meta: ApiMeta
}> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/data/update-logs`, {
      params: {
        database_url: 'sqlite:///../data/quant.db',
        limit: 20,
        ...(status ? { status } : {}),
      },
    })
    return response.data
  } catch (error) {
    console.error('Failed to fetch data update logs:', error)
    return {
      data: [],
      meta: { fallback: true },
    }
  }
}
