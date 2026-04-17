import { getTransaction, getUser } from "@/lib/api"
import { Sidebar } from "@/components/layout/Sidebar"
import { TopBar } from "@/components/layout/TopBar"
import { TransactionCard } from "@/components/transaction/TransactionCard"
import { AgentReasoning } from "@/components/transaction/AgentReasoning"

export const dynamic = "force-dynamic"

export default async function TransactionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const detail = await getTransaction(id)
  const tx = detail.transaction
  const user = await getUser(tx.user_id ?? "")

  const userBehavior = {
    name:             user.name,
    email:            user.email,
    avgSpend:         user.avg_spend,
    usualLocation:    user.usual_location,
    usualHours:       user.usual_hours,
    transactionCount: user.transaction_count,
    accountAgeDays:   user.account_age_days,
    riskProfile:      user.risk_profile,
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <TopBar title="Transaction Detail" />
        <main className="flex flex-1 overflow-y-auto p-6 gap-6">
          {/* Left column */}
          <div className="flex flex-col gap-4 flex-1">
            <TransactionCard tx={tx} userBehavior={userBehavior} />
            {/* User Behavior Card */}
            <div
              className="rounded-lg border p-5"
              style={{ background: "var(--surface)", borderColor: "var(--border)" }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="text-xs font-mono uppercase tracking-widest text-[var(--text-secondary)]">
                  {userBehavior.name}&apos;s Baseline
                </div>
                <span
                  className={`text-[10px] font-mono uppercase px-2 py-0.5 rounded border ${
                    userBehavior.riskProfile === "low"
                      ? "text-green-400 border-green-600 bg-green-900/30"
                      : userBehavior.riskProfile === "high"
                      ? "text-red-400 border-red-600 bg-red-900/30"
                      : "text-amber-400 border-amber-600 bg-amber-900/30"
                  }`}
                >
                  {userBehavior.riskProfile} risk
                </span>
              </div>
              <div className="grid grid-cols-2 gap-x-6 gap-y-4">
                <div>
                  <div className="text-[10px] font-mono uppercase text-[var(--text-secondary)] mb-1">
                    Avg Spend
                  </div>
                  <div className="font-mono text-white font-bold">
                    ${userBehavior.avgSpend}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] font-mono uppercase text-[var(--text-secondary)] mb-1">
                    Usual Location
                  </div>
                  <div className="font-mono text-white text-sm">
                    {userBehavior.usualLocation}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] font-mono uppercase text-[var(--text-secondary)] mb-1">
                    Typical Hours
                  </div>
                  <div className="font-mono text-white text-sm">
                    {userBehavior.usualHours || "—"}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] font-mono uppercase text-[var(--text-secondary)] mb-1">
                    Transactions
                  </div>
                  <div className="font-mono text-white font-bold">
                    {userBehavior.transactionCount}
                  </div>
                </div>
                <div>
                  <div className="text-[10px] font-mono uppercase text-[var(--text-secondary)] mb-1">
                    Account Age
                  </div>
                  <div className="font-mono text-white font-bold">
                    {userBehavior.accountAgeDays}d
                  </div>
                </div>
                <div>
                  <div className="text-[10px] font-mono uppercase text-[var(--text-secondary)] mb-1">
                    Email
                  </div>
                  <div className="font-mono text-[var(--text-secondary)] text-xs truncate">
                    {userBehavior.email}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right column */}
          <div className="w-96 shrink-0">
            {detail.decision && <AgentReasoning decision={detail.decision} />}
          </div>
        </main>
      </div>
    </div>
  )
}
