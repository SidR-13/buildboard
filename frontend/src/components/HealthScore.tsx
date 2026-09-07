function scoreColor(score: number | null) {
  if (score === null) return { text: 'text-text-dim', bg: 'bg-neutral-muted' }
  if (score >= 90) return { text: 'text-success', bg: 'bg-success-muted' }
  if (score >= 70) return { text: 'text-warning', bg: 'bg-warning-muted' }
  return { text: 'text-failure', bg: 'bg-failure-muted' }
}

export function HealthScore({ score }: { score: number | null }) {
  const { text, bg } = scoreColor(score)
  return (
    <div className={`flex h-11 w-11 items-center justify-center rounded-full ${bg}`}>
      <span className={`font-mono text-sm font-semibold ${text}`}>
        {/* "—" not 0: preserves the backend's no-data-vs-unhealthy distinction */}
        {score === null ? '—' : Math.round(score)}
      </span>
    </div>
  )
}
