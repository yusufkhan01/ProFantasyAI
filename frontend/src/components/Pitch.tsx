import type { Player, Position } from '../types'
import { positionLabel } from '../lib/format'
import { PlayerToken } from './PlayerToken'
import { PositionLegend } from './PositionLegend'
import { BallIcon } from './icons'

interface PitchProps {
  players: Player[]
}

const ROWS: Position[] = ['GK', 'DEF', 'MID', 'FWD']

export function Pitch({ players }: PitchProps) {
  return (
    <section className="overflow-hidden rounded-2xl border border-white/10 shadow-xl">
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 border-b border-white/10 bg-slate-900/70 px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-white">
          <BallIcon className="h-4 w-4 text-emerald-400" />
          Starting XI
        </div>
        <PositionLegend compact />
      </div>

      <div className="relative">
        <div className="pitch-surface absolute inset-0" aria-hidden />
        {/* Field markings */}
        <div
          className="pointer-events-none absolute inset-4 rounded-xl border-2 border-white/20"
          aria-hidden
        />
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
            if (row.length === 0) return null
            return (
              <div key={position} className="flex items-center gap-2 sm:gap-3">
                <span
                  className="hidden w-12 shrink-0 text-[10px] font-bold uppercase tracking-wider text-white/70 sm:block"
                  title={positionLabel(position)}
                >
                  {position}
                </span>
                <div className="flex flex-1 flex-wrap items-center justify-center gap-2 sm:gap-4">
                  {row.map((player) => (
                    <PlayerToken key={player.id} player={player} />
                  ))}
                </div>
                <span className="hidden w-12 shrink-0 sm:block" aria-hidden />
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
