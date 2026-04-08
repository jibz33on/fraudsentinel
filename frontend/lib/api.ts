import type {
  Transaction,
  AgentDecision,
  DashboardStats,
  AgentStatus,
  AgentActivityItem,
  UserProfile,
} from "./types"

const USE_MOCK = false
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
    const data = await res.json()
    return data.decision
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
    if (!res.ok) return []
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
