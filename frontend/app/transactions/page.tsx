"use client"

import { useEffect, useState, useCallback } from "react"
import { getTransactions } from "@/lib/api"
import { Sidebar } from "@/components/layout/Sidebar"
import { TopBar } from "@/components/layout/TopBar"
import { TransactionTable } from "@/components/dashboard/TransactionTable"
import type { TransactionDetail } from "@/lib/types"

const VERDICT_OPTIONS = ["All", "APPROVED", "REVIEW", "REJECTED"] as const

export default function TransactionsPage() {
  const [all, setAll] = useState<TransactionDetail[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [verdict, setVerdict] = useState<string>("All")

  const fetchData = useCallback(async () => {
    try {
      const data = await getTransactions()
      setAll(data)
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load transactions")
    } finally {
      setLoading((prev) => (prev ? false : prev))
    }
  }, [])

  useEffect(() => {
    fetchData()
    const id = setInterval(fetchData, 10000)
    return () => clearInterval(id)
  }, [fetchData])

  const filtered = all.filter((tx) => {
    const q = search.toLowerCase()
    const matchSearch =
      !q ||
      tx.transaction.merchant.toLowerCase().includes(q) ||
      tx.transaction.location.toLowerCase().includes(q)
    const txVerdict = tx.decision?.decision?.verdict ?? tx.transaction.status
    const matchVerdict = verdict === "All" || txVerdict === verdict
    return matchSearch && matchVerdict
  })

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
        <TopBar title="Transactions" />
        <main className="flex flex-col flex-1 overflow-y-auto p-6 gap-4">
          {/* Filter bar */}
          <div className="flex items-center gap-3">
            <input
              type="text"
              placeholder="Search merchant or location..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex-1 px-3 py-2 rounded-lg text-xs font-mono border bg-transparent text-white placeholder:text-[var(--text-secondary)] focus:outline-none focus:border-white/30"
              style={{ borderColor: "var(--border)" }}
            />
            <select
              value={verdict}
              onChange={(e) => setVerdict(e.target.value)}
              className="px-3 py-2 rounded-lg text-xs font-mono border bg-[var(--surface)] text-white focus:outline-none focus:border-white/30"
              style={{ borderColor: "var(--border)" }}
            >
              {VERDICT_OPTIONS.map((v) => (
                <option key={v} value={v}>
                  {v === "All" ? "All Verdicts" : v}
                </option>
              ))}
            </select>
            <span className="text-[10px] font-mono text-[var(--text-secondary)] whitespace-nowrap">
              Showing {filtered.length} of {all.length}
            </span>
          </div>

          <TransactionTable transactions={filtered} />
        </main>
      </div>
    </div>
  )
}
