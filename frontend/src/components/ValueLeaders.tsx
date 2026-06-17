import { useValueLeaders } from '../hooks/useFplData'
import { positionColor } from '../lib/format'
import { ChartIcon } from './icons'

export function ValueLeaders() {
  const { data, isLoading, isError } = useValueLeaders(10)
  const max = data && data.length ? Math.max(...data.map((player) => player.value_score)) : 0

  return (
    <section className="rounded-2xl border border-white/10 bg-slate-900/60 p-4 sm:p-5">
      <div className="mb-4 flex items-center gap-2">
        <ChartIcon className="h-5 w-5 text-emerald-400" />
        <h2 className="text-sm font-semibold text-white">Best value players</h2>
      </div>

      {isLoading ? (
        <p className="text-sm text-slate-400">Loading rankings...</p>
      ) : isError || !data ? (
        <p className="text-sm text-slate-400">Rankings are unavailable right now.</p>
      ) : (
        <ol className="space-y-2.5">
          {data.map((player, index) => (
            <li key={player.id} className="flex items-center gap-3">
              <span className="w-4 text-right text-xs font-semibold text-slate-500">
                {index + 1}
              </span>
              <div className="min-w-0 flex-1">
                <div className="mb-1 flex items-center justify-between gap-2">
                  <span className="truncate text-sm font-medium text-slate-200">
                    {player.name}
                    <span className="ml-1.5 text-xs text-slate-500">{player.team_short}</span>
                  </span>
                  <span className="shrink-0 text-xs font-semibold text-emerald-300">
                    {player.value_score.toFixed(1)}
                  </span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/5">
                  <div
                    className={`h-full rounded-full ${positionColor(player.position)}`}
                    style={{ width: `${max ? (player.value_score / max) * 100 : 0}%` }}
                  />
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}
