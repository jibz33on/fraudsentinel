import { getStats, getTransactions, getAgentActivity } from "@/lib/api"
import { Sidebar } from "@/components/layout/Sidebar"
import { TopBar } from "@/components/layout/TopBar"
import { StatsRow } from "@/components/dashboard/StatsRow"
import { TransactionTable } from "@/components/dashboard/TransactionTable"
import { AgentActivity } from "@/components/dashboard/AgentActivity"

export const dynamic = "force-dynamic"

export default async function DashboardPage() {
  const [stats, transactions, activities] = await Promise.all([
    getStats(),
    getTransactions(),
    getAgentActivity(),
  ])

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <TopBar title="Dashboard" />
        <main className="flex flex-1 overflow-hidden">
          <div className="flex flex-col flex-1 overflow-y-auto p-6 gap-6">
            <StatsRow stats={stats} />
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
