import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { TeamTracker } from '../TeamTracker'
import type { Player } from '../../types'

let nextId = 1

function makePlayer(
  team: string,
  team_short: string,
  team_id: number,
  team_code: number,
): Player {
  return {
    id: nextId++,
    name: `Player ${nextId}`,
    full_name: `Player ${nextId}`,
    position: 'MID',
    team_id,
    team,
    team_short,
    team_code,
    price: 5,
    total_points: 100,
    form: 5,
    points_per_game: 4,
    ict_index: 100,
    selected_by_percent: 10,
    value_score: 20,
    objective_points: 100,
    is_captain: false,
  }
}

const squad: Player[] = [
  makePlayer('Man City', 'MCI', 13, 43),
  makePlayer('Man City', 'MCI', 13, 43),
  makePlayer('Liverpool', 'LIV', 12, 14),
  makePlayer('Liverpool', 'LIV', 12, 14),
  makePlayer('Liverpool', 'LIV', 12, 14),
  makePlayer('Arsenal', 'ARS', 1, 3),
]

describe('TeamTracker', () => {
  it('shows each club with its player count out of the limit', () => {
    render(<TeamTracker squad={squad} />)
    expect(screen.getByText('Man City')).toBeInTheDocument()
    expect(screen.getByText('Liverpool')).toBeInTheDocument()
    expect(screen.getByText('Arsenal')).toBeInTheDocument()
    expect(screen.getByText('2/3')).toBeInTheDocument()
    expect(screen.getByText('1/3')).toBeInTheDocument()
  })

  it('renders a club crest for each represented club', () => {
    render(<TeamTracker squad={squad} />)
    expect(screen.getByRole('img', { name: 'Man City crest' })).toHaveAttribute(
      'src',
      'https://resources.premierleague.com/premierleague/badges/70/t43.png',
    )
    expect(screen.getAllByRole('img')).toHaveLength(3)
  })

  it('summarises how many clubs are at the per-club limit', () => {
    render(<TeamTracker squad={squad} />)
    // Liverpool is the only club at 3/3.
    expect(screen.getByText('3/3')).toBeInTheDocument()
    expect(screen.getByText(/3 clubs represented/)).toBeInTheDocument()
    expect(screen.getByText(/1 at the 3-player limit/)).toBeInTheDocument()
  })

  it('renders an empty state when there are no players', () => {
    render(<TeamTracker squad={[]} />)
    expect(screen.getByText('No players in the squad yet.')).toBeInTheDocument()
  })
})
