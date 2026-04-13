"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { getUsers } from "@/lib/api"
import { Sidebar } from "@/components/layout/Sidebar"
import { TopBar } from "@/components/layout/TopBar"
import type { UserProfile } from "@/lib/types"

const riskColors: Record<string, string> = {
  low:    "bg-green-500/20 text-[var(--accent-green)] border-green-500/30",
  medium: "bg-amber-500/20 text-[var(--accent-amber)] border-amber-500/30",
  high:   "bg-red-500/20 text-[var(--accent-red)] border-red-500/30",
}

function RiskBadge({ profile }: { profile: string }) {
  const key = profile.toLowerCase()
  const cls = riskColors[key] ?? "bg-white/10 text-[var(--text-secondary)] border-white/20"
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-mono uppercase tracking-wider border ${cls}`}>
      {profile}
    </span>
  )
}

function UserCard({ user }: { user: UserProfile }) {
  const initials = user.name
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase()

  return (
    <Link
      href={`/user/${user.id}`}
      className="block rounded-lg border p-5 hover:border-white/20 transition-colors"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="flex items-start gap-4 mb-4">
        <div
          className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-mono font-bold shrink-0"
          style={{
            background: "var(--accent-blue)22",
            border: "1px solid var(--accent-blue)44",
            color: "var(--accent-blue)",
          }}
        >
          {initials}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-white font-semibold text-sm truncate">{user.name}</div>
          <div className="text-[var(--text-secondary)] text-xs font-mono truncate">{user.email}</div>
        </div>
        <RiskBadge profile={user.risk_profile} />
      </div>
      <div className="grid grid-cols-3 gap-3">
        <div>
          <div className="text-[10px] font-mono uppercase text-[var(--text-secondary)] mb-0.5">Avg Spend</div>
          <div className="text-white text-xs font-mono font-bold">${user.avg_spend}</div>
        </div>
        <div>
          <div className="text-[10px] font-mono uppercase text-[var(--text-secondary)] mb-0.5">Location</div>
          <div className="text-white text-xs font-mono truncate">{user.usual_location}</div>
        </div>
        <div>
          <div className="text-[10px] font-mono uppercase text-[var(--text-secondary)] mb-0.5">Account Age</div>
          <div className="text-white text-xs font-mono font-bold">{user.account_age_days}d</div>
        </div>
      </div>
    </Link>
  )
}

export default function UsersPage() {
  const [users, setUsers] = useState<UserProfile[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getUsers()
      .then(setUsers)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load users"))
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
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
            {users.map((user) => (
              <UserCard key={user.id} user={user} />
            ))}
          </div>
        </main>
      </div>
    </div>
  )
}
