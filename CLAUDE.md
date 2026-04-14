# FraudSentinel — Claude Code Context

## What This Project Is
An autonomous multi-agent fraud detection system.
3 AI agents analyze transactions and make fraud decisions.
Full dashboard UI built in Next.js.

## Agent Pipeline
Transaction → DETECTOR → INVESTIGATOR → DECISION → Supabase → Dashboard

## The 3 Agents
DETECTOR     → rule-based risk scorer + LLM for ambiguous scores (40-70)
INVESTIGATOR → behavioral deviation analysis + LLM when deviation > 50
DECISION     → final verdict (APPROVE / REVIEW / REJECT) + LLM reasoning

## Tech Stack
- Python 3.11 (conda env: fraudsentinel)
- LangGraph → agent pipeline orchestration
- FastAPI + uvicorn → REST API
- Supabase → database + pgvector (vector memory)
- NVIDIA NIM (meta/llama-3.3-70b-instruct) → primary LLM
- OpenRouter → fallback LLM (automatic via llm_router)
- Next.js → frontend dashboard
- Railway → backend deployment (pending)
- Cloudflare Pages → frontend deployment (pending)

## Folder Structure
fraudsentinel/
├── agents/
│   ├── detector/
│   │   ├── rules_engine.py   ← pure rule checks (no I/O)
│   │   ├── scorer.py         ← flags → risk score (no I/O)
│   │   └── detector.py       ← orchestrates rules + scorer + LLM
│   ├── investigator/
│   │   ├── profiler.py       ← fetches user history from db/
│   │   └── investigator.py   ← deviation analysis + LLM
│   └── decision/
│       └── decision.py       ← final verdict + LLM reasoning
├── graph/
│   ├── state.py              ← shared TypedDict state (clipboard)
│   └── pipeline.py           ← LangGraph wiring, delegates DB to db/
├── db/
│   ├── client.py             ← single Supabase HTTP client
│   ├── decisions.py          ← agent_decisions table (read/write)
│   ├── transactions.py       ← transactions table (read)
│   └── users.py              ← users table (read)
├── memory/
│   └── vector.py             ← pgvector similarity search
├── tools/
│   ├── llm_router.py         ← NVIDIA NIM → OpenRouter fallback (3x retry)
│   ├── embed.py              ← NVIDIA embedding API
│   └── logger.py             ← logger factory
├── api/
│   ├── main.py               ← FastAPI app + CORS + router registration
│   ├── models.py             ← Pydantic request/response schemas
│   └── routers/
│       ├── analyze.py        ← POST /analyze → saves txn → runs pipeline
│       ├── dashboard.py      ← GET endpoints for UI (all use db/ layer)
│       └── health.py         ← GET /health
├── frontend/                 ← Next.js dashboard (separate)
├── scripts/
│   ├── simulate.py           ← infinite loop random transaction generator
│   └── run_golden_dataset.py ← runs 8 seed transactions through pipeline
├── tests/                    ← all test files
├── supabase/
│   └── migrations/           ← all schema migrations
├── docs/                     ← architecture notes
├── .env                      ← API keys (never commit)
├── requirements.txt
└── CLAUDE.md                 ← this file

## Supabase Tables
### transactions
id, user_id, amount, currency, merchant, location, 
ip_address, device, status, created_at

### users
id, name, email, avg_spend, usual_location, usual_hours, 
transaction_count, account_age_days, risk_profile, created_at

### agent_decisions
id, transaction_id, 
detector_score, detector_flags,
investigator_summary, investigator_deviation,
decision_verdict, decision_confidence, decision_reason,
detector_duration_ms, investigator_duration_ms, decision_duration_ms,
status, created_at

status values: in_progress → complete | failed

## LLM Setup
Provider:  NVIDIA NIM (free tier)
Base URL:  https://integrate.api.nvidia.com/v1
Model:     meta/llama-3.3-70b-instruct
Fallback:  OpenRouter (automatic, 3x retry on NVIDIA first)
Key:       NVIDIA_API_KEY in .env
Router:    tools/llm_router.py → call_llm() — always use this, never raw requests

