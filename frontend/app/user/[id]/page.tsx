import { getUser } from "@/lib/api"
import { Sidebar } from "@/components/layout/Sidebar"
import { TopBar } from "@/components/layout/TopBar"

export const dynamic = "force-dynamic"

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <div className="text-[10px] font-mono uppercase tracking-widest text-[var(--text-secondary)] mb-1">
        {label}
      </div>
      <div className="font-mono font-bold text-white text-sm">{value}</div>
    </div>
  )
}

function BehaviorField({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-[10px] font-mono uppercase tracking-widest text-[var(--text-secondary)] mb-1">
        {label}
      </div>
      <div className="text-white text-sm font-mono">{value}</div>
    </div>
  )
}

export default async function UserProfilePage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  const user = await getUser(id)

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <TopBar title="User Profile" />
        <main className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
          {/* User header card */}
          <div
            className="rounded-lg border p-5 flex items-center gap-5"
            style={{ background: "var(--surface)", borderColor: "var(--border)" }}
          >
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center text-xl font-mono font-bold"
              style={{
                background: "var(--accent-blue)22",
                border: "1px solid var(--accent-blue)44",
                color: "var(--accent-blue)",
              }}
            >
              {user.name
                .split(" ")
                .map((p: string) => p[0])
                .join("")
                .slice(0, 2)
                .toUpperCase()}
            </div>
            <div className="flex-1">
              <div className="text-white font-semibold text-lg">{user.name}</div>
              <div className="text-[var(--text-secondary)] text-sm font-mono">
                {user.email}
              </div>
            </div>
            <div className="grid grid-cols-3 gap-8">
              <Stat label="Account Age" value={`${user.account_age_days}d`} />
              <Stat label="Avg Spend" value={`$${user.avg_spend}`} />
              <Stat label="Location" value={user.usual_location} />
            </div>
          </div>

          {/* Behavioral patterns */}
          <div
            className="rounded-lg border p-5"
            style={{ background: "var(--surface)", borderColor: "var(--border)" }}
          >
            <div className="text-xs font-mono uppercase tracking-widest text-[var(--text-secondary)] mb-4">
              Behavioral Patterns
            </div>
            <div className="grid grid-cols-3 gap-6">
              <BehaviorField label="Usual Hours" value={user.usual_hours} />
              <BehaviorField label="Primary Location" value={user.usual_location} />
              <BehaviorField label="Risk Profile" value={user.risk_profile} />
            </div>
          </div>

        </main>
      </div>
    </div>
  )
}
