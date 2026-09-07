import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Link, useParams } from 'react-router-dom'
import { BuildTimeline } from '../components/BuildTimeline'
import { fetchRepoRuns } from '../services/api'
import { useWebSocket } from '../hooks/useWebSocket'
import type { WorkflowRun } from '../services/types'

interface RunUpdateMessage {
  event: 'run_update'
  run: {
    id: string
    github_run_id: number
    workflow_name: string
    branch: string
    commit_sha: string
    status: string
    conclusion: string | null
    duration_seconds: number | null
  }
}

const chartColors = {
  grid: '#26262f',
  axis: '#55555f',
  accent: '#22d3ee',
  success: '#34d399',
  failure: '#f87171',
}

function ChartTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="rounded-md border border-border bg-surface px-3 py-2 text-xs shadow-lg">
      <p className="font-mono text-text-dim">{label}</p>
      {payload.map((p: any) => (
        <p key={p.dataKey} className="font-mono text-text">
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  )
}

export function RepoDetail() {
  const { repoId } = useParams()
  const [runs, setRuns] = useState<WorkflowRun[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!repoId) return
    fetchRepoRuns(repoId)
      .then(setRuns)
      .catch(() => setError('Could not load build history for this repo.'))
  }, [repoId])

  const wsUrl = repoId ? `${import.meta.env.VITE_WS_URL}/ws/${repoId}` : null
  const { connected } = useWebSocket(wsUrl, (data) => {
    const msg = data as RunUpdateMessage
    if (msg.event !== 'run_update') return

    setRuns((prev) => {
      const incoming = msg.run
      if (!prev) {
        return [{ ...incoming, started_at: null, completed_at: null }]
      }
      const exists = prev.some((r) => r.id === incoming.id)
      if (exists) {
        return prev.map((r) => (r.id === incoming.id ? { ...r, ...incoming } : r))
      }
      return [{ ...incoming, started_at: null, completed_at: null }, ...prev]
    })
  })

  // API returns newest-first; charts read left-to-right chronologically.
  const chronological = runs ? [...runs].reverse() : []

  const durationData = chronological
    .filter((r) => r.duration_seconds !== null)
    .map((r) => ({
      label: r.commit_sha.slice(0, 7),
      duration: r.duration_seconds,
    }))

  const outcomeData = chronological
    .filter((r) => r.status === 'completed')
    .map((r) => ({
      label: r.commit_sha.slice(0, 7),
      outcome: r.conclusion === 'success' ? 1 : 0,
      conclusion: r.conclusion,
    }))

  return (
    <div className="min-h-screen bg-bg text-text">
      <header className="flex items-center justify-between border-b border-border px-8 py-5">
        <Link to="/" className="text-sm text-accent hover:underline">
          ← Dashboard
        </Link>
        <span className="flex items-center gap-1.5 text-xs font-medium text-text-dim">
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              connected ? 'bg-success animate-pulse' : 'bg-neutral'
            }`}
          />
          {connected ? 'Live' : 'Offline'}
        </span>
      </header>

      <main className="mx-auto max-w-3xl space-y-8 px-8 py-8">
        {error && (
          <div className="rounded-lg border border-failure/30 bg-failure-muted p-4 text-sm text-failure">
            {error}
          </div>
        )}

        {!error && runs === null && (
          <div className="h-64 animate-pulse rounded-lg border border-border bg-surface" />
        )}

        {!error && runs !== null && runs.length === 0 && (
          <div className="rounded-lg border border-border bg-surface p-8 text-center">
            <p className="text-text">No builds recorded yet</p>
          </div>
        )}

        {!error && runs !== null && runs.length > 0 && (
          <>
            <section>
              <h2 className="mb-3 font-mono text-xs uppercase tracking-wider text-text-dim">
                Build duration
              </h2>
              <div className="h-48 rounded-lg border border-border bg-surface p-4">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={durationData}>
                    <CartesianGrid stroke={chartColors.grid} vertical={false} />
                    <XAxis
                      dataKey="label"
                      stroke={chartColors.axis}
                      fontSize={11}
                      fontFamily="JetBrains Mono"
                    />
                    <YAxis
                      stroke={chartColors.axis}
                      fontSize={11}
                      unit="s"
                      width={40}
                    />
                    <Tooltip content={<ChartTooltip />} />
                    <Line
                      type="monotone"
                      dataKey="duration"
                      name="duration (s)"
                      stroke={chartColors.accent}
                      strokeWidth={2}
                      dot={{ r: 3, fill: chartColors.accent }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section>
              <h2 className="mb-3 font-mono text-xs uppercase tracking-wider text-text-dim">
                Pass / fail by build
              </h2>
              <div className="h-48 rounded-lg border border-border bg-surface p-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={outcomeData}>
                    <CartesianGrid stroke={chartColors.grid} vertical={false} />
                    <XAxis
                      dataKey="label"
                      stroke={chartColors.axis}
                      fontSize={11}
                      fontFamily="JetBrains Mono"
                    />
                    <YAxis stroke={chartColors.axis} fontSize={11} width={40} domain={[0, 1]} ticks={[0, 1]} />
                    <Tooltip content={<ChartTooltip />} />
                    <Bar dataKey="outcome" name="passed">
                      {outcomeData.map((entry) => (
                        <Cell
                          key={entry.label}
                          fill={
                            entry.conclusion === 'success'
                              ? chartColors.success
                              : chartColors.failure
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section>
              <h2 className="mb-3 font-mono text-xs uppercase tracking-wider text-text-dim">
                Build history
              </h2>
              <BuildTimeline runs={runs} />
            </section>
          </>
        )}
      </main>
    </div>
  )
}
