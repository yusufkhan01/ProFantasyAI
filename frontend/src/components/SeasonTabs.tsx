import type { Season } from '../types'

interface SeasonOption {
  value: Season
  label: string
  sublabel: string
}

const SEASONS: SeasonOption[] = [
  { value: '2025-26', label: '2025/26', sublabel: 'Actual results' },
  { value: '2026-27', label: '2026/27', sublabel: 'Predicted' },
]

interface SeasonTabsProps {
  season: Season
  onChange: (season: Season) => void
}

export function SeasonTabs({ season, onChange }: SeasonTabsProps) {
  return (
    <div
      className="inline-flex rounded-xl border border-white/10 bg-slate-900/70 p-1"
      role="tablist"
      aria-label="Select season"
    >
      {SEASONS.map((option) => {
        const active = season === option.value
        return (
          <button
            key={option.value}
            type="button"
            role="tab"
            aria-selected={active}
            onClick={() => onChange(option.value)}
            className={`flex flex-col items-start rounded-lg px-4 py-2 text-left transition ${
              active ? 'bg-emerald-500 text-slate-950' : 'text-slate-300 hover:bg-white/5'
            }`}
          >
            <span className="text-sm font-bold leading-tight">{option.label}</span>
            <span
              className={`text-[11px] font-medium leading-tight ${
                active ? 'text-slate-900/70' : 'text-slate-500'
              }`}
            >
              {option.sublabel}
            </span>
          </button>
        )
      })}
    </div>
  )
}
