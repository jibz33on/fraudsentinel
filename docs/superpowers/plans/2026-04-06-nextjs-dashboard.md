# FraudSentinel Next.js Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the Google Stitch static HTML dashboard into a full Next.js 14 App Router application with dark fintech UI, mock data, and live `/health` polling.

**Architecture:** Next.js App Router with TypeScript and Tailwind. All data flows through `lib/api.ts` which has a `USE_MOCK` flag — when `true` returns hardcoded mock data, when `false` fetches from FastAPI at `localhost:8000`. Agent status (`/health`) is always fetched live. Shared UI primitives live in `components/shared/`, layout chrome in `components/layout/`, and page-specific panels in `components/dashboard/`, `components/transaction/`.

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui (badge, card, table, button, separator)

---

## File Map

| File | Responsibility |
|------|---------------|
| `frontend/lib/types.ts` | All shared TypeScript interfaces |
| `frontend/lib/api.ts` | All data fetching — mock or real, controlled by `USE_MOCK` |
| `frontend/app/layout.tsx` | Root layout: dark html, Inter font, Sidebar + TopBar shell |
| `frontend/app/globals.css` | CSS variables, dark theme tokens |
| `frontend/tailwind.config.ts` | `darkMode: "class"`, custom colors |
| `frontend/components/shared/StatusBadge.tsx` | APPROVED/REVIEW/REJECTED pill |
| `frontend/components/shared/RiskScore.tsx` | Score number + colored progress bar |
| `frontend/components/shared/AgentBadge.tsx` | DETECTOR/INVESTIGATOR/DECISION pill |
| `frontend/components/layout/Sidebar.tsx` | Left nav + agent status panel |
| `frontend/components/layout/TopBar.tsx` | Page title + SYNC clock + SYSTEM LIVE badge |
| `frontend/components/dashboard/StatsRow.tsx` | 4 stat cards |
| `frontend/components/dashboard/TransactionTable.tsx` | Live feed table |
| `frontend/components/dashboard/AgentActivity.tsx` | Right activity panel |
| `frontend/components/transaction/TransactionCard.tsx` | Transaction info card |
| `frontend/components/transaction/AgentReasoning.tsx` | 3 agent verdict cards |
| `frontend/app/page.tsx` | Main dashboard page |
| `frontend/app/transaction/[id]/page.tsx` | Transaction detail page |
| `frontend/app/user/[id]/page.tsx` | User profile page |
| `frontend/.env.local` | `NEXT_PUBLIC_API_URL=http://localhost:8000` |

---

### Task 1: Initialize Next.js App

**Files:**
- Create: `frontend/` (entire directory via CLI)

- [ ] **Step 1: Run create-next-app from the fraudsentinel root**

```bash
cd /Users/jibinkunjumon/fraudsentinel
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --no-src-dir \
  --import-alias "@/*"
```

When prompted for any remaining interactive questions, accept defaults.

Expected: `frontend/` directory created with `app/`, `public/`, `package.json`, `tailwind.config.ts`, `tsconfig.json`.

- [ ] **Step 2: Verify structure**

```bash
ls /Users/jibinkunjumon/fraudsentinel/frontend/
```

Expected output includes: `app  node_modules  package.json  tailwind.config.ts  tsconfig.json`

- [ ] **Step 3: Create .env.local**

Create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

- [ ] **Step 4: Commit**

```bash
cd /Users/jibinkunjumon/fraudsentinel
git add frontend/
git commit -m "feat: initialize Next.js 14 app with TypeScript + Tailwind"
```

---

### Task 2: Install shadcn/ui and Components

**Files:**
- Modify: `frontend/components.json` (created by shadcn init)
- Create: `frontend/components/ui/` (shadcn primitives)

- [ ] **Step 1: Initialize shadcn/ui**

```bash
cd /Users/jibinkunjumon/fraudsentinel/frontend
npx shadcn@latest init
```

When prompted:
- Style: **Default**
- Base color: **Slate**
- CSS variables: **Yes**

- [ ] **Step 2: Install required shadcn components**

```bash
cd /Users/jibinkunjumon/fraudsentinel/frontend
npx shadcn@latest add badge
npx shadcn@latest add card
npx shadcn@latest add table
npx shadcn@latest add button
npx shadcn@latest add separator
```

Expected: each command says "✔ Done" and creates files in `components/ui/`.

- [ ] **Step 3: Verify components exist**

```bash
ls /Users/jibinkunjumon/fraudsentinel/frontend/components/ui/
```

Expected: `badge.tsx  button.tsx  card.tsx  separator.tsx  table.tsx`

- [ ] **Step 4: Commit**

