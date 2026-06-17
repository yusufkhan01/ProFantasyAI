import { SparklesIcon } from './icons'

const FEATURES = [
  'Real-time squad suggestions',
  'Week-by-week transfer tips',
  'Refreshed with new data every gameweek',
]

/**
 * A featured teaser for the upcoming interactive squad builder. Purely
 * informational for now — the action is disabled and flagged "coming soon".
 */
export function SquadBuilderBanner() {
  return (
    <section
      aria-label="Build your FPL Squad (coming soon)"
      className="relative overflow-hidden rounded-2xl border border-emerald-400/20 bg-gradient-to-br from-emerald-500/10 via-slate-900/60 to-slate-900/60 p-5 sm:p-6"
    >
      <div
        className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-emerald-500/10 blur-3xl"
        aria-hidden
      />

      <div className="relative flex flex-col gap-4 sm:flex-row sm:items-start sm:gap-5">
        <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-500/15 text-emerald-400">
          <SparklesIcon className="h-6 w-6" />
        </span>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-lg font-bold text-white">Build your FPL Squad</h2>
            <span className="rounded-full bg-amber-400/15 px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-amber-300">
              Coming soon
            </span>
          </div>

          <p className="mt-1.5 max-w-2xl text-sm text-slate-300">
            Build the best FPL squad with real-time suggestions, then get week-by-week transfer
            recommendations as fresh data lands every gameweek.
          </p>

          <ul className="mt-3 flex flex-wrap gap-2">
            {FEATURES.map((feature) => (
              <li
                key={feature}
                className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium text-slate-300"
              >
                {feature}
              </li>
            ))}
          </ul>
        </div>

        <button
          type="button"
          disabled
          aria-disabled="true"
          title="This feature is coming soon"
          className="shrink-0 cursor-not-allowed rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-slate-400"
        >
          Coming soon
        </button>
      </div>
    </section>
  )
}
