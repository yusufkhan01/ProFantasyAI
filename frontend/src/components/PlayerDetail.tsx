import { useCallback, useEffect, useState, type ReactNode } from 'react'
import type { Player } from '../types'
import { formatMoney, formatPercent, positionLabel, positionStyle } from '../lib/format'
import { CloseIcon } from './icons'
import { TeamCrest } from './TeamCrest'
import { PlayerDetailContext } from './playerDetailContext'

/**
 * Provides a single, shared player-detail modal. Any descendant can call
 * `usePlayerDetail().openPlayer(player)` to reveal full team, position and
 * performance information for a player.
 */
export function PlayerDetailProvider({ children }: { children: ReactNode }) {
  const [player, setPlayer] = useState<Player | null>(null)
  const openPlayer = useCallback((next: Player) => setPlayer(next), [])
  const close = useCallback(() => setPlayer(null), [])

  return (
    <PlayerDetailContext.Provider value={{ openPlayer }}>
      {children}
      {player ? <PlayerDetailModal player={player} onClose={close} /> : null}
    </PlayerDetailContext.Provider>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/5 px-3 py-2">
      <p className="text-[11px] uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-0.5 text-sm font-semibold text-white">{value}</p>
    </div>
  )
}

function PlayerDetailModal({ player, onClose }: { player: Player; onClose: () => void }) {
  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onClose])

  const style = positionStyle(player.position)
  // Projected players carry an objective (expected points) that differs from
  // their actual recorded total; historical and leaderboard players don't.
  const isProjected = player.objective_points !== player.total_points

  return (
    <div
      className="animate-fade-in fixed inset-0 z-50 flex items-end justify-center bg-slate-950/70 p-4 backdrop-blur-sm sm:items-center"
      role="dialog"
      aria-modal="true"
      aria-label={`${player.full_name} details`}
      onClick={onClose}
    >
      <div
        className="animate-pop-in w-full max-w-md overflow-hidden rounded-2xl border border-white/10 bg-slate-900 shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-3 border-b border-white/10 p-5">
          <div className="flex min-w-0 items-start gap-3">
            <TeamCrest
              code={player.team_code}
              team={player.team}
              teamShort={player.team_short}
              className="mt-0.5 h-10 w-10"
            />
            <div className="min-w-0">
              <div className="mb-2 flex flex-wrap items-center gap-1.5">
                <span
                  className={`rounded-full border px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide ${style.soft} ${style.text} ${style.border}`}
                >
                  {positionLabel(player.position)}
                </span>
                {player.is_captain ? (
                  <span className="rounded-full bg-amber-400/15 px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide text-amber-300">
                    Captain
                  </span>
                ) : null}
              </div>
              <h2 className="truncate text-xl font-bold text-white">{player.full_name}</h2>
              <p className="mt-0.5 text-sm text-slate-400">
                {player.team} <span className="text-slate-500">({player.team_short})</span>
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-slate-300 transition hover:bg-white/10"
          >
            <CloseIcon className="h-4 w-4" />
          </button>
        </div>

        <div className="grid grid-cols-2 gap-2 p-5 sm:grid-cols-3">
          <Stat label="Price" value={formatMoney(player.price)} />
          <Stat label="Value score" value={player.value_score.toFixed(1)} />
          {isProjected ? (
            <Stat label="Proj. points" value={player.objective_points.toFixed(1)} />
          ) : null}
          <Stat
            label={isProjected ? '2025/26 points' : 'Total points'}
            value={String(player.total_points)}
          />
          <Stat label="Form" value={player.form.toFixed(1)} />
          <Stat label="Points / game" value={player.points_per_game.toFixed(1)} />
          <Stat label="ICT index" value={player.ict_index.toFixed(1)} />
          <Stat label="Ownership" value={formatPercent(player.selected_by_percent)} />
        </div>
      </div>
    </div>
  )
}
