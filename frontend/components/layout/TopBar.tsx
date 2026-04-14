"use client"

import { useEffect, useState } from "react"

export function TopBar({ title }: { title: string }) {
  const [time, setTime] = useState("")

  useEffect(() => {
    function update() {
      setTime(new Date().toLocaleTimeString("en-GB", { hour12: false }))
    }
    update()
    const interval = setInterval(update, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <header
      className="flex items-center justify-between px-6 py-4 border-b"
      style={{
        background: "var(--surface)",
        borderColor: "var(--border)",
      }}
    >
      <h1 className="text-lg font-semibold text-white">{title}</h1>

      <div className="flex items-center gap-4">
        <div className="text-xs font-mono text-[var(--text-secondary)]">
          <span className="text-white">{time}</span>
          <span className="ml-1 text-[var(--text-secondary)]">IST</span>
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-500/10 border border-green-500/20">
          <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-green)] animate-pulse" />
          <span className="text-[10px] font-mono uppercase tracking-wider text-[var(--accent-green)]">
            System Live
          </span>
        </div>

        <button className="text-[var(--text-secondary)] hover:text-white transition-colors text-lg">
          🔔
        </button>
      </div>
    </header>
  )
}
