"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useEffect, useState } from "react"
import { getAgentStatus } from "@/lib/api"
import type { AgentStatus } from "@/lib/types"

const NAV_ITEMS = [
  { label: "Dashboard", href: "/" },
  { label: "Transactions", href: "/transactions" },
  { label: "Users", href: "/users" },
  { label: "Analytics", href: "/analytics" },
  { label: "Settings", href: "/settings" },
]

const AGENTS: Array<{ key: keyof AgentStatus; label: string }> = [
  { key: "detector", label: "DETECTOR" },
  { key: "investigator", label: "INVESTIGATOR" },
  { key: "decision", label: "DECISION" },
]

export function Sidebar() {
  const pathname = usePathname()
  const [agentStatus, setAgentStatus] = useState<AgentStatus>({
    detector: "offline",
    investigator: "offline",
    decision: "offline",
  })

  useEffect(() => {
    async function fetchStatus() {
      const status = await getAgentStatus()
      setAgentStatus(status)
    }
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <aside
      className="flex flex-col h-screen sticky top-0 shrink-0"
      style={{
        width: 240,
        background: "var(--surface)",
        borderRight: "1px solid var(--border)",
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-2 px-5 py-5 border-b border-[var(--border)]">
        <span className="text-xl">🛡️</span>
        <div>
          <div className="font-bold text-sm text-white tracking-wide">
            FraudSentinel
          </div>
          <div className="text-[10px] text-[var(--text-secondary)] font-mono uppercase tracking-widest">
            AI Fraud Detection
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 px-3 py-4 flex-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                active
                  ? "text-[var(--accent-green)] border-l-2 border-[var(--accent-green)] pl-[10px]"
                  : "text-[var(--text-secondary)] hover:text-white hover:bg-white/5"
              }`}
            >
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* Agent Status */}
      <div className="px-4 py-4 border-t border-[var(--border)]">
        <div className="text-[10px] font-mono uppercase tracking-widest text-[var(--text-secondary)] mb-3">
          AI Agent Status
        </div>
        <div className="flex flex-col gap-2">
          {AGENTS.map(({ key, label }) => {
            const online = agentStatus[key] === "online"
            return (
              <div key={key} className="flex items-center justify-between">
                <span className="text-xs font-mono text-[var(--text-secondary)]">
                  {label}
                </span>
                <div className="flex items-center gap-1.5">
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      online ? "bg-[var(--accent-green)] animate-pulse" : "bg-gray-600"
                    }`}
                  />
                  <span
                    className={`text-[10px] font-mono uppercase ${
                      online ? "text-[var(--accent-green)]" : "text-gray-600"
                    }`}
                  >
                    {online ? "ONLINE" : "OFFLINE"}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </aside>
  )
}
