export type Position = 'GK' | 'DEF' | 'MID' | 'FWD'

export type Season = '2025-26' | '2026-27'

export interface Player {
  id: number
  name: string
  full_name: string
  position: Position
  team_id: number
  team: string
  team_short: string
  price: number
  total_points: number
  form: number
  points_per_game: number
  ict_index: number
  selected_by_percent: number
  value_score: number
  objective_points: number
  is_captain: boolean
}

export interface TeamMetrics {
  season: Season
  is_projection: boolean
  formation: string
  total_cost: number
  budget_remaining: number
  squad_total_points: number
  starting_total_points: number
}

export interface OptimalTeamResponse {
  season: Season
  is_projection: boolean
  starting_xi: Player[]
  bench: Player[]
  squad: Player[]
  captain_id: number
  metrics: TeamMetrics
  generated_at: string
}
