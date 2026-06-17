import type { Position } from '../types'

export function formatMoney(millions: number): string {
  return `£${millions.toFixed(1)}m`
}

export function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`
}

/** Positions in pitch order, goalkeeper first. */
export const POSITION_LIST: Position[] = ['GK', 'DEF', 'MID', 'FWD']

/** Full, human-readable name for each position code. */
export const POSITION_LABEL: Record<Position, string> = {
  GK: 'Goalkeeper',
  DEF: 'Defender',
  MID: 'Midfielder',
  FWD: 'Forward',
}

/** A coordinated set of Tailwind classes for colour-coding a position. */
export interface PositionStyle {
  /** Solid fill — bars, dots, progress. */
  solid: string
  /** Translucent fill — chips and badges. */
  soft: string
  /** Accent text colour. */
  text: string
  /** Translucent border. */
  border: string
}

const POSITION_STYLES: Record<Position, PositionStyle> = {
  GK: {
    solid: 'bg-amber-500',
    soft: 'bg-amber-500/15',
    text: 'text-amber-300',
    border: 'border-amber-500/40',
  },
  DEF: {
    solid: 'bg-sky-500',
    soft: 'bg-sky-500/15',
    text: 'text-sky-300',
    border: 'border-sky-500/40',
  },
  MID: {
    solid: 'bg-emerald-500',
    soft: 'bg-emerald-500/15',
    text: 'text-emerald-300',
    border: 'border-emerald-500/40',
  },
  FWD: {
    solid: 'bg-rose-500',
    soft: 'bg-rose-500/15',
    text: 'text-rose-300',
    border: 'border-rose-500/40',
  },
}

const FALLBACK_STYLE: PositionStyle = {
  solid: 'bg-slate-500',
  soft: 'bg-slate-500/15',
  text: 'text-slate-300',
  border: 'border-slate-500/40',
}

/** Full colour palette used to colour-code a position. */
export function positionStyle(position: Position | string): PositionStyle {
  return POSITION_STYLES[position as Position] ?? FALLBACK_STYLE
}

/** Tailwind background class used to colour-code a position. */
export function positionColor(position: Position | string): string {
  return positionStyle(position).solid
}

/** Full human-readable name for a position code (falls back to the code). */
export function positionLabel(position: Position | string): string {
  return POSITION_LABEL[position as Position] ?? position
}

export const POSITION_ORDER: Record<string, number> = {
  GK: 0,
  DEF: 1,
  MID: 2,
  FWD: 3,
}
