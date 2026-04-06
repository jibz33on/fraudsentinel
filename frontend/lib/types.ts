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
