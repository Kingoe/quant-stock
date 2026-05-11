import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import BrokerReadiness from './BrokerReadiness'
import { getBrokerReadiness } from '../services/api'

vi.mock('../services/api', () => ({
  getBrokerReadiness: vi.fn(),
}))

const mockedGetBrokerReadiness = vi.mocked(getBrokerReadiness)

describe('BrokerReadiness page', () => {
  beforeEach(() => {
    mockedGetBrokerReadiness.mockReset()
  })

  it('renders blocked readiness state with failed reasons and read-only actions', async () => {
    mockedGetBrokerReadiness.mockResolvedValueOnce({
      data: {
        status: 'blocked',
        ready_for_manual_pilot: false,
        failed_reasons: ['模拟运行天数不足', '通知渠道未启用'],
        allowed_actions: ['read_account', 'read_positions', 'read_orders'],
        trade_boundary: '不是实盘交易入口，仅用于人工小资金试点评审。',
      },
      meta: {},
    })

    render(<BrokerReadiness />)

    expect(await screen.findByRole('heading', { name: '券商准入评估' })).toBeInTheDocument()
    expect(screen.getByText('blocked')).toBeInTheDocument()
    expect(screen.getByText('不可进入试点评审')).toBeInTheDocument()
    expect(screen.getByText('模拟运行天数不足')).toBeInTheDocument()
    expect(screen.getByText('通知渠道未启用')).toBeInTheDocument()
    expect(screen.getByText('read_account')).toBeInTheDocument()
    expect(screen.getByText('read_positions')).toBeInTheDocument()
    expect(screen.getByText('read_orders')).toBeInTheDocument()
    expect(screen.getByText('不是实盘交易入口，仅用于人工小资金试点评审。')).toBeInTheDocument()
    expect(screen.getByText('不自动下单')).toBeInTheDocument()
  })

  it('renders manual pilot review state when readiness checks pass', async () => {
    mockedGetBrokerReadiness.mockResolvedValueOnce({
      data: {
        status: 'manual_pilot_review',
        ready_for_manual_pilot: true,
        failed_reasons: [],
        allowed_actions: ['read_account', 'read_positions', 'read_orders'],
        trade_boundary: '不是实盘交易入口，仅用于人工小资金试点评审。',
      },
      meta: {},
    })

    render(<BrokerReadiness />)

    expect(await screen.findByText('manual_pilot_review')).toBeInTheDocument()
    expect(screen.getByText('可进入人工试点评审')).toBeInTheDocument()
    expect(screen.getByText('暂无失败原因')).toBeInTheDocument()
  })

  it('renders fallback blocked state when the API fallback is returned', async () => {
    mockedGetBrokerReadiness.mockResolvedValueOnce({
      data: {
        status: 'blocked',
        ready_for_manual_pilot: false,
        failed_reasons: ['接口不可用，请检查后端服务'],
        allowed_actions: ['read_account', 'read_positions', 'read_orders'],
        trade_boundary: '不是实盘交易入口，仅用于人工小资金试点评审。',
      },
      meta: { fallback: true },
    })

    render(<BrokerReadiness />)

    expect(await screen.findByText('接口不可用，请检查后端服务')).toBeInTheDocument()
  })
})
