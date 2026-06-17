import { useQuery } from '@tanstack/react-query'
import { getOptimalTeam, getValueLeaders } from '../api/client'
import type { Position, Season } from '../types'

export function useOptimalTeam(season: Season) {
  return useQuery({
    queryKey: ['optimal-team', season],
    queryFn: () => getOptimalTeam(season),
  })
}

export function useValueLeaders(limit = 10, position?: Position) {
  return useQuery({
    queryKey: ['value-leaders', limit, position ?? 'ALL'],
    queryFn: () => getValueLeaders(limit, position),
  })
}
