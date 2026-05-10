import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import Rebalance from './Rebalance'
import { runWeeklyStrategy } from '../services/api'

vi.mock('../services/api', () => ({
  runWeeklyStrategy: vi.fn(),
}))

const mockedRunWeeklyStrategy = vi.mocked(runWeeklyStrategy)

describe('Rebalance manual run', () => {
  beforeEach(() => {
    mockedRunWeeklyStrategy.mockReset()
  })

  it('runs the weekly strategy and shows the result summary', async () => {
    mockedRunWeeklyStrategy.mockResolvedValueOnce({
      data: {
        log_id: 7,
        status: 'success',
        recommendations_count: 3,
        action_counts: {
          buy: 1,
          hold: 1,
          sell: 0,
          watch: 1,
        },
      },
      meta: {},
    })
    const user = userEvent.setup()

    render(<Rebalance />)

    await user.click(screen.getByRole('button', { name: '运行本周策略' }))

    expect(mockedRunWeeklyStrategy).toHaveBeenCalledTimes(1)
    expect(await screen.findByText('运行成功，生成 3 条建议')).toBeInTheDocument()
  })

  it('shows a clear error state when the weekly strategy fails', async () => {
    mockedRunWeeklyStrategy.mockResolvedValueOnce({
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
        error_message: '数据不足',
      },
      meta: {},
    })
    const user = userEvent.setup()

    render(<Rebalance />)

    await user.click(screen.getByRole('button', { name: '运行本周策略' }))

    expect(await screen.findByText('运行失败：数据不足')).toBeInTheDocument()
  })
})
