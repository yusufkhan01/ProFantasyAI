import { POSITION_LIST, positionLabel, positionStyle } from '../lib/format'

interface PositionLegendProps {
  /** When true, hide the full position names on small screens. */
  compact?: boolean
}

/** A colour key that explains what each position colour means. */
export function PositionLegend({ compact = false }: PositionLegendProps) {
  return (
    <ul className="flex flex-wrap items-center gap-x-3 gap-y-1.5" aria-label="Position colour key">
      {POSITION_LIST.map((position) => {
        const style = positionStyle(position)
        return (
          <li key={position} className="flex items-center gap-1.5 text-[11px] text-slate-300">
            <span className={`h-2.5 w-2.5 rounded-full ${style.solid}`} aria-hidden />
            <span className="font-semibold">{position}</span>
            <span className={`text-slate-400 ${compact ? 'hidden sm:inline' : ''}`}>
              {positionLabel(position)}
            </span>
          </li>
        )
      })}
    </ul>
  )
}