## Layer Architecture
api/        ← receives HTTP, validates with Pydantic, returns responses
graph/      ← LangGraph orchestration only, no logic, no DB
agents/     ← pure logic, reads/writes state only
tools/      ← shared utilities (LLM, embeddings, logger)
db/         ← ALL Supabase I/O lives here, nowhere else
memory/     ← pgvector similarity search via db/client

## Hard Rules
- Never commit .env
- Always use: conda activate fraudsentinel
- Always use: python not python3
- Agent pipeline order: DETECTOR → INVESTIGATOR → DECISION, always
- db/ owns ALL Supabase I/O — no raw requests to Supabase anywhere else
- Agents are pure logic — no DB calls except profiler.py (needs user history)
- pipeline.py orchestrates only — delegates all DB writes to db/
- Always use call_llm() from tools/llm_router — never raw requests.post to NVIDIA
- Transaction must be saved to db/transactions before pipeline runs (FK constraint)
- Verify server starts after every change before moving to next step
- One step at a time

## API Endpoints
POST /analyze          ← submit transaction, runs full pipeline
GET  /health           ← health check
GET  /dashboard/stats                           ← summary stats
GET  /dashboard/transactions                    ← recent transactions (status=complete only)
GET  /dashboard/transaction/{id}
GET  /dashboard/users/{id}
GET  /dashboard/activity
POST /dashboard/transaction/{id}/approve        ← manual approve
POST /dashboard/transaction/{id}/reject         ← manual reject

## Current Status
✅ Modular folder structure (db/, agents/, graph/, api/, tools/, memory/)
✅ Single Supabase client in db/client.py
✅ Pydantic validation on all input/output
✅ Error handling on all API endpoints
✅ Agent logic isolated — one agent crash won't kill pipeline
✅ Pipeline status tracking (in_progress / complete / failed)
✅ Duration tracking per agent (detector/investigator/decision _duration_ms)
✅ LLM enabled on all 3 agents via call_llm()
✅ FK constraint fixed — transaction saved before pipeline runs
✅ Full end-to-end test passed
✅ Seed historical data (scripts/seed_data.py)
✅ memory/memory.py — fixed broken import + switched to supabase-py
✅ transactions table now written on every /analyze call
✅ pipeline_failed tracking — silent agent failures now set status=failed
✅ embedding fix — saved as vector not string
✅ Full test suite: 102/102 passing
   - test_detector.py     47/47
   - test_investigator.py 24/24
   - test_decision.py     21/21
   - test_pipeline.py     10/10
✅ Real user profile now passed to DETECTOR in pipeline.py
✅ APPROVE/REJECT endpoints: POST /dashboard/transaction/{id}/approve and /reject
✅ Backend fully complete
✅ All frontend pages built (/transactions, /users, /analytics, /settings)
✅ /dashboard/users and /dashboard/analytics backend endpoints added
✅ TransactionTable fixed to use TransactionDetail shape
✅ Approve/Reject/Escalate buttons wired with loading states
✅ Live polling on dashboard (5s) and analytics (15s)
✅ Settings page with test transaction form (POST /analyze)
✅ All 8 routes compile clean, no TS errors, committed and pushed

## Remaining TODOs
⬜ UI polish pass — /transactions, /users, /analytics, /settings
⬜ Deploy backend → Railway
⬜ Deploy frontend → Cloudflare Pages

## Seed Users (Supabase)
6 users seeded: Jimmy K, Mark T, Sarah M, Priya S, Alex R, TechCorp Ltd
Transactions table: ~8 seed rows total (thin history)
Note: transaction_count on users table is seeded high but actual 
transactions table rows are sparse — seed_data.py needed

## Next Session Starts With
1. Screenshot review of /transactions, /users, /analytics, /settings
2. UI polish pass on each page
3. Deploy backend → Railway
4. Deploy frontend → Cloudflare Pages