```bash
cd /Users/jibinkunjumon/fraudsentinel
git add frontend/
git commit -m "feat: install shadcn/ui with badge, card, table, button, separator"
```

---

### Task 3: Configure Dark Theme

**Files:**
- Modify: `frontend/tailwind.config.ts`
- Modify: `frontend/app/globals.css`
- Modify: `frontend/app/layout.tsx`

- [ ] **Step 1: Update tailwind.config.ts**

Replace the entire content of `frontend/tailwind.config.ts` with:

```typescript
import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        surface: "var(--surface)",
        border: "var(--border)",
        "accent-green": "var(--accent-green)",
        "accent-red": "var(--accent-red)",
        "accent-amber": "var(--accent-amber)",
        "accent-blue": "var(--accent-blue)",
        "text-primary": "var(--text-primary)",
        "text-secondary": "var(--text-secondary)",
      },
      fontFamily: {
        mono: ["var(--font-mono)", "monospace"],
      },
    },
  },
  plugins: [],
}

export default config
```

- [ ] **Step 2: Update globals.css**

Replace the entire content of `frontend/app/globals.css` with:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root,
.dark {
  --background: #0a0a0f;
  --surface: #12121a;
  --border: #1e1e2e;
  --accent-green: #00ff88;
  --accent-red: #ff4444;
  --accent-amber: #ffbb00;
  --accent-blue: #4488ff;
  --text-primary: #ffffff;
  --text-secondary: #8888aa;
}

body {
  background-color: var(--background);
  color: var(--text-primary);
}

* {
  border-color: var(--border);
}
```

- [ ] **Step 3: Update layout.tsx**

Replace `frontend/app/layout.tsx` with:

```typescript
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "FraudSentinel",
  description: "Multi-agent fraud detection system",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  )
}
```

- [ ] **Step 4: Commit**

```bash
cd /Users/jibinkunjumon/fraudsentinel
git add frontend/
git commit -m "feat: configure dark theme with CSS variables and Tailwind"
```

---

### Task 4: Create TypeScript Types

**Files:**
- Create: `frontend/lib/types.ts`

- [ ] **Step 1: Create lib directory and types.ts**

```bash
mkdir -p /Users/jibinkunjumon/fraudsentinel/frontend/lib
```

Create `frontend/lib/types.ts`:

```typescript
export interface Transaction {
  id: string
  user_id: string
  user_name: string
  amount: number
  currency: string
  merchant: string
  location: string
  timestamp: string
  risk_score: number
  status: "APPROVED" | "REVIEW" | "REJECTED"
}

export interface AgentDecision {
  transaction_id: string
  detector: {
    risk_score: number
    flags: string[]
  }
  investigator: {
    summary: string
    deviation_score: number
  }
  decision: {
    verdict: "APPROVED" | "REVIEW" | "REJECTED"
    confidence: number
    reason: string
  }
}

export interface DashboardStats {
  total: number
  flagged: number
  rejected: number
  approved: number
}

export interface AgentStatus {
  detector: "online" | "offline"
  investigator: "online" | "offline"
  decision: "online" | "offline"
}

export interface AgentActivityItem {
  id: string
  agent: "DETECTOR" | "INVESTIGATOR" | "DECISION"
  message: string
  timestamp: string
}

