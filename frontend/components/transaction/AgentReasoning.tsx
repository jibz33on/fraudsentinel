"use client"

import { useState } from "react"
import { AgentBadge } from "@/components/shared/AgentBadge"
import { RiskScore } from "@/components/shared/RiskScore"
import { StatusBadge } from "@/components/shared/StatusBadge"
import { approveTransaction, rejectTransaction } from "@/lib/api"
import type { AgentDecision } from "@/lib/types"

export function AgentReasoning({ decision }: { decision: AgentDecision }) {
  const [busy, setBusy] = useState<string | null>(null)
  const [done, setDone] = useState<string | null>(null)

  async function handleApprove() {
    setBusy("approve")
    try {
      await approveTransaction(decision.transaction_id)
      setDone("approve")
    } finally {
      setBusy(null)
    }
  }

  async function handleReject() {
    setBusy("reject")
    try {
      await rejectTransaction(decision.transaction_id)
      setDone("reject")
    } finally {
      setBusy(null)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {/* DETECTOR */}
      <div
        className="rounded-lg border p-4"
        style={{ background: "var(--surface)", borderColor: "var(--border)" }}
      >
        <div className="flex items-center gap-2 mb-3">
          <AgentBadge agent="DETECTOR" />
        </div>
        <RiskScore score={decision.detector.risk_score} />
        <ul className="mt-3 flex flex-col gap-1">
          {decision.detector.flags.map((flag, i) => (
            <li key={i} className="text-xs text-[var(--text-secondary)] flex gap-2">
              <span className="text-[var(--accent-red)] shrink-0">▸</span>
              {flag}
            </li>
          ))}
        </ul>
      </div>

      {/* INVESTIGATOR */}
      <div
        className="rounded-lg border p-4"
        style={{ background: "var(--surface)", borderColor: "var(--border)" }}
      >
        <div className="flex items-center justify-between mb-3">
          <AgentBadge agent="INVESTIGATOR" />
          <span className="text-xs font-mono text-[var(--text-secondary)]">
            deviation:{" "}
            <span className="text-[var(--accent-amber)]">
              {decision.investigator.deviation_score}
            </span>
          </span>
        </div>
        <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
          {decision.investigator.summary}
        </p>
      </div>

      {/* DECISION */}
      <div
        className="rounded-lg border p-4"
        style={{ background: "var(--surface)", borderColor: "var(--border)" }}
      >
        <div className="flex items-center justify-between mb-3">
          <AgentBadge agent="DECISION" />
          <StatusBadge status={decision.decision.verdict} />
        </div>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[10px] font-mono text-[var(--text-secondary)] uppercase">
            Confidence
          </span>
          <span className="text-[var(--accent-green)] font-mono text-sm font-bold">
            {decision.decision.confidence}%
          </span>
        </div>
        <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
          {decision.decision.reason}
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mt-2">
        <button
          onClick={handleApprove}
          disabled={busy !== null || done !== null}
          className="flex-1 py-2 rounded text-xs font-mono uppercase tracking-wider font-bold bg-green-500/20 text-[var(--accent-green)] border border-green-500/30 hover:bg-green-500/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {busy === "approve" ? "Approving..." : done === "approve" ? "✓ Approved" : "Approve"}
        </button>
        <button
          onClick={handleReject}
          disabled={busy !== null || done !== null}
          className="flex-1 py-2 rounded text-xs font-mono uppercase tracking-wider font-bold bg-red-500/20 text-[var(--accent-red)] border border-red-500/30 hover:bg-red-500/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {busy === "reject" ? "Rejecting..." : done === "reject" ? "✓ Rejected" : "Reject"}
        </button>
        <button className="flex-1 py-2 rounded text-xs font-mono uppercase tracking-wider font-bold bg-amber-500/20 text-[var(--accent-amber)] border border-amber-500/30 hover:bg-amber-500/30 transition-colors">
          Escalate
        </button>
      </div>
    </div>
  )
}
