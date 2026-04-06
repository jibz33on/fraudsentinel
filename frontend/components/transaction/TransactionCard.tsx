import type { Transaction } from "@/lib/types"

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-[10px] font-mono uppercase tracking-widest text-[var(--text-secondary)] mb-1">
        {label}
      </div>
      <div className="text-white text-sm font-mono">{value}</div>
    </div>
  )
}

export function TransactionCard({ tx }: { tx: Transaction }) {
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
      <div className="grid grid-cols-2 gap-4 text-sm">
        <Field label="User" value={tx.user_name} />
        <Field label="Merchant" value={tx.merchant} />
        <Field label="Location" value={`📍 ${tx.location}`} />
        <Field label="Time" value={new Date(tx.timestamp).toLocaleString()} />
      </div>
    </div>
  )
}
