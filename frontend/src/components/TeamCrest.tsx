import { useState } from 'react'

interface TeamCrestProps {
  /** Stable FPL club code (NOT the season team id). */
  code: number
  /** Full club name, used for the alt text and tooltip. */
  team: string
  /** Short code shown as a text fallback when the crest can't be displayed. */
  teamShort?: string
  /** Sizing / extra classes — should set both width and height (e.g. "h-5 w-5"). */
  className?: string
}

/** FPL serves club crests keyed by the club's stable code, e.g. Man City (43). */
function crestUrl(code: number): string {
  return `https://resources.premierleague.com/premierleague/badges/70/t${code}.png`
}

/**
 * Renders a Premier League club crest from the official FPL badge CDN.
 * Falls back to a short-code chip (or nothing) if the code is missing or the
 * image fails to load, so a broken crest never leaves an empty box.
 */
export function TeamCrest({ code, team, teamShort, className = 'h-5 w-5' }: TeamCrestProps) {
  const [broken, setBroken] = useState(false)

  if (!code || broken) {
    if (!teamShort) return null
    return (
      <span
        title={team}
        className={`inline-flex items-center justify-center rounded-full bg-white/10 text-[8px] font-bold uppercase leading-none text-slate-300 ${className}`}
      >
        {teamShort}
      </span>
    )
  }

  return (
    <img
      src={crestUrl(code)}
      alt={`${team} crest`}
      title={team}
      loading="lazy"
      decoding="async"
      referrerPolicy="no-referrer"
      onError={() => setBroken(true)}
      className={`shrink-0 object-contain ${className}`}
    />
  )
}
