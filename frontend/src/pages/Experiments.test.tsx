import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import Experiments from './Experiments'
import { getExperiments } from '../services/api'

vi.mock('../services/api', () => ({
  getExperiments: vi.fn(),
}))

const mockedGetExperiments = vi.mocked(getExperiments)

describe('Experiments page', () => {
  beforeEach(() => {
    mockedGetExperiments.mockReset()
  })

  it('renders experiment records with metrics and parameters', async () => {
    mockedGetExperiments.mockResolvedValueOnce({
      data: [
        {
          experiment_id: 2,
          name: '估值权重提升实验',
          description: '提高估值权重，观察回撤变化',
          parameters: {
            limit: 20,
            factor_weights: { valuation: 0.35, quality: 0.25 },
          },
          metrics: {
            annual_return: 0.12,
            max_drawdown: -0.08,
            sharpe: 1.15,
          },
          notes: '仅用于复盘',
          created_at: '2026-05-11T09:30:00',
        },
      ],
      meta: {},
    })

    render(<Experiments />)

    expect(await screen.findByRole('heading', { name: '实验记录' })).toBeInTheDocument()
    expect(screen.getAllByText('估值权重提升实验').length).toBeGreaterThan(0)
    expect(screen.getByText('年化收益')).toBeInTheDocument()
    expect(screen.getByText('12.00%')).toBeInTheDocument()
    expect(screen.getByText('最大回撤')).toBeInTheDocument()
    expect(screen.getByText('-8.00%')).toBeInTheDocument()
    expect(screen.getByText(/factor_weights/)).toBeInTheDocument()
    expect(screen.getByText('仅用于复盘')).toBeInTheDocument()
  })

  it('renders an empty state when no experiments exist', async () => {
    mockedGetExperiments.mockResolvedValueOnce({
      data: [],
      meta: {},
    })

    render(<Experiments />)

    expect(await screen.findByText('暂无实验记录')).toBeInTheDocument()
  })

  it('renders a stable empty state when the API fallback is returned', async () => {
    mockedGetExperiments.mockResolvedValueOnce({
      data: [],
      meta: { fallback: true },
    })

    render(<Experiments />)

    expect(await screen.findByText('暂无实验记录')).toBeInTheDocument()
  })
})
