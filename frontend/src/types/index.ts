export type Position = 'GK' | 'DEF' | 'MID' | 'FWD'

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
  is_captain: boolean
}

export interface TeamMetrics {
  formation: string
  total_cost: number
  budget_remaining: number
  squad_total_points: number
  starting_total_points: number
}

export interface OptimalTeamResponse {
  starting_xi: Player[]
  bench: Player[]
  squad: Player[]
  captain_id: number
  metrics: TeamMetrics
  generated_at: string
}
