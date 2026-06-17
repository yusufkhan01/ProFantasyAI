import { BallIcon, GithubIcon, RefreshIcon } from './icons'

const REPO_URL = 'https://github.com/yusufkhan01/ProFantasyAI'

interface HeaderProps {
  onRefresh: () => void
  isRefreshing: boolean
}

export function Header({ onRefresh, isRefreshing }: HeaderProps) {
  return (
    <header className="border-b border-white/10 bg-slate-950/60 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <div className="flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-500/15 text-emerald-400 ring-1 ring-emerald-500/30">
            <BallIcon className="h-6 w-6" />
          </span>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white sm:text-xl">
              ProFantasy<span className="text-emerald-400">AI</span>
            </h1>
            <p className="text-xs text-slate-400 sm:text-sm">
              The optimal Fantasy Premier League squad, built from live data
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onRefresh}
            disabled={isRefreshing}
            className="inline-flex items-center gap-2 rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RefreshIcon className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </button>
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            aria-label="View source on GitHub"
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-white/10 bg-white/5 text-slate-200 transition hover:bg-white/10"
          >
            <GithubIcon className="h-4 w-4" />
          </a>
        </div>
      </div>
    </header>
  )
}
