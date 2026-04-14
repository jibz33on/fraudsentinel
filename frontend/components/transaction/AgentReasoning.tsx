"use client"

import { useState } from "react"
import { AgentBadge } from "@/components/shared/AgentBadge"
import { RiskScore } from "@/components/shared/RiskScore"
import { StatusBadge } from "@/components/shared/StatusBadge"
import { approveTransaction, rejectTransaction } from "@/lib/api"
import type { AgentDecision } from "@/lib/types"

function DetectorFlags({ flags }: { flags: string[] }) {
  if (!flags || flags.length === 0) return <p className="text-sm text-gray-500">No flags triggered</p>

  const getColor = (flag: string) => {
    const f = flag.toLowerCase()
    if (f.includes("velocity") || f.includes("fraud"))   return "bg-red-900/50 text-red-300 border border-red-700"
    if (f.includes("amount") || f.includes("high"))      return "bg-orange-900/50 text-orange-300 border border-orange-700"
    if (f.includes("location") || f.includes("foreign")) return "bg-yellow-900/50 text-yellow-300 border border-yellow-700"
    if (f.includes("hour") || f.includes("time"))        return "bg-blue-900/50 text-blue-300 border border-blue-700"
    if (f.includes("new account"))                       return "bg-purple-900/50 text-purple-300 border border-purple-700"
    return "bg-gray-800 text-gray-300 border border-gray-600"
  }

  return (
    <div className="flex flex-col gap-2">
      {flags.map((flag, i) => (
        <span key={i} className={`text-xs px-2 py-1 rounded ${getColor(flag)}`}>
          ⚑ {flag}
        </span>
      ))}
    </div>
  )
}

function StructuredReason({ reason }: { reason: string }) {
  const labels = ["DECISION", "SIGNALS", "BEHAVIOUR", "ACTION", "PATTERN", "DEVIATION", "RISK"]

  const labelColors: Record<string, string> = {
    DECISION:  "text-red-400",
    SIGNALS:   "text-orange-400",
    BEHAVIOUR: "text-yellow-400",
    ACTION:    "text-blue-400",
    PATTERN:   "text-purple-400",
    DEVIATION: "text-orange-400",
    RISK:      "text-red-400",
  }

  const parts = reason.split(/\n+/).map(line => line.trim()).filter(Boolean)

  const sections: { label: string; text: string }[] = []
  for (const part of parts) {
    const match = labels.find(l => part.startsWith(l + ":"))
    if (match) {
      sections.push({ label: match, text: part.slice(match.length + 1).trim() })
    }
  }

  if (sections.length === 0) return <p className="text-sm text-gray-300">{reason}</p>

  return (
    <div className="space-y-3">
      {sections.map(({ label, text }) => (
        <div key={label}>
          <span className={`text-xs font-bold ${labelColors[label] ?? "text-gray-400"} mr-2`}>
            {label}
          </span>
          <span className="text-sm text-gray-300">{text}</span>
        </div>
      ))}
    </div>
  )
}

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
          <span className="text-xs font-mono text-[var(--text-secondary)]">①</span>
          <AgentBadge agent="DETECTOR" />
        </div>
        <RiskScore score={decision.detector.risk_score} />
        <div className="mt-3">
          <DetectorFlags flags={decision.detector.flags ?? []} />
        </div>
      </div>

      {/* INVESTIGATOR */}
      <div
        className="rounded-lg border p-4"
        style={{ background: "var(--surface)", borderColor: "var(--border)" }}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-[var(--text-secondary)]">②</span>
            <AgentBadge agent="INVESTIGATOR" />
          </div>
          <span className="text-xs font-mono text-[var(--text-secondary)]">
            deviation:{" "}
            <span className="text-[var(--accent-amber)]">
              {decision.investigator.deviation_score}
            </span>
          </span>
        </div>
        <StructuredReason reason={decision.investigator.summary ?? ""} />
      </div>

      {/* DECISION */}
      <div
        className="rounded-lg border p-4"
        style={{ background: "var(--surface)", borderColor: "var(--border)" }}
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-[var(--text-secondary)]">③</span>
            <AgentBadge agent="DECISION" />
          </div>
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
        <StructuredReason reason={decision.decision.reason ?? ""} />
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
