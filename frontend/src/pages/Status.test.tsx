import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import Status from './Status'
import { getDataStatus, getDataUpdateLogs } from '../services/api'

vi.mock('../services/api', () => ({
  getDataStatus: vi.fn(),
  getDataUpdateLogs: vi.fn(),
}))

const mockedGetDataStatus = vi.mocked(getDataStatus)
const mockedGetDataUpdateLogs = vi.mocked(getDataUpdateLogs)

describe('Status page data update logs', () => {
  beforeEach(() => {
    mockedGetDataStatus.mockReset()
    mockedGetDataUpdateLogs.mockReset()
    mockedGetDataStatus.mockResolvedValue({
      data: {
        daily_prices: { latest_date: '2026-05-11', has_data: true },
        valuation_metrics: { latest_date: '2026-05-11', has_data: true },
        financial_metrics: { latest_date: '2026-03-31', has_data: true },
        stock_info: { latest_date: '2026-05-10', has_data: true },
      },
      meta: {},
    })
  })

  it('renders recent data update logs with status, summary and error', async () => {
    mockedGetDataUpdateLogs.mockResolvedValueOnce({
      data: [
        {
          id: 8,
          task_type: 'data_update',
          status: 'failed',
          started_at: '2026-05-12T09:00:00',
          finished_at: '2026-05-12T09:01:00',
          error_message: 'provider unavailable',
          result: {
            data_type: 'daily_prices',
            source: 'akshare',
            records_count: 0,
            skipped_count: 0,
          },
        },
        {
          id: 7,
          task_type: 'data_update',
          status: 'success',
          started_at: '2026-05-11T20:00:00',
          finished_at: '2026-05-11T20:01:00',
          error_message: null,
          result: {
            data_type: 'stock_basics',
            source: 'local_csv',
            records_count: 2,
            skipped_count: 0,
          },
        },
      ],
      meta: {},
    })

    render(<Status />)

    expect(await screen.findByRole('heading', { name: '数据更新日志' })).toBeInTheDocument()
    expect(screen.getByText('daily_prices')).toBeInTheDocument()
    expect(screen.getByText('akshare')).toBeInTheDocument()
    expect(screen.getByText('provider unavailable')).toBeInTheDocument()
    expect(screen.getByText('stock_basics')).toBeInTheDocument()
    expect(screen.getByText('local_csv')).toBeInTheDocument()
    expect(screen.getByText('2 条')).toBeInTheDocument()
  })

  it('renders a failed update log even when the result summary is empty', async () => {
    mockedGetDataUpdateLogs.mockResolvedValueOnce({
      data: [
        {
          id: 9,
          task_type: 'data_update',
          status: 'failed',
          started_at: '2026-05-12T10:00:00',
          finished_at: '2026-05-12T10:01:00',
          error_message: 'unsupported data_type: not_supported',
          result: {},
        },
      ],
      meta: {},
    })

    render(<Status />)

    expect(await screen.findByText('unsupported data_type: not_supported')).toBeInTheDocument()
    expect(screen.getAllByText('未知').length).toBeGreaterThan(0)
  })

  it('renders an empty state when no update logs exist', async () => {
    mockedGetDataUpdateLogs.mockResolvedValueOnce({
      data: [],
      meta: {},
    })

    render(<Status />)

    expect(await screen.findByText('暂无数据更新记录')).toBeInTheDocument()
  })

  it('filters update logs by status', async () => {
    const user = userEvent.setup()
    mockedGetDataUpdateLogs.mockResolvedValue({
      data: [],
      meta: {},
    })

    render(<Status />)

    await screen.findByRole('heading', { name: '数据更新日志' })
    await user.click(screen.getByRole('button', { name: '失败' }))

    expect(mockedGetDataUpdateLogs).toHaveBeenLastCalledWith('failed')
  })
})
