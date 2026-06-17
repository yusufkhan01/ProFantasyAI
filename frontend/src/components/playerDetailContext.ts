import { createContext, useContext } from 'react'
import type { Player } from '../types'

export interface PlayerDetailContextValue {
  /** Open the detail panel for a given player. */
  openPlayer: (player: Player) => void
}

export const PlayerDetailContext = createContext<PlayerDetailContextValue>({
  openPlayer: () => {},
})

/** Access the player-detail opener from anywhere inside the provider. */
export function usePlayerDetail(): PlayerDetailContextValue {
  return useContext(PlayerDetailContext)
}
