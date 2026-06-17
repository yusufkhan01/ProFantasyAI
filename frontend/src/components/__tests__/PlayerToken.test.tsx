import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { PlayerToken } from '../PlayerToken'
import type { Player } from '../../types'

function makePlayer(overrides: Partial<Player> = {}): Player {
  return {
    id: 1,
    name: 'Salah',
    full_name: 'Mohamed Salah',
    position: 'MID',
    team_id: 12,
    team: 'Liverpool',
    team_short: 'LIV',
    team_code: 14,
    price: 12.5,
    total_points: 200,
    form: 7.5,
    points_per_game: 6.1,
    ict_index: 250.4,
    selected_by_percent: 45.2,
    value_score: 88.3,
    objective_points: 200,
    is_captain: false,
    ...overrides,
  }
}

describe('PlayerToken', () => {
  it('renders the player name, team, price and value score', () => {
    render(<PlayerToken player={makePlayer()} />)
    expect(screen.getByText('Salah')).toBeInTheDocument()
    expect(screen.getByText('LIV')).toBeInTheDocument()
    expect(screen.getByText('£12.5m')).toBeInTheDocument()
    expect(screen.getByText('88.3')).toBeInTheDocument()
  })

  it('shows the captain badge only for the captain', () => {
    const { rerender } = render(<PlayerToken player={makePlayer({ is_captain: true })} />)
    expect(screen.getByText('C')).toBeInTheDocument()

    rerender(<PlayerToken player={makePlayer({ is_captain: false })} />)
    expect(screen.queryByText('C')).not.toBeInTheDocument()
  })
})
