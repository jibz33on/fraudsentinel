import type { Transaction } from "@/lib/types"

interface UserBehavior {
  avgSpend: number
  usualLocation: string
  accountAgeDays: number
}

interface Props {
  tx: Transaction
  userBehavior?: UserBehavior
}

function AnomalyBanner({ tx, userBehavior }: { tx: Transaction; userBehavior?: UserBehavior }) {
  if (!userBehavior) return null

  const anomalies: string[] = []

  if (userBehavior.avgSpend > 0) {
    const ratio = tx.amount / userBehavior.avgSpend
    if (ratio >= 2) {
      anomalies.push(`Amount is ${ratio.toFixed(1)}x above average spend ($${userBehavior.avgSpend})`)
    }
  }

  if (userBehavior.usualLocation && tx.location &&
      userBehavior.usualLocation.toLowerCase() !== "unknown") {
    const usualCity = userBehavior.usualLocation.toLowerCase().split(",")[0].trim()
    const usualCountry = userBehavior.usualLocation.toLowerCase().split(",").pop()?.trim() ?? ""
    const txLoc = tx.location.toLowerCase().trim()
    const isKnownLocation =
      txLoc.includes(usualCity) ||
      txLoc.includes(usualCountry) ||
      usualCountry.includes(txLoc)   // catches "IN" ⊂ "india"
    if (!isKnownLocation) {
      anomalies.push(`New location — usual: ${userBehavior.usualLocation}`)
    }
  }

  if (anomalies.length === 0) return null

  return (
    <div
      className="rounded-lg border p-4 mb-4"
      style={{
        background: "rgba(239,68,68,0.05)",
        borderColor: "rgba(239,68,68,0.3)",
      }}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="text-[var(--accent-red)] text-sm font-bold">⚠</span>
        <span className="text-xs font-mono uppercase tracking-widest text-[var(--accent-red)] font-bold">
          {anomalies.length > 1 ? "Anomalies" : "Anomaly"} Detected
        </span>
      </div>
      <ul className="flex flex-col gap-1">
        {anomalies.map((a, i) => (
          <li key={i} className="text-xs text-[var(--accent-red)] flex gap-2">
            <span className="shrink-0">▸</span>
            {a}
          </li>
        ))}
      </ul>
    </div>
  )
}

export function TransactionCard({ tx, userBehavior }: Props) {
  return (
    <div
      className="rounded-lg border p-5"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="text-xs font-mono uppercase tracking-widest text-[var(--text-secondary)] mb-4">
        Transaction Details
      </div>

      <div className="font-mono text-4xl font-bold text-white mb-1">
        {tx.currency} {tx.amount.toLocaleString()}
      </div>
      <div className="text-xs text-[var(--text-secondary)] font-mono mb-6">{tx.id}</div>

      <AnomalyBanner tx={tx} userBehavior={userBehavior} />

      {/* Side by side comparison */}
      {userBehavior && (
        <div className="grid grid-cols-2 gap-3 mb-5">
          <div
            className="rounded-lg p-3 border"
            style={{ background: "rgba(255,255,255,0.03)", borderColor: "var(--border)" }}
          >
            <div className="text-[10px] font-mono uppercase text-[var(--accent-amber)] mb-2 tracking-widest">
              This Transaction
            </div>
            <div className="flex flex-col gap-1.5">
              <div className="text-xs font-mono text-white">${tx.amount.toLocaleString()}</div>
              <div className="text-xs font-mono text-white">📍 {tx.location}</div>
              <div className="text-xs font-mono text-white">🏪 {tx.merchant}</div>
              <div className="text-xs font-mono text-white">
                🕐 {(() => { const d = new Date(tx.timestamp.endsWith("Z") ? tx.timestamp : tx.timestamp + "Z"); return d.toLocaleString("en-GB", { hour: "2-digit", minute: "2-digit", day: "2-digit", month: "short", timeZone: "UTC" }) + " UTC" })()}
              </div>
            </div>
          </div>
          <div
            className="rounded-lg p-3 border"
            style={{ background: "rgba(255,255,255,0.03)", borderColor: "var(--border)" }}
          >
            <div className="text-[10px] font-mono uppercase text-[var(--accent-green)] mb-2 tracking-widest">
              {tx.user_name}'s Baseline
            </div>
            <div className="flex flex-col gap-1.5">
              <div className="text-xs font-mono text-[var(--text-secondary)]">
                Avg: ${userBehavior.avgSpend}
              </div>
              <div className="text-xs font-mono text-[var(--text-secondary)]">
                📍 {userBehavior.usualLocation}
              </div>
              <div className="text-xs font-mono text-[var(--text-secondary)]">
                Account age: {userBehavior.accountAgeDays}d
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Basic fields */}
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="text-[10px] font-mono uppercase text-[var(--text-secondary)] mb-1">User</div>
          <div className="text-white text-sm font-mono">{tx.user_name}</div>
        </div>
        <div>
          <div className="text-[10px] font-mono uppercase text-[var(--text-secondary)] mb-1">Merchant</div>
          <div className="text-white text-sm font-mono">{tx.merchant}</div>
        </div>
      </div>
    </div>
  )
}
