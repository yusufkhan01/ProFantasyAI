import type { ReactNode } from 'react'

interface StatCardProps {
  label: string
  value: string
  hint?: string
  icon: ReactNode
}

export function StatCard({ label, value, hint, icon }: StatCardProps) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-white/10 bg-slate-900/70 p-4">
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-400">
        {icon}
      </span>
      <div className="min-w-0">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</p>
        <p className="truncate text-lg font-bold text-white">{value}</p>
        {hint ? <p className="truncate text-xs text-slate-500">{hint}</p> : null}
      </div>
    </div>
  )
}
