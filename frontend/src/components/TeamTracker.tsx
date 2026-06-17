import { useMemo } from 'react'
import type { Player } from '../types'
import { ShirtIcon } from './icons'
import { TeamCrest } from './TeamCrest'

/** FPL allows at most this many players from a single club in a 15-man squad. */
const MAX_PLAYERS_PER_CLUB = 3

interface TeamTrackerProps {
  squad: Player[]
}

interface ClubCount {
  team_id: number
  team: string
  team_short: string
  team_code: number
  count: number
}

/** Tally how many squad players belong to each club, most-represented first. */
function countByClub(squad: Player[]): ClubCount[] {
  const counts = new Map<number, ClubCount>()
  for (const player of squad) {
    const entry = counts.get(player.team_id)
    if (entry) {
      entry.count += 1
    } else {
      counts.set(player.team_id, {
        team_id: player.team_id,
        team: player.team,
        team_short: player.team_short,
        team_code: player.team_code,
        count: 1,
      })
    }
  }
  return [...counts.values()].sort(
    (a, b) => b.count - a.count || a.team.localeCompare(b.team),
  )
}

export function TeamTracker({ squad }: TeamTrackerProps) {
  const clubs = useMemo(() => countByClub(squad), [squad])
  const atLimit = clubs.filter((club) => club.count >= MAX_PLAYERS_PER_CLUB).length

  return (
    <section className="rounded-2xl border border-white/10 bg-slate-900/60 p-4 sm:p-5">
      <div className="mb-3 flex items-center gap-2">
        <ShirtIcon className="h-5 w-5 text-emerald-400" />
        <h2 className="text-sm font-semibold text-white">Players per club</h2>
      </div>

      {clubs.length === 0 ? (
        <p className="text-sm text-slate-400">No players in the squad yet.</p>
      ) : (
        <>
          <p className="mb-4 text-xs text-slate-400">
            {clubs.length} {clubs.length === 1 ? 'club' : 'clubs'} represented
            {atLimit > 0
              ? ` · ${atLimit} at the ${MAX_PLAYERS_PER_CLUB}-player limit`
              : ''}
          </p>

          <ul className="space-y-2.5">
            {clubs.map((club) => {
              const full = club.count >= MAX_PLAYERS_PER_CLUB
              return (
                <li key={club.team_id}>
                  <div className="mb-1 flex items-center justify-between gap-2">
                    <span className="flex min-w-0 items-center gap-2">
                      <TeamCrest
                        code={club.team_code}
                        team={club.team}
                        teamShort={club.team_short}
                        className="h-5 w-5"
                      />
                      <span className="truncate text-sm font-medium text-slate-200">
                        {club.team}
                      </span>
                    </span>
                    <span
                      className={`shrink-0 text-xs font-semibold tabular-nums ${
                        full ? 'text-amber-300' : 'text-emerald-300'
                      }`}
                    >
                      {club.count}/{MAX_PLAYERS_PER_CLUB}
                    </span>
                  </div>
                  <div className="flex gap-1" aria-hidden>
                    {Array.from({ length: MAX_PLAYERS_PER_CLUB }, (_, segment) => (
                      <span
                        key={segment}
                        className={`h-1.5 flex-1 rounded-full ${
                          segment < club.count
                            ? full
                              ? 'bg-amber-400'
                              : 'bg-emerald-500'
                            : 'bg-white/5'
                        }`}
                      />
                    ))}
                  </div>
                </li>
              )
            })}
          </ul>
        </>
      )}
    </section>
  )
}
