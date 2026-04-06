import type { DashboardStats } from "@/lib/types"

interface StatCardProps {
  label: string
  value: number
  subtitle: string
  color: string
  borderColor: string
}

function StatCard({ label, value, subtitle, color, borderColor }: StatCardProps) {
  return (
    <div
      className="flex-1 rounded-lg p-5 border-l-4"
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
      <div className="text-xs text-[var(--text-secondary)] mt-1">{subtitle}</div>
      {/* Sparkline placeholder */}
      <div className="mt-3 h-8 rounded opacity-20" style={{ background: color }} />
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
      />
      <StatCard
        label="Flagged"
        value={stats.flagged}
        subtitle="Pending review"
        color="var(--accent-amber)"
        borderColor="var(--accent-amber)"
      />
      <StatCard
        label="Rejected"
        value={stats.rejected}
        subtitle="Blocked"
        color="var(--accent-red)"
        borderColor="var(--accent-red)"
      />
      <StatCard
        label="Approved"
        value={stats.approved}
        subtitle="Cleared"
        color="var(--accent-green)"
        borderColor="var(--accent-green)"
      />
    </div>
  )
}
