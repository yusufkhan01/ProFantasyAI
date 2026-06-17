import type { Player, TeamMetrics } from '../types'
import { formatMoney, positionLabel } from '../lib/format'
import { StatCard } from './StatCard'
import { BallIcon, SparklesIcon, TrophyIcon, WalletIcon } from './icons'

interface StatsSummaryProps {
  metrics: TeamMetrics
  captain?: Player
}

export function StatsSummary({ metrics, captain }: StatsSummaryProps) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
      <StatCard
        label="Formation"
        value={metrics.formation}
        icon={<BallIcon className="h-5 w-5" />}
      />
      <StatCard
        label="Squad cost"
        value={formatMoney(metrics.total_cost)}
        icon={<WalletIcon className="h-5 w-5" />}
      />
      <StatCard
        label="In the bank"
        value={formatMoney(metrics.budget_remaining)}
        icon={<WalletIcon className="h-5 w-5" />}
      />
      <StatCard
        label="XI points"
        value={String(metrics.starting_total_points)}
        hint={`${metrics.squad_total_points} squad total`}
        icon={<TrophyIcon className="h-5 w-5" />}
      />
      <StatCard
        label="Captain"
        value={captain?.name ?? '-'}
        hint={
          captain
            ? `${positionLabel(captain.position)} · ${captain.team_short} · ${captain.value_score.toFixed(1)}`
            : undefined
        }
        icon={<SparklesIcon className="h-5 w-5" />}
      />
    </div>
  )
}
