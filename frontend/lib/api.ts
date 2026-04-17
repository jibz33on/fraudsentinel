import type {
  TransactionDetail,
  DashboardStats,
  AgentStatus,
  AgentActivityItem,
  UserProfile,
  AnalyticsData,
} from "./types"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function getStats(): Promise<DashboardStats> {
  const res = await fetch(`${API_BASE}/dashboard/stats`)
  if (!res.ok) throw new Error(`getStats failed: ${res.status}`)
  return res.json()
}

export async function getTransactions(): Promise<TransactionDetail[]> {
  const res = await fetch(`${API_BASE}/dashboard/transactions`)
  if (!res.ok) throw new Error(`getTransactions failed: ${res.status}`)
  return res.json()
}

export async function getTransaction(id: string): Promise<TransactionDetail> {
  const res = await fetch(`${API_BASE}/dashboard/transaction/${id}`)
  if (!res.ok) throw new Error(`getTransaction failed: ${res.status}`)
  const data = await res.json()
  return data
}

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
  const res = await fetch(`${API_BASE}/dashboard/activity`)
  if (!res.ok) throw new Error(`getAgentActivity failed: ${res.status}`)
  return res.json()
}

export async function getUsers(): Promise<UserProfile[]> {
  const res = await fetch(`${API_BASE}/dashboard/users`)
  if (!res.ok) throw new Error(`getUsers failed: ${res.status}`)
  return res.json()
}

export async function getUser(id: string): Promise<UserProfile> {
  const res = await fetch(`${API_BASE}/dashboard/users/${id}`)
  if (!res.ok) throw new Error(`getUser failed: ${res.status}`)
  return res.json()
}

export async function getAnalytics(): Promise<AnalyticsData> {
  const res = await fetch(`${API_BASE}/dashboard/analytics`)
  if (!res.ok) throw new Error(`getAnalytics failed: ${res.status}`)
  return res.json()
}

export async function submitAnalyze(payload: {
  transaction_id: string
  user_id: string
  amount: number
  country: string
  location?: string
  hour: number
  merchant: string
  method: string
  currency?: string
  ip_address?: string
  ip_country?: string
  device?: string
}): Promise<{ transaction_id: string; verdict: string; confidence: number; reason: string }> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error(`submitAnalyze failed: ${res.status}`)
  return res.json()
}

export async function approveTransaction(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/dashboard/transaction/${id}/approve`, {
    method: "POST",
  })
  if (!res.ok) throw new Error(`approveTransaction failed: ${res.status}`)
}

export async function rejectTransaction(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/dashboard/transaction/${id}/reject`, {
    method: "POST",
  })
  if (!res.ok) throw new Error(`rejectTransaction failed: ${res.status}`)
}

export async function createUser(name: string, email: string): Promise<UserProfile> {
  const res = await fetch(`${API_BASE}/dashboard/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email }),
  })
  if (!res.ok) throw new Error(`createUser failed: ${res.status}`)
  return res.json()
}
