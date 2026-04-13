"use client"

import { useEffect, useState, useCallback } from "react"
import { getAnalytics } from "@/lib/api"
import { Sidebar } from "@/components/layout/Sidebar"
import { TopBar } from "@/components/layout/TopBar"
import type { AnalyticsData } from "@/lib/types"

function StatCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div
      className="rounded-lg border p-5 flex flex-col gap-1"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="text-[10px] font-mono uppercase tracking-widest text-[var(--text-secondary)]">{label}</div>
      <div className="text-2xl font-bold text-white font-mono">{value}</div>
      {sub && <div className="text-xs font-mono text-[var(--text-secondary)]">{sub}</div>}
    </div>
  )
}

function BarRow({
  label,
  count,
  total,
  color,
}: {
  label: string
  count: number
  total: number
  color: string
}) {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0
  return (
    <div className="flex items-center gap-3">
      <div className="w-20 text-xs font-mono text-[var(--text-secondary)] shrink-0">{label}</div>
      <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background: "var(--border)" }}>
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <div className="w-10 text-xs font-mono text-right text-white">{count}</div>
      <div className="w-10 text-[10px] font-mono text-right text-[var(--text-secondary)]">{pct}%</div>
    </div>
  )
}

function TrendChart({ data }: { data: AnalyticsData["daily_trend"] }) {
  const maxTotal = Math.max(...data.map((d) => d.total), 1)
  return (
    <div
      className="rounded-lg border p-5"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="text-xs font-mono font-semibold text-white mb-4">7-Day Transaction Trend</div>
      <div className="flex items-end gap-2 h-28">
        {data.map((d) => {
          const approvedH = Math.round((d.approved / maxTotal) * 100)
          const reviewH   = Math.round((d.review   / maxTotal) * 100)
          const rejectedH = Math.round((d.rejected / maxTotal) * 100)
          const label = d.date.slice(5) // MM-DD
          return (
            <div key={d.date} className="flex-1 flex flex-col items-center gap-1">
              <div className="w-full flex flex-col justify-end gap-0.5" style={{ height: 96 }}>
                {d.rejected > 0 && (
                  <div
                    className="w-full rounded-sm"
                    style={{ height: `${rejectedH}%`, background: "var(--accent-red)", opacity: 0.85 }}
                    title={`Rejected: ${d.rejected}`}
                  />
                )}
                {d.review > 0 && (
                  <div
                    className="w-full rounded-sm"
                    style={{ height: `${reviewH}%`, background: "var(--accent-amber)", opacity: 0.85 }}
                    title={`Review: ${d.review}`}
                  />
                )}
                {d.approved > 0 && (
                  <div
                    className="w-full rounded-sm"
                    style={{ height: `${approvedH}%`, background: "var(--accent-green)", opacity: 0.85 }}
                    title={`Approved: ${d.approved}`}
                  />
                )}
                {d.total === 0 && (
                  <div className="w-full h-0.5 rounded-sm" style={{ background: "var(--border)" }} />
                )}
              </div>
              <div className="text-[9px] font-mono text-[var(--text-secondary)]">{label}</div>
            </div>
          )
        })}
      </div>
      <div className="flex items-center gap-4 mt-3">
        {[
          { label: "Approved", color: "var(--accent-green)" },
          { label: "Review",   color: "var(--accent-amber)" },
          { label: "Rejected", color: "var(--accent-red)" },
        ].map(({ label, color }) => (
          <div key={label} className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-sm" style={{ background: color }} />
            <span className="text-[10px] font-mono text-[var(--text-secondary)]">{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function AnalyticsPage() {
  const [data, setData]     = useState<AnalyticsData | null>(null)
  const [error, setError]   = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    try {
      const d = await getAnalytics()
      setData(d)
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load analytics")
    } finally {
      setLoading((prev) => (prev ? false : prev))
    }
  }, [])

  useEffect(() => {
    fetchData()
    const id = setInterval(fetchData, 15000)
    return () => clearInterval(id)
  }, [fetchData])

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <span className="text-[var(--text-secondary)] font-mono text-sm animate-pulse">Loading...</span>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="flex h-screen items-center justify-center">
        <span className="text-[var(--accent-red)] font-mono text-sm">{error ?? "No data"}</span>
      </div>
    )
  }

  const { verdict_breakdown: vb, avg_scores: avg, top_flags, daily_trend } = data

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <TopBar title="Analytics" />
        <main className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">

          {/* Top stats */}
          <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-5 gap-4">
            <StatCard label="Total Analysed"   value={vb.total} />
            <StatCard label="Approved"          value={vb.approved} />
            <StatCard label="Under Review"      value={vb.review} />
            <StatCard label="Rejected"          value={vb.rejected} />
            <StatCard label="Fraud Rate"        value={`${vb.fraud_rate}%`} />
          </div>

          {/* Middle row: verdict breakdown + avg scores */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Verdict breakdown */}
            <div
              className="rounded-lg border p-5 flex flex-col gap-4"
              style={{ background: "var(--surface)", borderColor: "var(--border)" }}
            >
              <div className="text-xs font-mono font-semibold text-white">Verdict Breakdown</div>
              <BarRow label="APPROVED" count={vb.approved} total={vb.total} color="var(--accent-green)" />
              <BarRow label="REVIEW"   count={vb.review}   total={vb.total} color="var(--accent-amber)" />
              <BarRow label="REJECTED" count={vb.rejected} total={vb.total} color="var(--accent-red)"   />
            </div>

            {/* Avg scores */}
            <div
              className="rounded-lg border p-5 flex flex-col gap-4"
              style={{ background: "var(--surface)", borderColor: "var(--border)" }}
            >
              <div className="text-xs font-mono font-semibold text-white">Average Agent Scores</div>
              {[
                { label: "Detector Risk Score",       value: avg.detector_score,         color: "var(--accent-blue)",  max: 100 },
                { label: "Investigator Deviation",    value: avg.investigator_deviation,  color: "var(--accent-amber)", max: 100 },
                { label: "Decision Confidence",       value: avg.decision_confidence,     color: "var(--accent-green)", max: 100 },
              ].map(({ label, value, color, max }) => (
                <div key={label} className="flex flex-col gap-1.5">
                  <div className="flex justify-between">
                    <span className="text-xs font-mono text-[var(--text-secondary)]">{label}</span>
                    <span className="text-xs font-mono text-white font-bold">{value}</span>
                  </div>
                  <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "var(--border)" }}>
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.min((value / max) * 100, 100)}%`, background: color }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Bottom row: 7-day trend + top flags */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <TrendChart data={daily_trend} />

            {/* Top flags */}
            <div
              className="rounded-lg border p-5 flex flex-col gap-3"
              style={{ background: "var(--surface)", borderColor: "var(--border)" }}
            >
              <div className="text-xs font-mono font-semibold text-white">Top Fraud Flags</div>
              {top_flags.length === 0 ? (
                <div className="text-xs font-mono text-[var(--text-secondary)]">No flags recorded yet.</div>
              ) : (
                top_flags.map(({ flag, count }, i) => {
                  const maxCount = top_flags[0].count
                  const pct = Math.round((count / maxCount) * 100)
                  return (
                    <div key={flag} className="flex items-center gap-3">
                      <div className="w-4 text-[10px] font-mono text-[var(--text-secondary)] shrink-0">#{i + 1}</div>
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-mono text-white truncate mb-1">{flag}</div>
                        <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "var(--border)" }}>
                          <div
                            className="h-full rounded-full"
                            style={{ width: `${pct}%`, background: "var(--accent-red)", opacity: 0.8 }}
                          />
                        </div>
                      </div>
                      <div className="w-8 text-xs font-mono text-right text-white shrink-0">{count}</div>
                    </div>
                  )
                })
              )}
            </div>
          </div>

        </main>
      </div>
    </div>
  )
}
