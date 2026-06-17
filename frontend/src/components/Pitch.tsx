import type { Player, Position } from '../types'
import { PlayerToken } from './PlayerToken'

interface PitchProps {
  players: Player[]
}

const ROWS: Position[] = ['GK', 'DEF', 'MID', 'FWD']

export function Pitch({ players }: PitchProps) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 shadow-xl">
      <div className="pitch-surface absolute inset-0" aria-hidden />
      {/* Field markings */}
      <div className="pointer-events-none absolute inset-4 rounded-xl border-2 border-white/20" aria-hidden />
      <div
        className="pointer-events-none absolute left-4 right-4 top-1/2 h-0.5 -translate-y-1/2 bg-white/20"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute left-1/2 top-1/2 h-24 w-24 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white/20"
        aria-hidden
      />

      <div className="relative flex flex-col gap-4 p-4 sm:gap-7 sm:p-8">
        {ROWS.map((position) => {
          const row = players.filter((player) => player.position === position)
          return (
            <div
              key={position}
              className="flex flex-wrap items-center justify-center gap-2 sm:gap-4"
            >
              {row.map((player) => (
                <PlayerToken key={player.id} player={player} />
              ))}
            </div>
          )
        })}
      </div>
    </div>
  )
}
