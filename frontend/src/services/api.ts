import axios from 'axios'
import type { FailureAnalysis, Repo, RepoMetrics, WorkflowRun } from './types'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

export async function fetchRepos(): Promise<Repo[]> {
  const res = await client.get<Repo[]>('/repos')
  return res.data
}

export async function fetchRepoMetrics(repoId: string): Promise<RepoMetrics> {
  const res = await client.get<RepoMetrics>(`/repos/${repoId}/metrics`)
  return res.data
}

export async function fetchRepoRuns(repoId: string): Promise<WorkflowRun[]> {
  const res = await client.get<WorkflowRun[]>(`/repos/${repoId}/runs`)
  return res.data
}

export async function fetchRun(runId: string): Promise<WorkflowRun> {
  const res = await client.get<WorkflowRun>(`/runs/${runId}`)
  return res.data
}

export async function fetchRunAnalysis(runId: string): Promise<FailureAnalysis | null> {
  try {
    const res = await client.get<FailureAnalysis>(`/runs/${runId}/analysis`)
    return res.data
  } catch (err) {
    // 404 is expected, not an error: analysis is generated in a background task after the
    // failure webhook, so it legitimately doesn't exist yet for a just-failed run.
    if (axios.isAxiosError(err) && err.response?.status === 404) return null
    throw err
  }
}
