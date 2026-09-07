export interface Repo {
  id: string
  owner: string
  name: string
  full_name: string
  created_at: string
}

export interface WorkflowRun {
  id: string
  workflow_name: string
  branch: string
  commit_sha: string
  status: string
  conclusion: string | null
  started_at: string | null
  completed_at: string | null
  duration_seconds: number | null
}

export interface FailureAnalysis {
  id: string
  run_id: string
  logs_snippet: string
  claude_analysis: string
  suggested_fix: string | null
  created_at: string
}

export interface RepoMetrics {
  health_score: number | null
  pass_rate: number | null
  total_runs: number
  successful_runs: number
  avg_duration_seconds: number | null
  flaky_count: number
  flaky_commits: { branch: string; commit_sha: string }[]
}
