import type { Player } from '../types'
import { formatMoney, positionLabel, positionStyle } from '../lib/format'
import { TeamCrest } from './TeamCrest'
import { usePlayerDetail } from './playerDetailContext'

interface PlayerTokenProps {
  player: Player
  compact?: boolean
}

export function PlayerToken({ player, compact = false }: PlayerTokenProps) {
  const { openPlayer } = usePlayerDetail()
  const style = positionStyle(player.position)

  return (
    <button
      type="button"
      onClick={() => openPlayer(player)}
      title={`${player.full_name} · ${positionLabel(player.position)} · ${player.team}`}
      className={`group relative flex flex-col items-center rounded-xl border border-white/10 bg-slate-900/85 text-center shadow-lg backdrop-blur transition hover:-translate-y-0.5 hover:border-emerald-400/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400/60 ${
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

      <span
        className={`mb-1 rounded-full border px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider ${style.soft} ${style.text} ${style.border}`}
      >
        {player.position}
      </span>

      <span className="block w-full truncate text-sm font-semibold text-white">{player.name}</span>
      <span
        className="flex w-full items-center justify-center gap-1 text-[11px] font-medium uppercase tracking-wide text-slate-400"
        title={player.team}
      >
        <TeamCrest code={player.team_code} team={player.team} className="h-3.5 w-3.5" />
        <span className="truncate">{player.team_short || player.team}</span>
      </span>

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
    </button>
  )
}