export interface UserProfile {
  id: string
  name: string
  email: string
  account_age_days: number
  avg_spend: number
  usual_location: string
  usual_hours: string
  spend_pattern: string
  transactions: Transaction[]
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/jibinkunjumon/fraudsentinel
git add frontend/lib/types.ts
git commit -m "feat: add TypeScript interfaces for all data models"
```

---

### Task 5: Create API Layer with USE_MOCK Flag

**Files:**
- Create: `frontend/lib/api.ts`

- [ ] **Step 1: Create frontend/lib/api.ts**

```typescript
import type {
  Transaction,
  AgentDecision,
  DashboardStats,
  AgentStatus,
  AgentActivityItem,
  UserProfile,
} from "./types"

const USE_MOCK = true
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// ─── Mock Data ────────────────────────────────────────────────────────────────

const MOCK_TRANSACTIONS: Transaction[] = [
  {
    id: "txn-4821",
    user_id: "usr-001",
    user_name: "Jimmy K",
    amount: 4500,
    currency: "USD",
    merchant: "Crypto Exchange XY",
    location: "Lagos, Nigeria",
    timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
    risk_score: 94,
    status: "REJECTED",
  },
  {
    id: "txn-4822",
    user_id: "usr-002",
    user_name: "Sarah M",
    amount: 890,
    currency: "GBP",
    merchant: "Amazon UK",
    location: "London, UK",
    timestamp: new Date(Date.now() - 8 * 60 * 1000).toISOString(),
    risk_score: 67,
    status: "REVIEW",
  },
  {
    id: "txn-4823",
    user_id: "usr-003",
    user_name: "Mark T",
    amount: 45,
    currency: "INR",
    merchant: "Swiggy",
    location: "Kochi, India",
    timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    risk_score: 12,
    status: "APPROVED",
  },
  {
    id: "txn-4824",
    user_id: "usr-004",
    user_name: "Priya S",
    amount: 2100,
    currency: "SGD",
    merchant: "Lazada",
    location: "Singapore",
    timestamp: new Date(Date.now() - 22 * 60 * 1000).toISOString(),
    risk_score: 78,
    status: "REVIEW",
  },
]

const MOCK_STATS: DashboardStats = {
  total: 1243,
  flagged: 12,
  rejected: 4,
  approved: 1227,
}

const MOCK_AGENT_DECISION: AgentDecision = {
  transaction_id: "txn-4821",
  detector: {
    risk_score: 94,
    flags: [
      "High-risk country: Nigeria",
      "Amount exceeds 3x user average",
      "Crypto exchange merchant",
      "Transaction at unusual hour (02:14 UTC)",
    ],
  },
  investigator: {
    summary:
      "User Jimmy K has 14 prior transactions, all under $200, predominantly in Kochi, India. This transaction is 22.5x above average spend, from a country never previously transacted in. Behavioral deviation score is extremely high.",
    deviation_score: 96,
  },
  decision: {
    verdict: "REJECTED",
    confidence: 97,
    reason:
      "Extreme behavioral deviation combined with high-risk geography and merchant category. Transaction flagged as likely fraudulent.",
  },
}

const MOCK_ACTIVITY: AgentActivityItem[] = [
  {
    id: "act-001",
    agent: "DETECTOR",
    message: "Risk score 94 — txn-4821 flagged for review",
    timestamp: new Date(Date.now() - 30 * 1000).toISOString(),
  },
  {
    id: "act-002",
    agent: "INVESTIGATOR",
    message: "Behavioral deviation 96 detected for Jimmy K",
    timestamp: new Date(Date.now() - 45 * 1000).toISOString(),
  },
  {
    id: "act-003",
    agent: "DECISION",
    message: "REJECTED txn-4821 with 97% confidence",
    timestamp: new Date(Date.now() - 60 * 1000).toISOString(),
  },
  {
    id: "act-004",
    agent: "DETECTOR",
    message: "Risk score 67 — txn-4822 flagged for review",
    timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
  },
  {
    id: "act-005",
    agent: "INVESTIGATOR",
    message: "Moderate deviation for Sarah M",
    timestamp: new Date(Date.now() - 6 * 60 * 1000).toISOString(),
  },
  {
    id: "act-006",
    agent: "DECISION",
    message: "REVIEW required for txn-4822",
    timestamp: new Date(Date.now() - 7 * 60 * 1000).toISOString(),
  },
]

const MOCK_USER: UserProfile = {
  id: "usr-001",
  name: "Jimmy K",
  email: "jimmy.k@example.com",
  account_age_days: 547,
  avg_spend: 200,
  usual_location: "Kochi, India",
  usual_hours: "09:00 – 22:00 IST",
  spend_pattern: "Regular small transactions, electronics and food",
  transactions: MOCK_TRANSACTIONS,
}

// ─── API Functions ─────────────────────────────────────────────────────────────

export async function getStats(): Promise<DashboardStats> {
  if (USE_MOCK) return MOCK_STATS
  try {
    const res = await fetch(`${API_BASE}/stats`)
    return res.json()
  } catch {
    return MOCK_STATS
  }
}

export async function getTransactions(): Promise<Transaction[]> {
  if (USE_MOCK) return MOCK_TRANSACTIONS
  try {
    const res = await fetch(`${API_BASE}/transactions`)
    return res.json()
  } catch {
    return []
  }
}

export async function getTransaction(id: string): Promise<AgentDecision> {
  if (USE_MOCK) return MOCK_AGENT_DECISION
  try {
    const res = await fetch(`${API_BASE}/transaction/${id}`)
    return res.json()
  } catch {
    return MOCK_AGENT_DECISION
  }
}

// Agent status always fetched live — never mocked
export async function getAgentStatus(): Promise<AgentStatus> {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: "no-store" })
    const data = await res.json()
    return data.agents as AgentStatus
  } catch {
    return { detector: "offline", investigator: "offline", decision: "offline" }
  }
}

