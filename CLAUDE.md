# FraudSentinel — Claude Code Context

## What This Project Is
An autonomous multi-agent fraud detection system.
3 AI agents analyze transactions and make decisions.
Full dashboard UI already built via Google Stitch.

## The 3 Agents
DETECTOR     → fast risk scorer (rule-based + LLM)
INVESTIGATOR → behavioral analysis (checks user history)
DECISION     → final verdict (APPROVE / REVIEW / REJECT)

## Agent Pipeline
Transaction → DETECTOR → INVESTIGATOR → DECISION → Supabase → Dashboard

## Tech Stack
- Python 3.11 (conda env: fraudsentinel)
- LangGraph → agent pipeline orchestration
- LangChain + langchain-openai → LLM wrappers
- FastAPI + uvicorn → REST API
- Supabase → database + pgvector (vector memory)
- Streamlit → NOT used (replaced by Stitch UI)
- Google Stitch → generated the dashboard HTML/CSS

## LLM Setup
Provider: NVIDIA NIM (free)
Base URL: https://integrate.api.nvidia.com/v1
All agents use: meta/llama-3.3-70b-instruct
Fallback: OpenRouter (rate limited, use sparingly)
Key: in .env as NVIDIA_API_KEY

## Folder Structure
```
fraudsentinel/
├── agents/
│   ├── detector.py        ← rule-based + LLM risk scorer
│   ├── investigator.py    ← history lookup + reasoning
│   └── decision.py        ← final verdict + explanation
├── graph/
│   └── pipeline.py        ← LangGraph StateGraph wiring
├── memory/
│   ├── short_term.py      ← session state dict
│   └── long_term.py       ← Supabase + pgvector
├── api/
│   └── main.py            ← FastAPI endpoints
├── dashboard/
│   ├── templates/
│   │   ├── index.html       ← Main dashboard (from Stitch)
│   │   ├── transaction.html ← Transaction detail (from Stitch)
│   │   └── user.html        ← User profile (from Stitch)
│   └── static/
│       ├── css/
│       ├── js/
│       └── assets/
├── tools/
│   └── transaction_tools.py
├── supabase/
│   └── schema.sql
├── .env                   ← API keys (never commit)
├── requirements.txt
├── test_models.py         ← verified NVIDIA working ✅
└── CLAUDE.md              ← this file
```

## Supabase Tables (to be created)
- transactions      → all incoming transactions
- users             → user profiles + behavior patterns
- agent_decisions   → DETECTOR/INVESTIGATOR/DECISION outputs
- fraud_patterns    → known fraud embeddings (pgvector)

## Dashboard Connection Map
Stats numbers    ← Supabase transactions table
Transaction rows ← Supabase live query (every 5s)
Risk scores      ← DETECTOR agent output
Status badges    ← DECISION agent verdict
Agent activity   ← LangGraph pipeline logs
Agent status     ← FastAPI health endpoint
Chart bars       ← Supabase hourly aggregation

## Dashboard HTML Files
- All 3 screens are static HTML from Google Stitch
- Data is currently hardcoded
- Will be connected via fetch() calls to FastAPI
- FastAPI serves the HTML at localhost:8000

## Hard Rules
- Never commit .env
- Always use: conda activate fraudsentinel
- Use `python` not `python3`
- Agent pipeline order: DETECTOR first, always
- Supabase writes happen AFTER decision is made

## Current Status
✅ Environment set up (conda, Python 3.11)
✅ Dependencies installed (requirements.txt)
✅ NVIDIA models confirmed working
✅ Dashboard UI built (Google Stitch, 3 screens)
✅ CLAUDE.md created
⬜ Supabase schema (next session)
⬜ DETECTOR agent
⬜ Memory layer
⬜ INVESTIGATOR + DECISION agents
⬜ LangGraph pipeline
⬜ FastAPI endpoints
⬜ Connect dashboard to real data

## Next Task
Create Supabase schema in supabase/schema.sql
Tables: transactions, users, agent_decisions, fraud_patterns
Enable pgvector extension for fraud_patterns table
