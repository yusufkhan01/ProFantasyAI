import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { StatsSummary } from '../StatsSummary'
import type { Player, TeamMetrics } from '../../types'

const metrics: TeamMetrics = {
  formation: '3-4-3',
  total_cost: 99.5,
  budget_remaining: 0.5,
  squad_total_points: 1200,
  starting_total_points: 950,
}

const captain: Player = {
  id: 7,
  name: 'Haaland',
  full_name: 'Erling Haaland',
  position: 'FWD',
  team_id: 13,
  team: 'Man City',
  team_short: 'MCI',
  price: 15,
  total_points: 260,
  form: 8.2,
  points_per_game: 7.0,
  ict_index: 300,
  selected_by_percent: 70,
  value_score: 92.1,
  is_captain: true,
}

describe('StatsSummary', () => {
  it('renders formation, squad cost and the captain name', () => {
    render(<StatsSummary metrics={metrics} captain={captain} />)
    expect(screen.getByText('3-4-3')).toBeInTheDocument()
    expect(screen.getByText('£99.5m')).toBeInTheDocument()
    expect(screen.getByText('Haaland')).toBeInTheDocument()
  })

  it('renders a placeholder when there is no captain', () => {
    render(<StatsSummary metrics={metrics} />)
    expect(screen.getByText('-')).toBeInTheDocument()
  })
})
