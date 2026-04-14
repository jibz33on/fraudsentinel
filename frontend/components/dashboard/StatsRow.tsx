import type { DashboardStats } from "@/lib/types"

interface StatCardProps {
  label: string
  value: number
  subtitle: string
  color: string
  borderColor: string
  total: number
}

function StatCard({ label, value, subtitle, color, borderColor, total }: StatCardProps) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0

  return (
    <div
      className="flex-1 rounded-lg p-5 border-l-4 transition-all duration-200 hover:brightness-110"
      style={{
        background: "var(--surface)",
        borderColor,
        borderTop: "1px solid var(--border)",
        borderRight: "1px solid var(--border)",
        borderBottom: "1px solid var(--border)",
      }}
    >
      <div className="text-xs font-mono uppercase tracking-widest text-[var(--text-secondary)] mb-2">
        {label}
      </div>

      <div className="font-mono text-3xl font-bold" style={{ color }}>
        {value.toLocaleString()}
      </div>

      <div className="flex items-center justify-between mt-1">
        <span className="text-xs text-[var(--text-secondary)]">{subtitle}</span>
        {pct > 0 && (
          <span className="text-xs font-mono" style={{ color }}>
            {pct}%
          </span>
        )}
      </div>

      {/* Progress bar */}
      <div className="mt-3 h-1 rounded-full overflow-hidden" style={{ background: "var(--border)" }}>
        <div
          className="h-full rounded-full"
          style={{
            width: `${pct}%`,
            background: color,
            transition: "width 1s cubic-bezier(0.4, 0, 0.2, 1)",
            boxShadow: `0 0 6px ${color}`,
          }}
        />
      </div>
    </div>
  )
}

export function StatsRow({ stats }: { stats: DashboardStats }) {
  return (
    <div className="flex gap-4">
      <StatCard
        label="Total Transactions"
        value={stats.total}
        subtitle="All time"
        color="var(--text-primary)"
        borderColor="var(--border)"
        total={stats.total}
      />
      <StatCard
        label="Flagged"
        value={stats.flagged}
        subtitle="Pending review"
        color="var(--accent-amber)"
        borderColor="var(--accent-amber)"
        total={stats.total}
      />
      <StatCard
        label="Rejected"
        value={stats.rejected}
        subtitle="Blocked"
        color="var(--accent-red)"
        borderColor="var(--accent-red)"
        total={stats.total}
      />
      <StatCard
        label="Approved"
        value={stats.approved}
        subtitle="Cleared"
        color="var(--accent-green)"
        borderColor="var(--accent-green)"
        total={stats.total}
      />
    </div>
  )
}