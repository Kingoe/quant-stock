import axios from 'axios'
import { describe, expect, it, vi } from 'vitest'

import { getDataStatus, getRebalanceLatest } from './api'

vi.mock('axios')

const mockedAxios = vi.mocked(axios)

describe('api fallback states', () => {
  it('returns an empty data status when the backend request fails', async () => {
    mockedAxios.get.mockRejectedValueOnce(new Error('network unavailable'))

    const result = await getDataStatus()

    expect(result.data.daily_prices).toEqual({ latest_date: null, has_data: false })
    expect(result.data.valuation_metrics).toEqual({ latest_date: null, has_data: false })
    expect(result.data.financial_metrics).toEqual({ latest_date: null, has_data: false })
    expect(result.data.stock_info).toEqual({ latest_date: null, has_data: false })
  })

  it('returns empty rebalance lists when the backend request fails', async () => {
    mockedAxios.get.mockRejectedValueOnce(new Error('network unavailable'))

    const result = await getRebalanceLatest()

    expect(result.data).toEqual({
      buy: [],
      hold: [],
      sell: [],
      watch: [],
    })
  })
})
