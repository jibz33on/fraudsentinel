# 🛡️ FraudSentinel

### **Autonomous Multi-Agent Fraud Detection System**

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange?style=flat-square)
![NVIDIA](https://img.shields.io/badge/LLM-NVIDIA_NIM-green?style=flat-square)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi)
![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E?style=flat-square&logo=supabase)

FraudSentinel is an advanced, autonomous fraud detection engine that leverages a multi-agent orchestrated pipeline to analyze, investigate, and adjudicate financial transactions in real-time. By combining behavioral analysis with generative reasoning, it provides not just a risk score, but a full audit trail of *why* a decision was made.

---

## 🏗️ Architecture

```text
┌───────────────┐      ┌─────────────┐      ┌──────────────────────────┐
│  Transaction  │─────▶│  FastAPI    │─────▶│    LangGraph Pipeline    │
└───────────────┘      └─────────────┘      └─────────────┬────────────┘
                                                          │
          ┌──────────────────────┬────────────────────────┴───────────────────────┐
          │                      │                                                │
  ┌───────▼───────┐      ┌───────▼───────┐                        ┌───────────────▼┐
  │   DETECTOR    │      │ INVESTIGATOR  │                        │    DECISION     │
  │ (Risk Scoring)│      │  (Behavior)   │                        │   (Adjudicator) │
  └───────┬───────┘      └───────┬───────┘                        └───────┬────────┘
          │                      │                                        │
          └──────────────────────┴───▶  Stored in Supabase (pgvector)  ◀──┘
                                     │
                                     ▼
                        ┌──────────────────────────┐
                        │  Google Stitch Dashboard │
                        │    (Live Reasoning)      │
                        └──────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.11 |
| **Orchestration** | LangGraph (Stateful Multi-Agent Workflows) |
| **LLM Inference** | NVIDIA NIM (Llama 3.3 70B) with OpenRouter Fallback |
| **Framework** | LangChain |
| **API** | FastAPI (Asynchronous REST) |
| **Database** | Supabase (PostgreSQL + pgvector for memory) |
| **Frontend** | Google Stitch (Tailwind CSS/HTML5 Dashboard) |

---

## 🌟 Key Features

- **Multi-Agent Adjudication:** Three specialized agents (Detector, Investigator, Decision) collaborate to minimize false positives.
- **Explainable AI (XAI):** A dedicated reasoning panel in the dashboard shows the thought process of each agent per transaction.
- **Resilient Inference:** Centralized LLM router with automatic failover from NVIDIA NIM to OpenRouter.
- **Behavioral Profiling:** Uses vector memory to compare current transaction patterns against historical user behavior.
- **Real-time Monitoring:** Live telemetry via a 3-screen dashboard (Overview, Detailed Reasoning, User Profiles).
- **Fault-Tolerant Design:** Comprehensive error handling and async processing for high-throughput environments.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- Supabase Account
- NVIDIA NIM API Key (or OpenRouter)

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/jibz33on/fraudsentinel.git
cd fraudsentinel

# Install dependencies
pip install -r requirements.md

# Configure environment
cp .env.example .env
# Update .env with your API keys and Supabase credentials
```

### 3. Run
```bash
# Start the FastAPI server
uvicorn main:app --reload

# The dashboard will be accessible at http://localhost:8000/dashboard
```

---

## 📁 Project Structure

```text
fraudsentinel/
├── agents/             # Agent logic (Detector, Investigator, Decision)
├── graph/              # LangGraph state machine definitions
├── api/                # FastAPI routes and middleware
├── memory/             # Vector store and behavioral history logic
├── dashboard/          # Google Stitch UI components & static files
├── core/               # LLM Router, Logger, and Config
├── CLAUDE.md           # Project context and guidelines
└── README.md
```

---

## 🧠 How It Works

1.  **DETECTOR:** Performs a rapid horizontal scan of the transaction metadata to generate a raw risk score (0-100).
2.  **INVESTIGATOR:** Queries the `pgvector` memory to pull historical user patterns and identifies anomalies in current behavior.
3.  **DECISION:** Synthesizes inputs from both prior agents to issue a final verdict: `APPROVE`, `REVIEW`, or `REJECT`.

---

## 🛡️ System Design Patterns

- **Neuro-Symbolic Logic:** Combining LLM reasoning with strict numeric thresholds and database constraints.
- **Provider Redundancy:** Automatic fallback mechanisms ensure 99.9% uptime for the agent pipeline.
- **Asynchronous Processing:** Non-blocking transaction ingestion via message queues/async tasks.
- **Schema Enforcement:** Strict data validation using Pydantic to prevent pipeline drift.

---

## 🗺️ Roadmap

- [ ] Implementation of self-correcting feedback loops from manual reviews.
- [ ] Integration with real-time payment gateways (Stripe/Adyen).
- [ ] Advanced Graph Analysis for identifying fraud rings.
- [ ] Mobile-native dashboard companion.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
