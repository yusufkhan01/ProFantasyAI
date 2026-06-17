import type { Position } from '../types'

export function formatMoney(millions: number): string {
  return `£${millions.toFixed(1)}m`
}

/** Tailwind background class used to colour-code a position. */
export function positionColor(position: Position | string): string {
  switch (position) {
    case 'GK':
      return 'bg-amber-500'
    case 'DEF':
      return 'bg-sky-500'
    case 'MID':
      return 'bg-emerald-500'
    case 'FWD':
      return 'bg-rose-500'
    default:
      return 'bg-slate-500'
  }
}

export const POSITION_ORDER: Record<string, number> = {
  GK: 0,
  DEF: 1,
  MID: 2,
  FWD: 3,
}