export async function getAgentActivity(): Promise<AgentActivityItem[]> {
  if (USE_MOCK) return MOCK_ACTIVITY
  try {
    const res = await fetch(`${API_BASE}/activity`)
    return res.json()
  } catch {
    return []
  }
}

export async function getUser(id: string): Promise<UserProfile> {
  if (USE_MOCK) return MOCK_USER
  try {
    const res = await fetch(`${API_BASE}/user/${id}`)
    return res.json()
  } catch {
    return MOCK_USER
  }
}
```

- [ ] **Step 2: Commit**

```bash
cd /Users/jibinkunjumon/fraudsentinel
git add frontend/lib/api.ts
git commit -m "feat: add api.ts with USE_MOCK flag and mock data"
```

---

### Task 6: Build Shared Components

**Files:**
- Create: `frontend/components/shared/StatusBadge.tsx`
- Create: `frontend/components/shared/RiskScore.tsx`
- Create: `frontend/components/shared/AgentBadge.tsx`

- [ ] **Step 1: Create components/shared directory**

```bash
mkdir -p /Users/jibinkunjumon/fraudsentinel/frontend/components/shared
```

- [ ] **Step 2: Create StatusBadge.tsx**

```typescript
// frontend/components/shared/StatusBadge.tsx
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
```

- [ ] **Step 3: Create RiskScore.tsx**

```typescript
// frontend/components/shared/RiskScore.tsx
function getColor(score: number): string {
  if (score <= 30) return "var(--accent-green)"
  if (score <= 69) return "var(--accent-amber)"
  return "var(--accent-red)"
}

export function RiskScore({ score }: { score: number }) {
  const color = getColor(score)
  return (
    <div className="flex flex-col gap-1 min-w-[60px]">
      <span
        className="font-mono text-sm font-bold"
        style={{ color }}
      >
        {score}
      </span>
      <div className="h-1 w-full rounded-full bg-white/10">
        <div
          className="h-1 rounded-full transition-all"
          style={{ width: `${score}%`, backgroundColor: color }}
        />
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create AgentBadge.tsx**

```typescript
// frontend/components/shared/AgentBadge.tsx
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
```

- [ ] **Step 5: Commit**

```bash
cd /Users/jibinkunjumon/fraudsentinel
git add frontend/components/shared/
git commit -m "feat: add StatusBadge, RiskScore, AgentBadge shared components"
```

---

### Task 7: Build Layout Components (Sidebar + TopBar)

**Files:**
- Create: `frontend/components/layout/Sidebar.tsx`
- Create: `frontend/components/layout/TopBar.tsx`

- [ ] **Step 1: Create components/layout directory**

```bash
mkdir -p /Users/jibinkunjumon/fraudsentinel/frontend/components/layout
```

- [ ] **Step 2: Create Sidebar.tsx**

```typescript
// frontend/components/layout/Sidebar.tsx
"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useEffect, useState } from "react"
import { getAgentStatus } from "@/lib/api"
import type { AgentStatus } from "@/lib/types"

const NAV_ITEMS = [
  { label: "Dashboard", href: "/" },
  { label: "Transactions", href: "/transactions" },
  { label: "Users", href: "/users" },
  { label: "Analytics", href: "/analytics" },
  { label: "Settings", href: "/settings" },
]

const AGENTS: Array<{ key: keyof AgentStatus; label: string }> = [
  { key: "detector", label: "DETECTOR" },
  { key: "investigator", label: "INVESTIGATOR" },
  { key: "decision", label: "DECISION" },
]

export function Sidebar() {
  const pathname = usePathname()
  const [agentStatus, setAgentStatus] = useState<AgentStatus>({
    detector: "offline",
    investigator: "offline",
    decision: "offline",
  })

  useEffect(() => {
    async function fetchStatus() {
      const status = await getAgentStatus()
      setAgentStatus(status)
    }
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <aside
      className="flex flex-col h-screen sticky top-0 shrink-0"
      style={{
        width: 240,
        background: "var(--surface)",
        borderRight: "1px solid var(--border)",
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-2 px-5 py-5 border-b border-[var(--border)]">
        <span className="text-xl">🛡️</span>
        <div>
          <div className="font-bold text-sm text-white tracking-wide">
            FraudSentinel
          </div>
          <div className="text-[10px] text-[var(--text-secondary)] font-mono uppercase tracking-widest">
            AI Fraud Detection
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 px-3 py-4 flex-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`px-3 py-2 rounded text-sm font-medium transition-colors ${
                active
                  ? "text-[var(--accent-green)] border-l-2 border-[var(--accent-green)] pl-[10px]"
                  : "text-[var(--text-secondary)] hover:text-white hover:bg-white/5"
              }`}
            >
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* Agent Status */}
      <div className="px-4 py-4 border-t border-[var(--border)]">
        <div className="text-[10px] font-mono uppercase tracking-widest text-[var(--text-secondary)] mb-3">
          AI Agent Status
        </div>
        <div className="flex flex-col gap-2">
          {AGENTS.map(({ key, label }) => {
            const online = agentStatus[key] === "online"
            return (
              <div key={key} className="flex items-center justify-between">
                <span className="text-xs font-mono text-[var(--text-secondary)]">
                  {label}
                </span>
                <div className="flex items-center gap-1.5">
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      online ? "bg-[var(--accent-green)] animate-pulse" : "bg-gray-600"
                    }`}
                  />
                  <span
                    className={`text-[10px] font-mono uppercase ${
                      online ? "text-[var(--accent-green)]" : "text-gray-600"
                    }`}
                  >
                    {online ? "ONLINE" : "OFFLINE"}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </aside>
  )
}
```

- [ ] **Step 3: Create TopBar.tsx**

```typescript
// frontend/components/layout/TopBar.tsx
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
          SYNC{" "}
          <span className="text-white">{time}</span>
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
```

- [ ] **Step 4: Commit**

```bash
cd /Users/jibinkunjumon/fraudsentinel
git add frontend/components/layout/
git commit -m "feat: add Sidebar with live agent status polling and TopBar"
```

---

### Task 8: Build Dashboard Components

**Files:**
- Create: `frontend/components/dashboard/StatsRow.tsx`
- Create: `frontend/components/dashboard/TransactionTable.tsx`
- Create: `frontend/components/dashboard/AgentActivity.tsx`

- [ ] **Step 1: Create components/dashboard directory**

```bash
mkdir -p /Users/jibinkunjumon/fraudsentinel/frontend/components/dashboard
```

- [ ] **Step 2: Create StatsRow.tsx**

```typescript
// frontend/components/dashboard/StatsRow.tsx
import type { DashboardStats } from "@/lib/types"

