import { AlertIcon, RefreshIcon } from './icons'

interface ErrorStateProps {
  message: string
  onRetry: () => void
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-white/10 bg-slate-900/70 px-6 py-16 text-center">
      <span className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-rose-500/15 text-rose-400">
        <AlertIcon className="h-7 w-7" />
      </span>
      <h2 className="text-lg font-semibold text-white">Couldn&apos;t load the squad</h2>
      <p className="mt-1 max-w-md text-sm text-slate-400">{message}</p>
      <button
        type="button"
        onClick={onRetry}
        className="mt-6 inline-flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400"
      >
        <RefreshIcon className="h-4 w-4" />
        Try again
      </button>
    </div>
  )
}
