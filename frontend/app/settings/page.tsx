"use client"

import { useState, useEffect } from "react"
import { submitAnalyze, createUser, getUsers } from "@/lib/api"
import type { UserProfile } from "@/lib/types"
import { Sidebar } from "@/components/layout/Sidebar"
import { TopBar } from "@/components/layout/TopBar"

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

const PIPELINE_STAGES = [
  { name: "DETECTOR",     desc: "Rule-based risk scorer + LLM for ambiguous scores (40–70)" },
  { name: "INVESTIGATOR", desc: "Behavioural deviation analysis + LLM when deviation > 50" },
  { name: "DECISION",     desc: "Final verdict (APPROVE / REVIEW / REJECT) + LLM reasoning" },
]

const DEFAULT_USERS = [
  { id: "55472a7d-8980-4777-b98d-e8b65e65d33c", label: "Jimmy K" },
  { id: "67f045c9-658d-4e62-8300-877be9a006d1", label: "Mark T" },
  { id: "720b0db6-e4b4-4ca1-9989-5693728d871a", label: "Sarah M" },
  { id: "d5dbff76-59df-45d8-b92d-bfa4cd3a7748", label: "Priya S" },
  { id: "dce92994-825b-4264-8ece-67b4ca440cbe", label: "Alex R" },
  { id: "5f3bfd92-46d1-46b5-b82d-4bacbc42928d", label: "TechCorp Ltd" },
]

const PAYMENT_METHODS = ["card", "bank_transfer", "crypto", "wallet"]

interface FormState {
  user_id:    string
  amount:     string
  country:    string
  location:   string
  hour:       string
  merchant:   string
  method:     string
  currency:   string
  ip_address: string
  ip_country: string
  device:     string
}

interface AnalyzeResult {
  transaction_id: string
  verdict: string
  confidence: number
  reason: string
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div
      className="rounded-lg border p-5 flex flex-col gap-4"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      <div className="text-xs font-mono font-semibold text-white uppercase tracking-wider">{title}</div>
      {children}
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b last:border-0" style={{ borderColor: "var(--border)" }}>
      <span className="text-xs font-mono text-[var(--text-secondary)]">{label}</span>
      <span className="text-xs font-mono text-white">{value}</span>
    </div>
  )
}

const verdictColors: Record<string, string> = {
  APPROVED: "text-[var(--accent-green)]",
  REVIEW:   "text-[var(--accent-amber)]",
  REJECTED: "text-[var(--accent-red)]",
}

