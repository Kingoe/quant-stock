import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import Overview from './Overview'
import { getSimulationSummary } from '../services/api'

vi.mock('../services/api', () => ({
  getSimulationSummary: vi.fn(),
}))

const mockedGetSimulationSummary = vi.mocked(getSimulationSummary)

describe('Overview simulation section', () => {
  beforeEach(() => {
    mockedGetSimulationSummary.mockReset()
  })

  it('renders simulation account and execution summary', async () => {
    mockedGetSimulationSummary.mockResolvedValueOnce({
      data: {
        latest_date: '2026-05-10',
        account: {
          latest_value: 102000,
          cash: 88000,
          total_return: 2,
        },
        performance: {
          max_drawdown: 1.92,
          daily_volatility: 0.64,
        },
        execution: {
          total_signals: 2,
          executed_signals: 1,
          failed_signals: 0,
          pending_signals: 1,
          execution_rate: 0.5,
        },
      },
      meta: {},
    })

    render(<Overview />)

    expect(await screen.findByRole('heading', { name: '模拟运行' })).toBeInTheDocument()
    expect(screen.getByText('102,000')).toBeInTheDocument()
    expect(screen.getByText('2.00%')).toBeInTheDocument()
    expect(screen.getByText('1 / 2')).toBeInTheDocument()
    expect(screen.getByText('待执行 1 条')).toBeInTheDocument()
  })

  it('renders an empty simulation state when there is no data', async () => {
    mockedGetSimulationSummary.mockResolvedValueOnce({
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
    })

    render(<Overview />)

    expect(await screen.findByText('暂无模拟运行数据')).toBeInTheDocument()
  })
})
