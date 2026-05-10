import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import App from './App'

describe('App workspace navigation', () => {
  it('renders the overview first and switches to the rebalance page', async () => {
    const user = userEvent.setup()

    render(<App />)

    expect(screen.getByRole('heading', { name: '总览' })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: '本周调仓' }))

    expect(screen.getByRole('heading', { name: '本周调仓' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /买入/ })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /卖出/ })).toBeInTheDocument()
  })
})
