import { useEffect, useState } from 'react'
import { RepoCard } from '../components/RepoCard'
import { fetchRepoMetrics, fetchRepos } from '../services/api'
import type { Repo, RepoMetrics } from '../services/types'

export function Dashboard() {
  const [repos, setRepos] = useState<Repo[] | null>(null)
  const [metricsByRepo, setMetricsByRepo] = useState<Record<string, RepoMetrics>>({})
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchRepos()
      .then(async (repoList) => {
        setRepos(repoList)
        const entries = await Promise.all(
          repoList.map(async (repo) => {
            const metrics = await fetchRepoMetrics(repo.id).catch(() => null)
            return [repo.id, metrics] as const
          }),
        )
        const map: Record<string, RepoMetrics> = {}
        for (const [id, metrics] of entries) {
          if (metrics) map[id] = metrics
        }
        setMetricsByRepo(map)
      })
      .catch(() => setError('Could not reach the BuildBoard backend. Is it running?'))
  }, [])

  return (
    <div className="min-h-screen bg-bg text-text">
      <header className="border-b border-border px-8 py-5">
        <h1 className="text-lg font-semibold">BuildBoard</h1>
      </header>

      <main className="mx-auto max-w-3xl space-y-3 px-8 py-8">
        {error && (
          <div className="rounded-lg border border-failure/30 bg-failure-muted p-4 text-sm text-failure">
            {error}
          </div>
        )}

        {!error && repos === null && (
          <div className="space-y-3">
            {[0, 1, 2].map((i) => (
              <div key={i} className="h-24 animate-pulse rounded-lg border border-border bg-surface" />
            ))}
          </div>
        )}

        {!error && repos !== null && repos.length === 0 && (
          <div className="rounded-lg border border-border bg-surface p-8 text-center">
            <p className="text-text">No repos yet</p>
            <p className="mt-1 text-sm text-text-muted">
              Connect a GitHub repo's webhook to start tracking builds.
            </p>
          </div>
        )}

        {repos?.map((repo) => (
          <RepoCard key={repo.id} repo={repo} metrics={metricsByRepo[repo.id] ?? null} />
        ))}
      </main>
    </div>
  )
}
