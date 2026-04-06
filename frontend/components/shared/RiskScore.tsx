function getColor(score: number): string {
  if (score <= 30) return "var(--accent-green)"
  if (score <= 69) return "var(--accent-amber)"
  return "var(--accent-red)"
}

export function RiskScore({ score }: { score: number }) {
  const color = getColor(score)
  return (
    <div className="flex flex-col gap-1 min-w-[60px]">
      <span className="font-mono text-sm font-bold" style={{ color }}>
        {score}
      </span>
      <div className="h-1 w-full rounded-full bg-white/10">
        <div
          className="h-1 rounded-full transition-all"
          style={{ width: `${score}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}
