type Agent = "DETECTOR" | "INVESTIGATOR" | "DECISION"

const styles: Record<Agent, string> = {
  DETECTOR: "bg-blue-500/20 text-[var(--accent-blue)] border border-blue-500/30",
  INVESTIGATOR: "bg-purple-500/20 text-purple-400 border border-purple-500/30",
  DECISION: "bg-red-500/20 text-[var(--accent-red)] border border-red-500/30",
}

export function AgentBadge({ agent }: { agent: Agent }) {
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded-full text-xs font-mono uppercase tracking-wider ${styles[agent]}`}
    >
      {agent}
    </span>
  )
}
