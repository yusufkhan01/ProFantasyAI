import type { Player } from '../types'
import { formatMoney, positionColor } from '../lib/format'

interface PlayerTokenProps {
  player: Player
  compact?: boolean
}

export function PlayerToken({ player, compact = false }: PlayerTokenProps) {
  return (
    <div
      className={`relative flex flex-col items-center rounded-xl border border-white/10 bg-slate-900/85 text-center shadow-lg backdrop-blur transition hover:-translate-y-0.5 hover:border-emerald-400/40 ${
        compact ? 'w-[4.75rem] p-2 sm:w-24' : 'w-[5.25rem] p-2.5 sm:w-28'
      }`}
    >
      {player.is_captain ? (
        <span
          className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-amber-400 text-[10px] font-extrabold text-slate-900 ring-2 ring-slate-900"
          title="Captain"
        >
          C
        </span>
      ) : null}

      <span className={`mb-1 h-1.5 w-8 rounded-full ${positionColor(player.position)}`} />

      <p className="w-full truncate text-sm font-semibold text-white" title={player.full_name}>
        {player.name}
      </p>
      <p className="text-[11px] font-medium uppercase tracking-wide text-slate-400">
        {player.team_short || player.team}
      </p>

      <div className="mt-1.5 flex w-full items-center justify-between gap-1 text-[11px]">
        <span className="rounded bg-white/5 px-1.5 py-0.5 font-medium text-slate-300">
          {formatMoney(player.price)}
        </span>
        <span
          className="rounded bg-emerald-500/15 px-1.5 py-0.5 font-semibold text-emerald-300"
          title="Value score"
        >
          {player.value_score.toFixed(1)}
        </span>
      </div>
    </div>
  )
}
