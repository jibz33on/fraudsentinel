type Status = "APPROVED" | "REVIEW" | "REJECTED"

const styles: Record<Status, string> = {
  APPROVED: "bg-green-500/20 text-[var(--accent-green)] border border-green-500/30",
  REVIEW: "bg-amber-500/20 text-[var(--accent-amber)] border border-amber-500/30",
  REJECTED: "bg-red-500/20 text-[var(--accent-red)] border border-red-500/30",
}

export function StatusBadge({ status }: { status: Status }) {
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded-full text-xs font-mono uppercase tracking-wider ${styles[status]}`}
    >
      {status}
    </span>
  )
}