interface StatCardProps {
  label: string
  value: number
  subtitle: string
  color: string
  borderColor: string
}

function StatCard({ label, value, subtitle, color, borderColor }: StatCardProps) {
  return (
    <div
      className="flex-1 rounded-lg p-5 border-l-4"
      style={{
        background: "var(--surface)",
        borderColor,
        borderTop: "1px solid var(--border)",
        borderRight: "1px solid var(--border)",
        borderBottom: "1px solid var(--border)",
      }}
    >
      <div className="text-xs font-mono uppercase tracking-widest text-[var(--text-secondary)] mb-2">
        {label}
      </div>
      <div className="font-mono text-3xl font-bold" style={{ color }}>
        {value.toLocaleString()}
      </div>
      <div className="text-xs text-[var(--text-secondary)] mt-1">{subtitle}</div>
      {/* Sparkline placeholder */}
      <div className="mt-3 h-8 rounded opacity-20" style={{ background: color }} />
    </div>
  )
}

export function StatsRow({ stats }: { stats: DashboardStats }) {
  return (
    <div className="flex gap-4">
      <StatCard
        label="Total Transactions"
        value={stats.total}
        subtitle="All time"
        color="var(--text-primary)"
        borderColor="var(--border)"
      />
      <StatCard
        label="Flagged"
        value={stats.flagged}
        subtitle="Pending review"
        color="var(--accent-amber)"
        borderColor="var(--accent-amber)"
      />
      <StatCard
        label="Rejected"
        value={stats.rejected}
        subtitle="Blocked"
        color="var(--accent-red)"
        borderColor="var(--accent-red)"
      />
      <StatCard
        label="Approved"
        value={stats.approved}
        subtitle="Cleared"
        color="var(--accent-green)"
        borderColor="var(--accent-green)"
      />
    </div>
  )
}
```

- [ ] **Step 3: Create TransactionTable.tsx**

```typescript
// frontend/components/dashboard/TransactionTable.tsx
import Link from "next/link"
import { RiskScore } from "@/components/shared/RiskScore"
import { StatusBadge } from "@/components/shared/StatusBadge"
import type { Transaction } from "@/lib/types"

function Initials({ name }: { name: string }) {
  const parts = name.trim().split(" ")
  const initials = parts.map((p) => p[0]).join("").slice(0, 2).toUpperCase()
  const colors = ["#4488ff", "#00ff88", "#ff4444", "#ffbb00", "#aa44ff"]
  const color = colors[name.charCodeAt(0) % colors.length]
  return (
    <div
      className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-mono font-bold text-white shrink-0"
      style={{ backgroundColor: color + "33", border: `1px solid ${color}55`, color }}
    >
      {initials}
    </div>
  )
}

