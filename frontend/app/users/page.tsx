"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { getUsers } from "@/lib/api"
import { Sidebar } from "@/components/layout/Sidebar"
import { TopBar } from "@/components/layout/TopBar"
import type { UserProfile } from "@/lib/types"

const riskColors: Record<string, string> = {
  low:    "text-green-400 border-green-600 bg-green-900/30",
  medium: "text-amber-400 border-amber-600 bg-amber-900/30",
  high:   "text-red-400 border-red-600 bg-red-900/30",
}

function Avatar({ name }: { name: string }) {
  const initials = name.split(" ").map(p => p[0]).join("").slice(0, 2).toUpperCase()
  return (
    <div
      className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-mono font-bold shrink-0"
      style={{ background: "var(--accent-blue)22", border: "1px solid var(--accent-blue)44", color: "var(--accent-blue)" }}
    >
      {initials}
    </div>
  )
}

function RiskBadge({ profile }: { profile: string }) {
  const cls = riskColors[profile.toLowerCase()] ?? "text-gray-400 border-gray-600 bg-gray-900/30"
  return (
    <span className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${cls}`}>
      {profile}
    </span>
  )
}

export default function UsersPage() {
  const [users, setUsers] = useState<UserProfile[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getUsers()
      .then(setUsers)
      .catch(e => setError(e instanceof Error ? e.message : "Failed to load users"))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <span className="text-[var(--text-secondary)] font-mono text-sm animate-pulse">Loading...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center">
        <span className="text-[var(--accent-red)] font-mono text-sm">{error}</span>
      </div>
    )
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <TopBar title="Users" />
        <main className="flex-1 overflow-y-auto p-6">
          <div className="rounded-lg border overflow-hidden" style={{ borderColor: "var(--border)" }}>

            {/* Header */}
            <div
              className="grid grid-cols-[2fr_1fr_1fr_1.5fr_1fr_1fr_1fr_1fr] gap-4 px-5 py-3 text-[10px] font-mono uppercase tracking-widest text-[var(--text-secondary)]"
              style={{ background: "var(--surface-2, #0f0f1a)", borderBottom: "1px solid var(--border)" }}
            >
              <div>User</div>
              <div>Risk</div>
              <div>Avg Spend</div>
              <div>Location</div>
              <div>Hours</div>
              <div>Txns</div>
              <div className="text-[var(--accent-amber)]">Flagged</div>
              <div className="text-[var(--accent-red)]">Rejected</div>
            </div>

            {/* Rows */}
            {users.map((user, i) => (
              <Link
                key={user.id}
                href={`/user/${user.id}`}
                className="grid grid-cols-[2fr_1fr_1fr_1.5fr_1fr_1fr_1fr_1fr] gap-4 px-5 py-4 items-center hover:bg-white/5 transition-colors"
                style={{
                  background: "var(--surface)",
                  borderBottom: i < users.length - 1 ? "1px solid var(--border)" : "none",
                }}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <Avatar name={user.name} />
                  <div className="min-w-0">
                    <div className="text-white text-sm font-semibold truncate">{user.name}</div>
                    <div className="text-[var(--text-secondary)] text-xs font-mono truncate">{user.email}</div>
                  </div>
                </div>

                <div><RiskBadge profile={user.risk_profile} /></div>

                <div className="font-mono text-white text-sm font-bold">
                  ${user.avg_spend.toLocaleString()}
                </div>

                <div className="text-white text-xs font-mono truncate">{user.usual_location}</div>

                <div className="text-[var(--text-secondary)] text-xs font-mono">{user.usual_hours || "—"}</div>

                <div className="font-mono text-white text-sm">{user.transaction_count.toLocaleString()}</div>

                <div>
                  {(user.review_count ?? 0) > 0 ? (
                    <span className="font-mono text-sm text-[var(--accent-amber)] font-bold">{user.review_count}</span>
                  ) : (
                    <span className="font-mono text-sm text-[var(--text-secondary)]">0</span>
                  )}
                </div>

                <div>
                  {(user.rejected_count ?? 0) > 0 ? (
                    <span className="font-mono text-sm text-[var(--accent-red)] font-bold">{user.rejected_count}</span>
                  ) : (
                    <span className="font-mono text-sm text-[var(--text-secondary)]">0</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        </main>
      </div>
    </div>
  )
}
