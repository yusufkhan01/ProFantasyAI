import { useQuery } from '@tanstack/react-query'
import { getOptimalTeam, getValueLeaders } from '../api/client'
import type { Position } from '../types'

export function useOptimalTeam() {
  return useQuery({
    queryKey: ['optimal-team'],
    queryFn: getOptimalTeam,
  })
}

export function useValueLeaders(limit = 10, position?: Position) {
  return useQuery({
    queryKey: ['value-leaders', limit, position ?? 'ALL'],
    queryFn: () => getValueLeaders(limit, position),
  })
}
