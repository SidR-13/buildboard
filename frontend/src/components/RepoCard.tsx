import { Link } from 'react-router-dom'
import { HealthScore } from './HealthScore'
import type { Repo, RepoMetrics } from '../services/types'

export function RepoCard({ repo, metrics }: { repo: Repo; metrics: RepoMetrics | null }) {
  return (
    <Link
      to={`/repos/${repo.id}`}
      className="block rounded-lg border border-border bg-surface p-5 transition-colors hover:bg-surface-hover"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="font-medium text-text">{repo.name}</p>
          <p className="mt-0.5 font-mono text-xs text-text-dim">{repo.full_name}</p>
        </div>
        <HealthScore score={metrics?.health_score ?? null} />
      </div>

      <div className="mt-4 flex items-center gap-6 text-sm text-text-muted">
        <span>
          Pass rate{' '}
          <span className="font-mono text-text">
            {metrics?.pass_rate !== null && metrics?.pass_rate !== undefined
              ? `${Math.round(metrics.pass_rate)}%`
              : '—'}
          </span>
        </span>
        <span>
          Avg build{' '}
          <span className="font-mono text-text">
            {metrics?.avg_duration_seconds != null
              ? `${Math.round(metrics.avg_duration_seconds)}s`
              : '—'}
          </span>
        </span>
        <span>
          Runs <span className="font-mono text-text">{metrics?.total_runs ?? 0}</span>
        </span>
        {metrics && metrics.flaky_count > 0 && (
          <span className="rounded-full bg-warning-muted px-2 py-0.5 text-xs font-medium text-warning">
            {metrics.flaky_count} flaky
          </span>
        )}
      </div>
    </Link>
  )
}
