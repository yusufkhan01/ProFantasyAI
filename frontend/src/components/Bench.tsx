import type { Player } from '../types'
import { PlayerToken } from './PlayerToken'
import { ShirtIcon } from './icons'

interface BenchProps {
  players: Player[]
}

export function Bench({ players }: BenchProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-900/60 p-4">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-300">
        <ShirtIcon className="h-4 w-4 text-slate-400" />
        Bench
        <span className="text-xs font-normal text-slate-500">({players.length})</span>
      </div>
      <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3">
        {players.map((player) => (
          <PlayerToken key={player.id} player={player} compact />
        ))}
      </div>
    </div>
  )
}
