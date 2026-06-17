import type { OptimalTeamResponse, Player, Position, Season } from '../types'

const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '')

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`)

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`
    try {
      const body = await response.json()
      if (body?.detail) detail = body.detail
    } catch {
      // Response had no JSON body; keep the default message.
    }
    throw new Error(detail)
  }

  return response.json() as Promise<T>
}

export function getOptimalTeam(season: Season): Promise<OptimalTeamResponse> {
  return request<OptimalTeamResponse>(`/api/optimal-team?season=${encodeURIComponent(season)}`)
}

export function getValueLeaders(limit = 10, position?: Position): Promise<Player[]> {
  const params = new URLSearchParams({ limit: String(limit) })
  if (position) {
    params.set('position', position)
  }
  return request<Player[]>(`/api/players?${params.toString()}`)
}
