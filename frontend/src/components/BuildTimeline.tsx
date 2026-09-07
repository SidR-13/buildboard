import { Link } from 'react-router-dom'
import type { WorkflowRun } from '../services/types'

const statusStyle: Record<string, { dot: string; text: string }> = {
  success: { dot: 'bg-success', text: 'text-success' },
  failure: { dot: 'bg-failure', text: 'text-failure' },
  cancelled: { dot: 'bg-neutral', text: 'text-neutral' },
  skipped: { dot: 'bg-neutral', text: 'text-neutral' },
}

function runLabel(run: WorkflowRun) {
  if (run.status !== 'completed') return { dot: 'bg-accent animate-pulse', text: 'text-accent', label: run.status }
  const style = statusStyle[run.conclusion ?? ''] ?? statusStyle.cancelled
  return { ...style, label: run.conclusion ?? 'unknown' }
}

export function BuildTimeline({ runs }: { runs: WorkflowRun[] }) {
  return (
    <div className="divide-y divide-border rounded-lg border border-border bg-surface">
      {runs.map((run) => {
        const { dot, text, label } = runLabel(run)
        return (
          <Link
            key={run.id}
            to={`/runs/${run.id}`}
            className="flex items-center justify-between px-4 py-3 transition-colors hover:bg-surface-hover"
          >
            <div className="flex items-center gap-3">
              <span className={`h-2 w-2 rounded-full ${dot}`} />
              <span className="font-mono text-xs text-text-dim">
                {run.commit_sha.slice(0, 7)}
              </span>
              <span className="text-sm text-text-muted">{run.branch}</span>
            </div>
            <div className="flex items-center gap-4">
              <span className={`text-xs font-medium ${text}`}>{label}</span>
              <span className="font-mono text-xs text-text-dim">
                {run.duration_seconds !== null ? `${run.duration_seconds}s` : '—'}
              </span>
            </div>
          </Link>
        )
      })}
    </div>
  )
}
