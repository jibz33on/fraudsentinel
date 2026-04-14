export interface Transaction {
  id: string
  user_id?: string
  user_name: string
  amount: number
  currency: string
  merchant: string
  location: string
  ip_address?: string
  device?: string
  timestamp: string
  risk_score: number
  status: "APPROVED" | "REVIEW" | "REJECTED"
  created_at?: string
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

export interface TransactionDetail {
  transaction: Transaction
  decision: AgentDecision | null
}

export interface DashboardStats {
  total: number
  approved: number
  rejected: number
  review: number
  flagged: number
  fraud_rate: number
}

export interface AgentStatus {
  detector: "online" | "offline"
  investigator: "online" | "offline"
  decision: "online" | "offline"
}

export interface AgentActivityItem {
  id: string
  agent: "DETECTOR" | "INVESTIGATOR" | "DECISION"
  timestamp: string
  verdict: string
  confidence: number | null
  merchant: string
  user_name: string
}

export interface AnalyticsData {
  verdict_breakdown: {
    total: number
    approved: number
    review: number
    rejected: number
    fraud_rate: number
  }
  avg_scores: {
    detector_score: number
    investigator_deviation: number
    decision_confidence: number
  }
  top_flags: Array<{ flag: string; count: number }>
  daily_trend: Array<{
    date: string
    total: number
    approved: number
    review: number
    rejected: number
  }>
}

export interface UserProfile {
  id: string
  name: string
  email: string
  avg_spend: number
  usual_location: string
  usual_hours: string
  transaction_count: number
  account_age_days: number
  risk_profile: string
  created_at: string
}
