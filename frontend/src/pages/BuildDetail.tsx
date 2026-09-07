import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchRun, fetchRunAnalysis } from '../services/api'
import type { FailureAnalysis, WorkflowRun } from '../services/types'

const conclusionStyle: Record<string, { text: string; bg: string }> = {
  success: { text: 'text-success', bg: 'bg-success-muted' },
  failure: { text: 'text-failure', bg: 'bg-failure-muted' },
}

export function BuildDetail() {
  const { runId } = useParams()
  const [run, setRun] = useState<WorkflowRun | null>(null)
  const [analysis, setAnalysis] = useState<FailureAnalysis | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!runId) return
    fetchRun(runId)
      .then((r) => {
        setRun(r)
        if (r.conclusion === 'failure') {
          fetchRunAnalysis(runId).then(setAnalysis)
        }
      })
      .catch(() => setError('Could not load this build.'))
  }, [runId])

  return (
    <div className="min-h-screen bg-bg text-text">
      <header className="border-b border-border px-8 py-5">
        <Link to="/" className="text-sm text-accent hover:underline">
          ← Dashboard
        </Link>
      </header>

      <main className="mx-auto max-w-3xl space-y-6 px-8 py-8">
        {error && (
          <div className="rounded-lg border border-failure/30 bg-failure-muted p-4 text-sm text-failure">
            {error}
          </div>
        )}

        {!error && !run && (
          <div className="h-32 animate-pulse rounded-lg border border-border bg-surface" />
        )}

        {run && (
          <>
            <section className="rounded-lg border border-border bg-surface p-5">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-mono text-sm text-text">{run.commit_sha.slice(0, 7)}</p>
                  <p className="mt-0.5 text-sm text-text-muted">
                    {run.branch} · {run.workflow_name}
                  </p>
                </div>
                {run.conclusion && (
                  <span
                    className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                      conclusionStyle[run.conclusion]?.bg ?? 'bg-neutral-muted'
                    } ${conclusionStyle[run.conclusion]?.text ?? 'text-neutral'}`}
                  >
                    {run.conclusion}
                  </span>
                )}
              </div>
              <div className="mt-4 flex gap-6 text-sm text-text-muted">
                <span>
                  Duration{' '}
                  <span className="font-mono text-text">
                    {run.duration_seconds !== null ? `${run.duration_seconds}s` : '—'}
                  </span>
                </span>
                <span>
                  Status <span className="font-mono text-text">{run.status}</span>
                </span>
              </div>
            </section>

            {run.conclusion === 'failure' && (
              <section className="space-y-3">
                <h2 className="font-mono text-xs uppercase tracking-wider text-text-dim">
                  Claude failure analysis
                </h2>

                {analysis === null && (
                  <div className="rounded-lg border border-border bg-surface p-5 text-sm text-text-muted">
                    Analysis not available yet — it runs shortly after the build fails.
                  </div>
                )}

                {analysis && (
                  <div className="space-y-4 rounded-lg border border-border bg-surface p-5">
                    <div>
                      <p className="mb-1 text-xs font-medium text-text-dim">Root cause</p>
                      <p className="text-sm text-text">{analysis.claude_analysis}</p>
                    </div>
                    {analysis.suggested_fix && (
                      <div>
                        <p className="mb-1 text-xs font-medium text-text-dim">Suggested fix</p>
                        <p className="text-sm text-text">{analysis.suggested_fix}</p>
                      </div>
                    )}
                    <div>
                      <p className="mb-1 text-xs font-medium text-text-dim">Log snippet</p>
                      <pre className="max-h-64 overflow-auto whitespace-pre-wrap rounded-md bg-bg p-3 font-mono text-xs text-text-muted">
                        {analysis.logs_snippet}
                      </pre>
                    </div>
                  </div>
                )}
              </section>
            )}
          </>
        )}
      </main>
    </div>
  )
}