export default function SettingsPage() {
  const [userList, setUserList] = useState(DEFAULT_USERS)

  useEffect(() => {
    getUsers().then((users) =>
      setUserList(users.map((u) => ({ id: u.id, label: u.name })))
    ).catch(() => {/* keep DEFAULT_USERS on failure */})
  }, [])

  const [newUserName,   setNewUserName]   = useState("")
  const [newUserEmail,  setNewUserEmail]  = useState("")
  const [creatingUser,  setCreatingUser]  = useState(false)
  const [createdUser,   setCreatedUser]   = useState<UserProfile | null>(null)
  const [createError,   setCreateError]   = useState<string | null>(null)

  async function handleCreateUser(e: { preventDefault: () => void }) {
    e.preventDefault()
    setCreatingUser(true)
    setCreatedUser(null)
    setCreateError(null)
    try {
      const user = await createUser(newUserName.trim(), newUserEmail.trim())
      setUserList((prev) => [...prev, { id: user.id, label: user.name }])
      set("user_id", user.id)
      setCreatedUser(user)
      setNewUserName("")
      setNewUserEmail("")
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : "Failed to create user")
    } finally {
      setCreatingUser(false)
    }
  }

  const [form, setForm] = useState<FormState>({
    user_id:    userList[0].id,
    amount:     "250",
    country:    "US",
    location:   "United States",
    hour:       "14",
    merchant:   "Amazon",
    method:     "card",
    currency:   "USD",
    ip_address: "192.168.1.1",
    ip_country: "US",
    device:     "Chrome/Mac",
  })
  const [submitting, setSubmitting] = useState(false)
  const [result, setResult]         = useState<AnalyzeResult | null>(null)
  const [submitError, setSubmitError] = useState<string | null>(null)

  function set(key: keyof FormState, value: string) {
    setForm((f) => ({ ...f, [key]: value }))
  }

  async function handleSubmit(e: { preventDefault: () => void }) {
    e.preventDefault()
    setSubmitting(true)
    setResult(null)
    setSubmitError(null)
    try {
      const res = await submitAnalyze({
        transaction_id: crypto.randomUUID(),
        user_id:        form.user_id,
        amount:         parseFloat(form.amount) || 0,
        country:        form.country,
        location:       form.location,
        hour:           parseInt(form.hour, 10) || 0,
        merchant:       form.merchant,
        method:         form.method,
        currency:       form.currency,
        ip_address:     form.ip_address,
        ip_country:     form.ip_country,
        device:         form.device,
      })
      setResult(res)
    } catch (e) {
      setSubmitError(e instanceof Error ? e.message : "Submission failed")
    } finally {
      setSubmitting(false)
    }
  }

  const inputCls =
    "w-full px-3 py-2 rounded-lg text-xs font-mono border bg-transparent text-white placeholder:text-[var(--text-secondary)] focus:outline-none focus:border-white/30"
  const inputStyle = { borderColor: "var(--border)" }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <TopBar title="Settings" />
        <main className="flex-1 overflow-y-auto p-6 flex flex-col gap-6 max-w-3xl">

          {/* System config */}
          <Section title="System Configuration">
            <InfoRow label="API Base URL"  value={API_BASE} />
            <InfoRow label="LLM Provider"  value="NVIDIA NIM (meta/llama-3.3-70b-instruct)" />
            <InfoRow label="Fallback LLM"  value="OpenRouter (3× retry)" />
            <InfoRow label="Database"      value="Supabase + pgvector" />
          </Section>

          {/* Pipeline info */}
          <Section title="Agent Pipeline">
            <div className="flex flex-col gap-3">
              {PIPELINE_STAGES.map((stage, i) => (
                <div key={stage.name} className="flex items-start gap-3">
                  <div
                    className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-mono font-bold shrink-0 mt-0.5"
                    style={{ background: "var(--accent-blue)22", border: "1px solid var(--accent-blue)44", color: "var(--accent-blue)" }}
                  >
                    {i + 1}
                  </div>
                  <div>
                    <div className="text-xs font-mono font-bold text-white">{stage.name}</div>
                    <div className="text-[11px] font-mono text-[var(--text-secondary)]">{stage.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </Section>

          {/* Create test user */}
          <Section title="Create Test User">
            <p className="text-[11px] font-mono text-[var(--text-secondary)] leading-relaxed">
              New users have 0 transactions — no behavioural baseline can be built. Submit a transaction for a new
              user to see the <span className="text-blue-400">New Account</span> panel in the investigator output.
            </p>
            <form onSubmit={handleCreateUser} className="flex flex-col gap-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">Full Name</label>
                  <input
                    type="text"
                    required
                    value={newUserName}
                    onChange={(e) => setNewUserName(e.target.value)}
                    placeholder="e.g. Jane Doe"
                    className={inputCls}
                    style={inputStyle}
                  />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">Email</label>
                  <input
                    type="email"
                    required
                    value={newUserEmail}
                    onChange={(e) => setNewUserEmail(e.target.value)}
                    placeholder="e.g. jane@example.com"
                    className={inputCls}
                    style={inputStyle}
                  />
                </div>
              </div>
              <button
                type="submit"
                disabled={creatingUser}
                className="px-4 py-2 rounded-lg text-xs font-mono font-bold transition-colors disabled:opacity-50"
                style={{
                  background: "var(--accent-blue)22",
                  border:     "1px solid var(--accent-blue)44",
                  color:      "var(--accent-blue)",
                }}
              >
                {creatingUser ? "Creating…" : "Create User"}
              </button>
            </form>

            {createdUser && (
              <div
                className="rounded-lg border p-3 flex flex-col gap-1"
                style={{ borderColor: "var(--accent-green)44", background: "var(--accent-green)11" }}
              >
                <div className="text-[10px] font-mono uppercase text-[var(--accent-green)] mb-1">User Created</div>
                <div className="text-xs font-mono text-white">{createdUser.name}</div>
                <div className="text-[11px] font-mono text-[var(--text-secondary)]">{createdUser.email}</div>
                <div className="text-[9px] font-mono text-[var(--text-secondary)] mt-1">ID: {createdUser.id}</div>
                <div className="text-[10px] font-mono text-[var(--text-secondary)] mt-1">
                  Now submit a transaction above using this user ID to see the{" "}
                  <span className="text-blue-400">New Account</span> investigator panel.
                </div>
              </div>
            )}

            {createError && (
              <div className="text-xs font-mono text-[var(--accent-red)]">{createError}</div>
            )}
          </Section>

          {/* Test transaction form */}
          <Section title="Submit Test Transaction">
            <form onSubmit={handleSubmit} className="flex flex-col gap-3">
              <div className="grid grid-cols-2 gap-3">
                {/* User */}
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">User</label>
                  <select
                    value={form.user_id}
                    onChange={(e) => set("user_id", e.target.value)}
                    className={inputCls}
                    style={{ ...inputStyle, background: "var(--surface)" }}
                  >
                    {userList.map((u) => (
                      <option key={u.id} value={u.id}>{u.label}</option>
                    ))}
                  </select>
                </div>

                {/* Amount */}
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">Amount (USD)</label>
                  <input
                    type="number"
                    min="1"
                    step="0.01"
                    value={form.amount}
                    onChange={(e) => set("amount", e.target.value)}
                    className={inputCls}
                    style={inputStyle}
                  />
                </div>

                {/* Merchant */}
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">Merchant</label>
                  <input
                    type="text"
                    value={form.merchant}
                    onChange={(e) => set("merchant", e.target.value)}
                    className={inputCls}
                    style={inputStyle}
                    placeholder="e.g. Amazon"
                  />
                </div>

                {/* Country */}
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">Country</label>
                  <input
                    type="text"
                    value={form.country}
                    onChange={(e) => set("country", e.target.value)}
                    className={inputCls}
                    style={inputStyle}
                    placeholder="e.g. US"
                  />
                </div>

                {/* Location */}
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">Location (full name)</label>
                  <input
                    type="text"
                    value={form.location}
                    onChange={(e) => set("location", e.target.value)}
                    className={inputCls}
                    style={inputStyle}
                    placeholder="e.g. Kochi, India"
                  />
                </div>

                {/* Hour */}
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">Hour (0–23)</label>
                  <input
                    type="number"
                    min="0"
                    max="23"
                    value={form.hour}
                    onChange={(e) => set("hour", e.target.value)}
                    className={inputCls}
                    style={inputStyle}
                  />
                </div>

                {/* Method */}
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">Payment Method</label>
                  <select
                    value={form.method}
                    onChange={(e) => set("method", e.target.value)}
                    className={inputCls}
                    style={{ ...inputStyle, background: "var(--surface)" }}
                  >
                    {PAYMENT_METHODS.map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </div>

                {/* Currency */}
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">Currency</label>
                  <input
                    type="text"
                    value={form.currency}
                    onChange={(e) => set("currency", e.target.value)}
                    className={inputCls}
                    style={inputStyle}
                    placeholder="e.g. USD"
                  />
                </div>

                {/* IP Address */}
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">IP Address</label>
                  <input
                    type="text"
                    value={form.ip_address}
                    onChange={(e) => set("ip_address", e.target.value)}
                    className={inputCls}
                    style={inputStyle}
                    placeholder="e.g. 192.168.1.1"
                  />
                </div>

                {/* IP Country */}
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">IP Country</label>
                  <input
                    type="text"
                    value={form.ip_country}
                    onChange={(e) => set("ip_country", e.target.value)}
                    className={inputCls}
                    style={inputStyle}
                    placeholder="e.g. US"
                  />
                </div>

                {/* Device */}
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">Device</label>
                  <input
                    type="text"
                    value={form.device}
                    onChange={(e) => set("device", e.target.value)}
                    className={inputCls}
                    style={inputStyle}
                    placeholder="e.g. Chrome/Mac"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="mt-1 px-4 py-2 rounded-lg text-xs font-mono font-bold transition-colors disabled:opacity-50"
                style={{
                  background:   "var(--accent-blue)22",
                  border:       "1px solid var(--accent-blue)44",
                  color:        "var(--accent-blue)",
                }}
              >
                {submitting ? "Running pipeline…" : "Run Pipeline"}
              </button>
            </form>

            {/* Result */}
            {result && (
              <div
                className="mt-2 rounded-lg border p-4 flex flex-col gap-2"
                style={{ borderColor: "var(--border)", background: "var(--bg)" }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">Verdict</span>
                  <span className={`text-sm font-mono font-bold ${verdictColors[result.verdict] ?? "text-white"}`}>
                    {result.verdict}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono uppercase text-[var(--text-secondary)]">Confidence</span>
                  <span className="text-sm font-mono text-white">{result.confidence}%</span>
                </div>
                <div className="pt-1 border-t" style={{ borderColor: "var(--border)" }}>
                  <div className="text-[10px] font-mono uppercase text-[var(--text-secondary)] mb-1">Reason</div>
                  <div className="text-xs font-mono text-white leading-relaxed">{result.reason}</div>
                </div>
                <div className="text-[9px] font-mono text-[var(--text-secondary)]">
                  ID: {result.transaction_id}
                </div>
              </div>
            )}

            {submitError && (
              <div className="mt-2 text-xs font-mono text-[var(--accent-red)]">{submitError}</div>
            )}
          </Section>

        </main>
      </div>
    </div>
  )
}
