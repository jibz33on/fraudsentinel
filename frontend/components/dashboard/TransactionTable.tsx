import Link from "next/link"
import { RiskScore } from "@/components/shared/RiskScore"
import { StatusBadge } from "@/components/shared/StatusBadge"
import type { TransactionDetail } from "@/lib/types"

function Initials({ name }: { name: string }) {
  const parts = name.trim().split(" ")
  const initials = parts.map((p) => p[0]).join("").slice(0, 2).toUpperCase()
  const colors = ["#4488ff", "#00ff88", "#ff4444", "#ffbb00", "#aa44ff"]
  const color = colors[name.charCodeAt(0) % colors.length]
  return (
    <div
      className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-mono font-bold text-white shrink-0"
      style={{ backgroundColor: color + "33", border: `1px solid ${color}55`, color }}
    >
      {initials}
    </div>
  )
}

function timeAgo(iso: string): string {
  const utc = iso.endsWith("Z") ? iso : iso + "Z"
  const seconds = Math.floor((Date.now() - new Date(utc).getTime()) / 1000)
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  return `${Math.floor(minutes / 60)}h ago`
}

function getAnomalyTags(tx: TransactionDetail): string[] {
  const tags: string[] = []
  const flags = tx.decision?.detector?.flags ?? []
  flags.forEach(flag => {
    const match = flag.match(/Amount ([\d.]+)x above/)
    if (match) tags.push(`⚠ ${match[1]}x above avg`)
    if (flag.includes("High-risk merchant")) tags.push("⚠ High-risk merchant")
    if (flag.includes("High absolute amount")) tags.push("⚠ Large amount")
  })
  const summary = tx.decision?.investigator?.summary ?? ""
  if (summary.includes("new country") && !tags.some(t => t.includes("country"))) {
    tags.push("⚠ New country")
  }
  if (summary.includes("unusual hour")) tags.push("⚠ Unusual hour")
  return tags.slice(0, 2)
}

export function TransactionTable({ transactions }: { transactions: TransactionDetail[] }) {
  const sorted = transactions

  return (
    <div
      className="rounded-lg border flex flex-col"
      style={{ background: "var(--surface)", borderColor: "var(--border)", maxHeight: "520px" }}
    >
      <div className="px-5 py-4 border-b border-[var(--border)]">
        <span className="text-sm font-semibold text-white">Live Transaction Feed</span>
      </div>
        <div className="overflow-y-auto flex-1">
        <table className="w-full text-sm">
        <thead>
          <tr className="text-[10px] font-mono uppercase tracking-wider text-[var(--text-secondary)] border-b border-[var(--border)]">
            <th className="text-left px-5 py-3">User</th>
            <th className="text-left px-5 py-3">Amount</th>
            <th className="text-left px-5 py-3">Location / Time</th>
            <th className="text-left px-5 py-3">Risk Score</th>
            <th className="text-left px-5 py-3">Status</th>
            <th className="px-5 py-3" />
          </tr>
        </thead>
        <tbody>
          {sorted.map((tx) => {
            const name = tx.transaction.user_name
            const riskScore = tx.decision?.detector?.risk_score ?? 0
            const verdict = (tx.decision?.decision?.verdict ?? tx.transaction.status) as "APPROVED" | "REVIEW" | "REJECTED"
            const time = tx.transaction.timestamp ?? tx.transaction.created_at ?? ""
            const isReview = verdict === "REVIEW"
            const isRejected = verdict === "REJECTED"
            const anomalyTags = getAnomalyTags(tx)

            return (
              <tr
                key={tx.transaction.id}
                className="border-b border-[var(--border)] hover:bg-white/[0.03] transition-colors"
                style={
                  isRejected
                    ? { borderLeft: "3px solid var(--accent-red)", backgroundColor: "rgba(239,68,68,0.04)" }
                    : isReview
                    ? { borderLeft: "3px solid var(--accent-amber)", backgroundColor: "rgba(245,158,11,0.04)" }
                    : { borderLeft: "3px solid transparent" }
                }
              >
                <td className="px-5 py-3">
                  <div className="flex items-center gap-3">
                    <Initials name={name} />
                    <div>
                      <div className="text-white text-xs font-medium">{name}</div>
                      <div className="text-[var(--text-secondary)] text-[10px] font-mono">
                        {tx.transaction.merchant}
                      </div>
                      {anomalyTags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {anomalyTags.map((tag, i) => (
                            <span
                              key={i}
                              className="text-[9px] font-mono px-1.5 py-0.5 rounded"
                              style={{
                                background: "rgba(245,158,11,0.1)",
                                color: "var(--accent-amber)",
                                border: "1px solid rgba(245,158,11,0.2)",
                              }}
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-5 py-3 font-mono font-bold text-white">
                  {tx.transaction.currency} {tx.transaction.amount.toLocaleString()}
                </td>
                <td className="px-5 py-3">
                  <div className="text-xs text-[var(--text-secondary)]">
                    📍 {tx.transaction.location}
                  </div>
                  <div className="text-[10px] font-mono text-[var(--text-secondary)]">
                    {timeAgo(time)}
                  </div>
                </td>
                <td className="px-5 py-3">
                  <RiskScore score={riskScore} />
                </td>
                <td className="px-5 py-3">
                  <StatusBadge status={verdict} />
                </td>
                <td className="px-5 py-3">
                  <Link
                    href={`/transaction/${tx.transaction.id}`}
                    className="text-[10px] font-mono uppercase tracking-wider px-3 py-1 rounded border border-[var(--border)] text-[var(--text-secondary)] hover:text-white hover:border-white/30 transition-colors"
                  >
                    VIEW
                  </Link>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
        </div>
    </div>
  )
}