function timeAgo(iso: string): string {
  const seconds = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  return `${Math.floor(minutes / 60)}h ago`
}

export function TransactionTable({ transactions }: { transactions: Transaction[] }) {
  return (
    <div
      className="rounded-lg border overflow-hidden"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="px-5 py-4 border-b border-[var(--border)]">
        <span className="text-sm font-semibold text-white">Live Transaction Feed</span>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-[10px] font-mono uppercase tracking-wider text-[var(--text-secondary)] border-b border-[var(--border)]">
            <th className="text-left px-5 py-3">User</th>
            <th className="text-left px-5 py-3">Amount</th>
            <th className="text-left px-5 py-3">Location / Time</th>
            <th className="text-left px-5 py-3">Risk Score</th>
            <th className="text-left px-5 py-3">Status</th>
            <th className="px-5 py-3" />
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx) => (
            <tr
              key={tx.id}
              className="border-b border-[var(--border)] hover:bg-white/3 transition-colors"
            >
              <td className="px-5 py-3">
                <div className="flex items-center gap-3">
                  <Initials name={tx.user_name} />
                  <div>
                    <div className="text-white text-xs font-medium">{tx.user_name}</div>
                    <div className="text-[var(--text-secondary)] text-[10px] font-mono">
                      {tx.merchant}
                    </div>
                  </div>
                </div>
              </td>
              <td className="px-5 py-3 font-mono font-bold text-white">
                {tx.currency} {tx.amount.toLocaleString()}
              </td>
              <td className="px-5 py-3">
                <div className="text-xs text-[var(--text-secondary)]">
                  📍 {tx.location}
                </div>
                <div className="text-[10px] font-mono text-[var(--text-secondary)]">
                  {timeAgo(tx.timestamp)}
                </div>
              </td>
              <td className="px-5 py-3">
                <RiskScore score={tx.risk_score} />
              </td>
              <td className="px-5 py-3">
                <StatusBadge status={tx.status} />
              </td>
              <td className="px-5 py-3">
                <Link
                  href={`/transaction/${tx.id}`}
                  className="text-[10px] font-mono uppercase tracking-wider px-3 py-1 rounded border border-[var(--border)] text-[var(--text-secondary)] hover:text-white hover:border-white/30 transition-colors"
                >
                  VIEW
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

- [ ] **Step 4: Create AgentActivity.tsx**

```typescript
// frontend/components/dashboard/AgentActivity.tsx
import { AgentBadge } from "@/components/shared/AgentBadge"
import type { AgentActivityItem } from "@/lib/types"

function timeAgo(iso: string): string {
  const seconds = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  return `${Math.floor(minutes / 60)}h ago`
}

export function AgentActivity({ activities }: { activities: AgentActivityItem[] }) {
  return (
    <div
      className="flex flex-col h-full rounded-lg border overflow-hidden"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="flex items-center justify-between px-4 py-4 border-b border-[var(--border)]">
        <span className="text-sm font-semibold text-white">Agent Activity</span>
        <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full bg-green-500/10 text-[var(--accent-green)] border border-green-500/20 flex items-center gap-1">
          <span className="w-1 h-1 rounded-full bg-[var(--accent-green)] animate-pulse inline-block" />
          Live
        </span>
      </div>
      <div className="flex flex-col overflow-y-auto flex-1">
        {activities.map((item, i) => (
          <div key={item.id}>
            <div className="px-4 py-3">
              <div className="flex items-center justify-between mb-1">
                <AgentBadge agent={item.agent} />
                <span className="text-[10px] font-mono text-[var(--text-secondary)]">
                  {timeAgo(item.timestamp)}
                </span>
              </div>
              <p className="text-xs text-[var(--text-secondary)] mt-1 leading-relaxed">
                {item.message}
              </p>
            </div>
            {i < activities.length - 1 && (
              <div className="border-b border-[var(--border)]" />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Commit**

```bash
cd /Users/jibinkunjumon/fraudsentinel
git add frontend/components/dashboard/
git commit -m "feat: add StatsRow, TransactionTable, AgentActivity dashboard components"
```

---

### Task 9: Build Main Dashboard Page

**Files:**
- Modify: `frontend/app/page.tsx`

- [ ] **Step 1: Replace app/page.tsx**

```typescript
// frontend/app/page.tsx
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
```

- [ ] **Step 2: Commit**

```bash
cd /Users/jibinkunjumon/fraudsentinel
git add frontend/app/page.tsx
git commit -m "feat: build main dashboard page with stats, table, and activity panel"
```

---

### Task 10: Build Transaction Detail Components and Page

**Files:**
- Create: `frontend/components/transaction/TransactionCard.tsx`
- Create: `frontend/components/transaction/AgentReasoning.tsx`
- Create: `frontend/app/transaction/[id]/page.tsx`

- [ ] **Step 1: Create components/transaction directory**

```bash
mkdir -p /Users/jibinkunjumon/fraudsentinel/frontend/components/transaction
mkdir -p /Users/jibinkunjumon/fraudsentinel/frontend/app/transaction/\[id\]
```

- [ ] **Step 2: Create TransactionCard.tsx**

```typescript
// frontend/components/transaction/TransactionCard.tsx
import type { Transaction } from "@/lib/types"

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
```

- [ ] **Step 3: Create AgentReasoning.tsx**

```typescript
// frontend/components/transaction/AgentReasoning.tsx
import { AgentBadge } from "@/components/shared/AgentBadge"
import { RiskScore } from "@/components/shared/RiskScore"
import { StatusBadge } from "@/components/shared/StatusBadge"
import type { AgentDecision } from "@/lib/types"

export function AgentReasoning({ decision }: { decision: AgentDecision }) {
  return (
    <div className="flex flex-col gap-4">
      {/* DETECTOR */}
      <div
        className="rounded-lg border p-4"
        style={{ background: "var(--surface)", borderColor: "var(--border)" }}
      >
        <div className="flex items-center gap-2 mb-3">
          <AgentBadge agent="DETECTOR" />
        </div>
        <RiskScore score={decision.detector.risk_score} />
        <ul className="mt-3 flex flex-col gap-1">
          {decision.detector.flags.map((flag, i) => (
            <li key={i} className="text-xs text-[var(--text-secondary)] flex gap-2">
              <span className="text-[var(--accent-red)] shrink-0">▸</span>
              {flag}
            </li>
          ))}
        </ul>
      </div>

      {/* INVESTIGATOR */}
      <div
        className="rounded-lg border p-4"
        style={{ background: "var(--surface)", borderColor: "var(--border)" }}
      >
        <div className="flex items-center justify-between mb-3">
          <AgentBadge agent="INVESTIGATOR" />
          <span className="text-xs font-mono text-[var(--text-secondary)]">
            deviation:{" "}
            <span className="text-[var(--accent-amber)]">
              {decision.investigator.deviation_score}
            </span>
          </span>
        </div>
        <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
          {decision.investigator.summary}
        </p>
      </div>

      {/* DECISION */}
      <div
        className="rounded-lg border p-4"
        style={{ background: "var(--surface)", borderColor: "var(--border)" }}
      >
        <div className="flex items-center justify-between mb-3">
          <AgentBadge agent="DECISION" />
          <StatusBadge status={decision.decision.verdict} />
        </div>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[10px] font-mono text-[var(--text-secondary)] uppercase">
            Confidence
          </span>
          <span className="text-[var(--accent-green)] font-mono text-sm font-bold">
            {decision.decision.confidence}%
          </span>
        </div>
        <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
          {decision.decision.reason}
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mt-2">
        <button className="flex-1 py-2 rounded text-xs font-mono uppercase tracking-wider font-bold bg-green-500/20 text-[var(--accent-green)] border border-green-500/30 hover:bg-green-500/30 transition-colors">
          Approve
        </button>
        <button className="flex-1 py-2 rounded text-xs font-mono uppercase tracking-wider font-bold bg-red-500/20 text-[var(--accent-red)] border border-red-500/30 hover:bg-red-500/30 transition-colors">
          Reject
        </button>
        <button className="flex-1 py-2 rounded text-xs font-mono uppercase tracking-wider font-bold bg-amber-500/20 text-[var(--accent-amber)] border border-amber-500/30 hover:bg-amber-500/30 transition-colors">
          Escalate
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create transaction detail page**

Create `frontend/app/transaction/[id]/page.tsx`:

```typescript
import { getTransaction, getTransactions } from "@/lib/api"
import { Sidebar } from "@/components/layout/Sidebar"
import { TopBar } from "@/components/layout/TopBar"
import { TransactionCard } from "@/components/transaction/TransactionCard"
import { AgentReasoning } from "@/components/transaction/AgentReasoning"

export const dynamic = "force-dynamic"

export default async function TransactionDetailPage({
  params,
}: {
  params: { id: string }
}) {
  const [decision, transactions] = await Promise.all([
    getTransaction(params.id),
    getTransactions(),
  ])

  // Find the transaction object for TransactionCard
  const tx = transactions.find((t) => t.id === params.id) ?? transactions[0]

  // Mock user behavior data
  const userBehavior = {
    avgSpend: 200,
    usualLocation: "Kochi, India",
    accountAgeDays: 547,
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
            <AgentReasoning decision={decision} />
          </div>
        </main>
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Commit**

```bash
cd /Users/jibinkunjumon/fraudsentinel
git add frontend/components/transaction/ frontend/app/transaction/
git commit -m "feat: build transaction detail page with agent reasoning cards"
```

---

### Task 11: Build User Profile Page

**Files:**
- Create: `frontend/app/user/[id]/page.tsx`

- [ ] **Step 1: Create the user directory**

```bash
mkdir -p /Users/jibinkunjumon/fraudsentinel/frontend/app/user/\[id\]
```

- [ ] **Step 2: Create user profile page**

Create `frontend/app/user/[id]/page.tsx`:

```typescript
import { getUser } from "@/lib/api"
import { Sidebar } from "@/components/layout/Sidebar"
import { TopBar } from "@/components/layout/TopBar"
import { TransactionTable } from "@/components/dashboard/TransactionTable"

export const dynamic = "force-dynamic"

export default async function UserProfilePage({
  params,
}: {
  params: { id: string }
}) {
  const user = await getUser(params.id)

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
              <BehaviorField label="Spend Pattern" value={user.spend_pattern} />
            </div>
          </div>

          {/* Transaction history */}
          <TransactionTable transactions={user.transactions} />
        </main>
      </div>
    </div>
  )
}

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
```

- [ ] **Step 3: Commit**

```bash
cd /Users/jibinkunjumon/fraudsentinel
git add frontend/app/user/
git commit -m "feat: build user profile page with behavior patterns and transaction history"
```

---

### Task 12: Verify Dev Server

**Files:**
- No changes — verification only

- [ ] **Step 1: Run the dev server**

```bash
cd /Users/jibinkunjumon/fraudsentinel/frontend
npm run dev
```

Expected output contains:
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
- Environments: .env.local
✓ Ready in ...ms
```

- [ ] **Step 2: Check for TypeScript errors**

```bash
cd /Users/jibinkunjumon/fraudsentinel/frontend
npx tsc --noEmit
```

Expected: no output (zero errors).

- [ ] **Step 3: Run ESLint**

```bash
cd /Users/jibinkunjumon/fraudsentinel/frontend
npm run lint
```

Expected: `✔ No ESLint warnings or errors`

If lint errors are reported, fix them before proceeding.

- [ ] **Step 4: Final commit**

```bash
cd /Users/jibinkunjumon/fraudsentinel
git add frontend/
git commit -m "feat: complete Next.js FraudSentinel dashboard — all pages and components built"
```

---

## Self-Review

**Spec coverage check:**
- ✅ Next.js init with correct flags (Task 1)
- ✅ shadcn/ui init + 5 components (Task 2)
- ✅ Dark theme — `darkMode: "class"`, CSS vars, layout with `className="dark"` (Task 3)
- ✅ All TypeScript interfaces including `AgentActivityItem` and `UserProfile` (Task 4)
- ✅ `USE_MOCK = true`, `NEXT_PUBLIC_API_URL` flag, all 6 API functions, `/health` always live (Task 5)
- ✅ StatusBadge, RiskScore, AgentBadge shared components (Task 6)
- ✅ Sidebar with 240px width, nav links, agent status pulsing dots (Task 7)
- ✅ TopBar with live clock and SYSTEM LIVE badge (Task 7)
- ✅ StatsRow with 4 colored cards + sparkline placeholder (Task 8)
- ✅ TransactionTable with initials avatar, monospace amounts, RiskScore, StatusBadge, VIEW link (Task 8)
- ✅ AgentActivity with AgentBadge + LIVE POLLING badge (Task 8)
- ✅ Main dashboard page layout: Sidebar + main + right 320px panel (Task 9)
- ✅ Mock data matches spec: Jimmy K $4500 Nigeria REJECTED 94, Sarah M, Mark T, Priya S (Task 5)
- ✅ Transaction detail: two-column, TransactionCard + UserBehavior + AgentReasoning with 3 cards (Task 10)
- ✅ Action buttons: Approve/Reject/Escalate with correct colors (Task 10)
- ✅ User profile: header, behavioral patterns, transaction history table (Task 11)
- ✅ `npm run dev` verification (Task 12)
- ✅ `.env.local` created (Task 1)

**Type consistency check:**
- `AgentActivityItem` defined in types.ts (Task 4) and used in `AgentActivity.tsx` (Task 8) — ✅ match
- `USE_MOCK` flag controls all functions except `getAgentStatus` — ✅ consistent throughout api.ts
- `Transaction` used in `TransactionTable` props — ✅ matches type definition
- `AgentDecision` used in `AgentReasoning` props — ✅ matches type definition
