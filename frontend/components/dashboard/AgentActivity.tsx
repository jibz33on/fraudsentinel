import { AgentBadge } from "@/components/shared/AgentBadge"
import type { AgentActivityItem } from "@/lib/types"

function timeAgo(iso: string): string {
  const utc = iso.endsWith("Z") ? iso : iso + "Z"
  const seconds = Math.floor((Date.now() - new Date(utc).getTime()) / 1000)
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}d ago`
  const weeks = Math.floor(days / 7)
  if (weeks < 5) return `${weeks}w ago`
  return `${Math.floor(weeks / 4)}mo ago`
}

function verdictColor(verdict: string): string {
  if (verdict === "APPROVED") return "var(--accent-green)"
  if (verdict === "REJECTED") return "var(--accent-red)"
  if (verdict === "REVIEW")   return "var(--accent-amber)"
  return "var(--text-secondary)"
}

export function AgentActivity({ activities }: { activities: AgentActivityItem[] }) {
  return (
    <div
      className="flex flex-col h-full rounded-lg border overflow-hidden"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="flex items-center justify-between px-4 py-4 border-b border-[var(--border)]">
        <span className="text-sm font-semibold text-white">Agent Activity</span>
        <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full bg-green-500/10 text-[var(--accent-green)] border border-green-500/20 flex items-center gap-1">
          <span className="w-1 h-1 rounded-full bg-[var(--accent-green)] animate-pulse inline-block" />
          Live
        </span>
      </div>

      <div className="flex flex-col overflow-y-auto flex-1">
        {activities.map((item, i) => (
          <div key={item.id}>
            <div className="px-4 py-3">

              {/* Top row: badge + timestamp */}
              <div className="flex items-center justify-between mb-1.5">
                <AgentBadge agent={item.agent} />
                <span className="text-[10px] font-mono text-[var(--text-secondary)]">
                  {timeAgo(item.timestamp)}
                </span>
              </div>

              {/* User + merchant */}
              <p className="text-xs text-[var(--text-secondary)] mb-1">
                {item.user_name}
                <span className="mx-1 opacity-40">·</span>
                {item.merchant}
              </p>

              {/* Verdict + agent-specific metric */}
              <div className="flex items-center gap-2 flex-wrap">
                <span
                  className="text-xs font-mono font-semibold"
                  style={{ color: verdictColor(item.verdict) }}
                >
                  {item.verdict}
                </span>
                {item.agent === "DETECTOR" && item.score != null && (
                  <span className="text-[10px] font-mono text-[var(--text-secondary)]">
                    score: {item.score}
                  </span>
                )}
                {item.agent === "INVESTIGATOR" && item.deviation != null && (
                  <span className="text-[10px] font-mono text-[var(--text-secondary)]">
                    deviation: {item.deviation}
                  </span>
                )}
                {item.agent === "DECISION" && item.confidence != null && (
                  <span className="text-[10px] font-mono text-[var(--text-secondary)]">
                    {item.confidence}% confidence
                  </span>
                )}
              </div>

              {/* Detail line */}
              {item.detail && (
                <p className="text-[10px] text-[var(--text-secondary)] mt-0.5 truncate">
                  {item.detail}
                </p>
              )}

            </div>
            {i < activities.length - 1 && (
              <div className="border-b border-[var(--border)]" />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}