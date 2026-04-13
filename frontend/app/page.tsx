"use client"

import { useEffect, useState, useCallback } from "react"
import { getStats, getTransactions, getAgentActivity } from "@/lib/api"
import { Sidebar } from "@/components/layout/Sidebar"
import { TopBar } from "@/components/layout/TopBar"
import { StatsRow } from "@/components/dashboard/StatsRow"
import { TransactionTable } from "@/components/dashboard/TransactionTable"
import { AgentActivity } from "@/components/dashboard/AgentActivity"
import type { DashboardStats, TransactionDetail, AgentActivityItem } from "@/lib/types"

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [transactions, setTransactions] = useState<TransactionDetail[]>([])
  const [activities, setActivities] = useState<AgentActivityItem[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    try {
      const [s, t, a] = await Promise.all([
        getStats(),
        getTransactions(),
        getAgentActivity(),
      ])
      setStats(s)
      setTransactions(t)
      setActivities(a)
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load dashboard")
    } finally {
      setLoading((prev) => (prev ? false : prev))
    }
  }, [])

  useEffect(() => {
    fetchData()
    const id = setInterval(fetchData, 5000)
    return () => clearInterval(id)
  }, [fetchData])

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <span className="text-[var(--text-secondary)] font-mono text-sm animate-pulse">
          Loading...
        </span>
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
        <TopBar title="Dashboard" />
        <main className="flex flex-1 overflow-hidden">
          <div className="flex flex-col flex-1 overflow-y-auto p-6 gap-6">
            {stats && <StatsRow stats={stats} />}
            <TransactionTable transactions={transactions} />
          </div>
          <div className="w-80 shrink-0 p-4 overflow-y-auto border-l border-[var(--border)]">
            <AgentActivity activities={activities} />
          </div>
        </main>
      </div>
    </div>
  )
}
