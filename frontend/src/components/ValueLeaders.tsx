import { useState } from 'react'
import { useValueLeaders } from '../hooks/useFplData'
import { POSITION_LIST, positionStyle } from '../lib/format'
import type { Position } from '../types'
import { ChartIcon } from './icons'
import { usePlayerDetail } from './playerDetailContext'

type Filter = Position | 'ALL'

const FILTERS: Array<{ label: string; value: Filter }> = [
  { label: 'All', value: 'ALL' },
  ...POSITION_LIST.map((position) => ({ label: position, value: position as Filter })),
]

export function ValueLeaders() {
  const [filter, setFilter] = useState<Filter>('ALL')
  const { openPlayer } = usePlayerDetail()
  const { data, isLoading, isError } = useValueLeaders(10, filter === 'ALL' ? undefined : filter)
  const max = data && data.length ? Math.max(...data.map((player) => player.value_score)) : 0

  return (
    <section className="rounded-2xl border border-white/10 bg-slate-900/60 p-4 sm:p-5">
      <div className="mb-3 flex items-center gap-2">
        <ChartIcon className="h-5 w-5 text-emerald-400" />
        <h2 className="text-sm font-semibold text-white">Best value players</h2>
      </div>

      <div className="mb-4 flex flex-wrap gap-1.5" role="group" aria-label="Filter by position">
        {FILTERS.map((option) => {
          const active = filter === option.value
          return (
            <button
              key={option.value}
              type="button"
              onClick={() => setFilter(option.value)}
              aria-pressed={active}
              className={`rounded-full px-2.5 py-1 text-xs font-medium transition ${
                active
                  ? 'bg-emerald-500 text-slate-950'
                  : 'bg-white/5 text-slate-300 hover:bg-white/10'
              }`}
            >
              {option.label}
            </button>
          )
        })}
      </div>

      {isLoading ? (
        <p className="text-sm text-slate-400">Loading rankings...</p>
      ) : isError || !data ? (
        <p className="text-sm text-slate-400">Rankings are unavailable right now.</p>
      ) : data.length === 0 ? (
        <p className="text-sm text-slate-400">No players found for this position.</p>
      ) : (
        <ol className="space-y-1.5">
          {data.map((player, index) => {
            const style = positionStyle(player.position)
            return (
              <li key={player.id}>
                <button
                  type="button"
                  onClick={() => openPlayer(player)}
                  className="flex w-full items-center gap-3 rounded-lg px-1.5 py-1.5 text-left transition hover:bg-white/5 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-400/60"
                >
                  <span className="w-4 shrink-0 text-right text-xs font-semibold text-slate-500">
                    {index + 1}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="mb-1 flex items-center justify-between gap-2">
                      <span className="flex min-w-0 items-center gap-1.5">
                        <span
                          className={`shrink-0 rounded px-1 py-0.5 text-[9px] font-bold uppercase tracking-wide ${style.soft} ${style.text}`}
                        >
                          {player.position}
                        </span>
                        <span className="truncate text-sm font-medium text-slate-200">
                          {player.name}
                        </span>
                        <span className="shrink-0 text-xs text-slate-500" title={player.team}>
                          {player.team_short}
                        </span>
                      </span>
                      <span className="shrink-0 text-xs font-semibold text-emerald-300">
                        {player.value_score.toFixed(1)}
                      </span>
                    </div>
                    <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/5">
                      <div
                        className={`h-full rounded-full ${style.solid}`}
                        style={{ width: `${max ? (player.value_score / max) * 100 : 0}%` }}
                      />
                    </div>
                  </div>
                </button>
              </li>
            )
          })}
        </ol>
      )}
    </section>
  )
}
