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
    avgSpend:       user.avg_spend,
    usualLocation:  user.usual_location,
    accountAgeDays: user.account_age_days,
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <TopBar title="Transaction Detail" />
        <main className="flex flex-1 overflow-y-auto p-6 gap-6">
          {/* Left column */}
          <div className="flex flex-col gap-4 flex-1">
            <TransactionCard tx={tx} />
            {/* User Behavior Card */}
            <div
              className="rounded-lg border p-5"
              style={{ background: "var(--surface)", borderColor: "var(--border)" }}
            >
              <div className="text-xs font-mono uppercase tracking-widest text-[var(--text-secondary)] mb-4">
                User Behavior Baseline
              </div>
              <div className="grid grid-cols-3 gap-4">
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
                    Account Age
                  </div>
                  <div className="font-mono text-white font-bold">
                    {userBehavior.accountAgeDays}d
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
