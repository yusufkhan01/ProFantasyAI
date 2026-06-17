import { useOptimalTeam } from './hooks/useFplData'
import { Header } from './components/Header'
import { StatsSummary } from './components/StatsSummary'
import { Pitch } from './components/Pitch'
import { Bench } from './components/Bench'
import { ValueLeaders } from './components/ValueLeaders'
import { Loader } from './components/Loader'
import { ErrorState } from './components/ErrorState'
import { PlayerDetailProvider } from './components/PlayerDetail'

export default function App() {
  const { data, isLoading, isError, error, refetch, isFetching } = useOptimalTeam()
  const captain = data?.starting_xi.find((player) => player.is_captain)

  return (
    <PlayerDetailProvider>
      <div className="min-h-full bg-slate-950 text-slate-100">
        <div className="app-glow pointer-events-none fixed inset-0" aria-hidden />

        <div className="relative">
          <Header onRefresh={() => void refetch()} isRefreshing={isFetching} />

          <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">
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
