import { useState } from 'react'
import { useOptimalTeam } from './hooks/useFplData'
import { Header } from './components/Header'
import { SeasonTabs } from './components/SeasonTabs'
import { StatsSummary } from './components/StatsSummary'
import { Pitch } from './components/Pitch'
import { Bench } from './components/Bench'
import { ValueLeaders } from './components/ValueLeaders'
import { Loader } from './components/Loader'
import { ErrorState } from './components/ErrorState'
import { PlayerDetailProvider } from './components/PlayerDetail'
import type { Season } from './types'

const SEASON_COPY: Record<Season, { title: string; description: string }> = {
  '2025-26': {
    title: 'Best XI you could have had',
    description:
      'The points-maximising £100m squad for 2025/26, using real results and season-start prices.',
  },
  '2026-27': {
    title: 'Projected best squad',
    description:
      'A £100m squad for 2026/27, ranked by expected points projected from 2025/26 underlying data.',
  },
}

export default function App() {
  const [season, setSeason] = useState<Season>('2025-26')
  const { data, isLoading, isError, error, refetch, isFetching } = useOptimalTeam(season)
  const captain = data?.starting_xi.find((player) => player.is_captain)
  const copy = SEASON_COPY[season]

  return (
    <PlayerDetailProvider>
      <div className="min-h-full bg-slate-950 text-slate-100">
        <div className="app-glow pointer-events-none fixed inset-0" aria-hidden />

        <div className="relative">
          <Header onRefresh={() => void refetch()} isRefreshing={isFetching} />

          <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
            <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
              <div className="min-w-0">
                <h2 className="flex flex-wrap items-center gap-2 text-xl font-bold text-white">
                  {copy.title}
                  {season === '2026-27' ? (
                    <span className="rounded-full bg-amber-400/15 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-amber-300">
                      Prediction
                    </span>
                  ) : null}
                </h2>
                <p className="mt-1 max-w-xl text-sm text-slate-400">{copy.description}</p>
              </div>
              <SeasonTabs season={season} onChange={setSeason} />
            </div>

            {isLoading ? (
              <Loader />
            ) : isError ? (
              <ErrorState
                message={error instanceof Error ? error.message : 'An unexpected error occurred.'}
                onRetry={() => void refetch()}
              />
            ) : data ? (
              <div className="space-y-6">
                <StatsSummary metrics={data.metrics} captain={captain} />
                <div className="grid gap-6 lg:grid-cols-3">
                  <div className="space-y-6 lg:col-span-2">
                    <Pitch players={data.starting_xi} />
                    <Bench players={data.bench} />
                  </div>
                  <ValueLeaders />
                </div>
              </div>
            ) : null}
          </main>

          <footer className="mx-auto max-w-6xl px-4 pb-10 pt-4 text-center text-xs text-slate-500 sm:px-6">
            <p>
              Built with FastAPI and React. Data from the official Fantasy Premier League API.
              Not affiliated with the Premier League.
            </p>
          </footer>
        </div>
      </div>
    </PlayerDetailProvider>
  )
}
