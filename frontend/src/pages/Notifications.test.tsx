import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import Notifications from './Notifications'
import { getNotifications } from '../services/api'

vi.mock('../services/api', () => ({
  getNotifications: vi.fn(),
}))

const mockedGetNotifications = vi.mocked(getNotifications)

describe('Notifications page', () => {
  beforeEach(() => {
    mockedGetNotifications.mockReset()
  })

  it('renders notification records with channel, level, status and metadata', async () => {
    mockedGetNotifications.mockResolvedValueOnce({
      data: [
        {
          id: 3,
          channel: 'local',
          title: '本周策略已完成',
          content: '生成 12 条建议',
          level: 'success',
          metadata: { recommendations: 12, buy: 3 },
          status: 'success',
          error_message: null,
          created_at: '2026-05-11T10:30:00',
        },
      ],
      meta: {},
    })

    render(<Notifications />)

    expect(await screen.findByRole('heading', { name: '通知历史' })).toBeInTheDocument()
    expect(screen.getByText('本周策略已完成')).toBeInTheDocument()
    expect(screen.getByText('local')).toBeInTheDocument()
    expect(screen.getByText('success')).toBeInTheDocument()
    expect(screen.getByText('生成 12 条建议')).toBeInTheDocument()
    expect(screen.getByText(/recommendations/)).toBeInTheDocument()
    expect(screen.getByText('2026-05-11T10:30:00')).toBeInTheDocument()
  })

  it('renders an empty state when no notifications exist', async () => {
    mockedGetNotifications.mockResolvedValueOnce({
      data: [],
      meta: {},
    })

    render(<Notifications />)

    expect(await screen.findByText('暂无通知记录')).toBeInTheDocument()
  })

  it('renders a stable empty state when the API fallback is returned', async () => {
    mockedGetNotifications.mockResolvedValueOnce({
      data: [],
      meta: { fallback: true },
    })

    render(<Notifications />)

    expect(await screen.findByText('暂无通知记录')).toBeInTheDocument()
  })
})
