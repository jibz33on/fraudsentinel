import { AgentBadge } from "@/components/shared/AgentBadge"
import type { AgentActivityItem } from "@/lib/types"

function timeAgo(iso: string): string {
  const seconds = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  return `${Math.floor(minutes / 60)}h ago`
}

function verdictColor(message: string): string {
  if (message.startsWith("APPROVED")) return "var(--accent-green)"
  if (message.startsWith("REJECTED")) return "var(--accent-red)"
  if (message.startsWith("REVIEW")) return "var(--accent-amber)"
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
              <div className="flex items-center justify-between mb-1">
                <AgentBadge agent={item.agent} />
                <span className="text-[10px] font-mono text-[var(--text-secondary)]">
                  {timeAgo(item.timestamp)}
                </span>
              </div>
              <p
                className="text-xs mt-1 leading-relaxed font-mono"
                style={{ color: verdictColor(item.message) }}
              >
                {item.message}
              </p>
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
