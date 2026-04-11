# DB Layer Refactor — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract all Supabase I/O into a dedicated `db/` layer so agents, pipeline, and API routers have a single, shared database client with zero duplicated HTTP setup code.

**Architecture:** Create `db/client.py` as the single source of truth for Supabase credentials and HTTP helpers. Four table modules (`decisions`, `transactions`, `users`) expose named functions. All existing callers (`profiler.py`, `pipeline.py`, `dashboard.py`) are then migrated to use these functions, removing their duplicated `_URL/_KEY/_HEADERS` blocks and raw `requests` calls.

**Tech Stack:** Python 3.11, requests, python-dotenv, FastAPI, conda env `fraudsentinel`

**Verification command (run after every task):**
```bash
conda run -n fraudsentinel python -c "from api.main import app; print('✅ imports OK')"
```

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `db/__init__.py` | Empty package marker |
| Create | `db/client.py` | Shared Supabase URL, key, headers; `get()`, `post()`, `patch()` helpers |
| Create | `db/decisions.py` | `insert_decision()`, `patch_decision()`, `get_decision()`, `list_decisions()` |
| Create | `db/transactions.py` | `get_transaction()`, `list_transactions()` |
| Create | `db/users.py` | `get_user()`, `get_user_basics()` |
| Modify | `agents/investigator/profiler.py` | Replace raw requests with `db.users` + `db.transactions` |
| Move | `agents/shared/embed.py` → `tools/embed.py` | No logic change, just new path |
| Modify | `graph/pipeline.py` | Replace raw requests with `db.decisions`; update embed import |
| Modify | `api/routers/dashboard.py` | Replace `_supabase_get()` and duplicated headers with `db/` calls |
| Create | `tests/` | Move all `test_*.py` from root |

---

## Task 1: Create `db/` package with `client.py`

**Files:**
- Create: `db/__init__.py`
- Create: `db/client.py`

- [ ] **Step 1: Create the package**

```bash
mkdir -p /Users/jibinkunjumon/fraudsentinel/db
touch /Users/jibinkunjumon/fraudsentinel/db/__init__.py
```

- [ ] **Step 2: Write `db/client.py`**

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

_URL = os.environ["SUPABASE_URL"]
_KEY = os.environ["SUPABASE_SERVICE_KEY"]

_READ_HEADERS = {
    "apikey": _KEY,
    "Authorization": f"Bearer {_KEY}",
}

_WRITE_HEADERS = {
    **_READ_HEADERS,
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def get(table: str, params: dict = None) -> list:
    resp = requests.get(
        f"{_URL}/rest/v1/{table}",
        headers=_READ_HEADERS,
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def post(table: str, data: dict) -> dict:
    resp = requests.post(
        f"{_URL}/rest/v1/{table}",
        headers=_WRITE_HEADERS,
        json=data,
        timeout=30,
    )
    resp.raise_for_status()
    result = resp.json()
    return result[0] if isinstance(result, list) else result


def patch(table: str, params: dict, data: dict) -> None:
    resp = requests.patch(
        f"{_URL}/rest/v1/{table}",
        headers=_WRITE_HEADERS,
        params=params,
        json=data,
        timeout=30,
    )
    resp.raise_for_status()
```

- [ ] **Step 3: Verify import**

```bash
conda run -n fraudsentinel python -c "from db.client import get, post, patch; print('✅ db.client OK')"
```

Expected: `✅ db.client OK`

- [ ] **Step 4: Verify server still imports**

```bash
conda run -n fraudsentinel python -c "from api.main import app; print('✅ imports OK')"
```

Expected: `✅ imports OK`

---

## Task 2: Create `db/decisions.py`

**Files:**
- Create: `db/decisions.py`

- [ ] **Step 1: Write `db/decisions.py`**

```python
from db import client


def insert_decision(row: dict) -> dict:
    """Insert a new agent_decisions row. Returns inserted row."""
    return client.post("agent_decisions", row)


def patch_decision(transaction_id: str, data: dict) -> None:
    """Update fields on an existing agent_decisions row."""
    client.patch(
        "agent_decisions",
        {"transaction_id": f"eq.{transaction_id}"},
        data,
    )


def get_decision(transaction_id: str) -> dict | None:
    """Fetch a single agent_decisions row by transaction_id."""
    rows = client.get("agent_decisions", {
        "transaction_id": f"eq.{transaction_id}",
        "select": "*",
        "limit": 1,
    })
    return rows[0] if rows else None


def list_decisions(select: str = "*", limit: int = 50) -> list:
    """List recent agent_decisions rows ordered by created_at desc."""
    return client.get("agent_decisions", {
        "select": select,
        "order": "created_at.desc",
        "limit": limit,
    })
```

- [ ] **Step 2: Verify import**

```bash
conda run -n fraudsentinel python -c "from db.decisions import insert_decision, patch_decision, get_decision, list_decisions; print('✅ db.decisions OK')"
```

Expected: `✅ db.decisions OK`

- [ ] **Step 3: Verify server still imports**

```bash
conda run -n fraudsentinel python -c "from api.main import app; print('✅ imports OK')"
```

---

## Task 3: Create `db/transactions.py` and `db/users.py`

**Files:**
- Create: `db/transactions.py`
- Create: `db/users.py`

- [ ] **Step 1: Write `db/transactions.py`**

```python
from db import client


def get_transaction(txn_id: str) -> dict | None:
    """Fetch a single transaction row by id."""
    rows = client.get("transactions", {
        "id": f"eq.{txn_id}",
        "select": "amount,merchant,location,currency,user_id",
        "limit": 1,
    })
    return rows[0] if rows else None


def list_transactions(user_id: str, limit: int = 20) -> list:
    """Fetch recent transactions for a user, ordered by created_at desc."""
    return client.get("transactions", {
        "user_id": f"eq.{user_id}",
        "select": "amount,location,created_at,merchant",
        "order": "created_at.desc",
        "limit": limit,
    })
```

- [ ] **Step 2: Write `db/users.py`**

```python
from db import client


def get_user(user_id: str, select: str = "*") -> dict | None:
    """Fetch a single user row by id."""
    rows = client.get("users", {
        "id": f"eq.{user_id}",
        "select": select,
        "limit": 1,
    })
    return rows[0] if rows else None


def get_user_basics(user_id: str) -> dict | None:
    """Fetch only the fields needed for behavioral profiling."""
    return get_user(user_id, select="avg_spend,account_age_days,risk_profile")
```

- [ ] **Step 3: Verify imports**

```bash
conda run -n fraudsentinel python -c "
from db.transactions import get_transaction, list_transactions
from db.users import get_user, get_user_basics
print('✅ db.transactions + db.users OK')
"
```

Expected: `✅ db.transactions + db.users OK`

- [ ] **Step 4: Verify server still imports**

```bash
conda run -n fraudsentinel python -c "from api.main import app; print('✅ imports OK')"
```

---

## Task 4: Move `embed.py` from `agents/shared/` to `tools/`

**Files:**
- Move: `agents/shared/embed.py` → `tools/embed.py`
- Modify: `graph/pipeline.py` line 14 (import)

- [ ] **Step 1: Copy embed.py to tools/**

```bash
cp /Users/jibinkunjumon/fraudsentinel/agents/shared/embed.py \
   /Users/jibinkunjumon/fraudsentinel/tools/embed.py
```

- [ ] **Step 2: Update import in `graph/pipeline.py`**

Change line 14:
```python
# Before
from agents.shared.embed import embed

# After
from tools.embed import embed
```

- [ ] **Step 3: Verify import**

```bash
conda run -n fraudsentinel python -c "from tools.embed import embed; print('✅ tools.embed OK')"
```

- [ ] **Step 4: Verify server still imports**

```bash
conda run -n fraudsentinel python -c "from api.main import app; print('✅ imports OK')"
```

- [ ] **Step 5: Delete old file**

```bash
rm /Users/jibinkunjumon/fraudsentinel/agents/shared/embed.py
```

- [ ] **Step 6: Verify server still imports after deletion**

```bash
conda run -n fraudsentinel python -c "from api.main import app; print('✅ imports OK')"
```

---

## Task 5: Refactor `profiler.py` to use `db/` layer

**Files:**
- Modify: `agents/investigator/profiler.py`

- [ ] **Step 1: Rewrite `profiler.py`**

Replace the entire file content:

```python
from datetime import datetime
from db.users import get_user_basics
from db.transactions import list_transactions


def get_user_profile(user_id: str) -> dict:
    user_row = get_user_basics(user_id) or {}

    avg_spend = user_row.get("avg_spend", 0.0)
    account_age_days = user_row.get("account_age_days", 0)

    txns = list_transactions(user_id)

    if not txns:
        return {
            "avg_amount": avg_spend,
            "avg_spend": avg_spend,
            "account_age_days": account_age_days,
            "known_countries": [],
            "known_merchants": [],
            "typical_hours": [],
            "transaction_count": 0,
        }

    amounts = [t["amount"] for t in txns if t.get("amount") is not None]
    avg_amount = sum(amounts) / len(amounts) if amounts else avg_spend

    known_countries = list({
        t["location"].split(",")[-1].strip()
        for t in txns
        if t.get("location")
    })

    known_merchants = list({t["merchant"] for t in txns if t.get("merchant")})

    typical_hours = list({
        datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")).hour
        for t in txns
        if t.get("created_at")
    })

    return {
        "avg_amount": avg_amount,
        "avg_spend": avg_spend,
        "account_age_days": account_age_days,
        "known_countries": known_countries,
        "known_merchants": known_merchants,
        "typical_hours": typical_hours,
        "transaction_count": len(txns),
    }


if __name__ == "__main__":
    profile = get_user_profile("55472a7d-8980-4777-b98d-e8b65e65d33c")
    for k, v in profile.items():
        print(f"  {k}: {v}")
```

- [ ] **Step 2: Verify import**

```bash
conda run -n fraudsentinel python -c "from agents.investigator.profiler import get_user_profile; print('✅ profiler OK')"
```

- [ ] **Step 3: Verify server still imports**

```bash
conda run -n fraudsentinel python -c "from api.main import app; print('✅ imports OK')"
```

---

## Task 6: Refactor `pipeline.py` to use `db/decisions.py`

**Files:**
- Modify: `graph/pipeline.py`

- [ ] **Step 1: Replace DB code in `pipeline.py`**

Replace the entire file:

```python
import os
import sys

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph

from graph.state import FraudState
from agents.detector.detector import DetectorAgent
from tools.embed import embed
from agents.investigator.profiler import get_user_profile
from agents.investigator.investigator import investigate
from agents.decision.decision import decide
from db.decisions import insert_decision, patch_decision

_detector = DetectorAgent()


def detector_node(state: FraudState) -> FraudState:
    transaction = {
        "id": state["transaction_id"],
        "user_id": state["user_id"],
        "amount": state["amount"],
        "country": state["country"],
        "hour": state["hour"],
        "merchant": state["merchant"],
        "method": state["method"],
    }
    result = _detector.analyze(transaction, {})

    score = result["risk_score"]
    verdict = result["verdict"]
    flags = result["flags"]

    embed_text = (
        f"verdict:{verdict} score:{score} flags:{flags} "
        f"country:{state['country']} amount:{state['amount']} hour:{state['hour']}"
    )
    embedding = embed(embed_text, input_type="passage")

    try:
        insert_decision({
            "transaction_id": state["transaction_id"],
            "detector_score": score,
            "detector_flags": flags,
            "embedding": str(embedding),
        })
    except Exception as e:
        print(f"[pipeline] detector insert failed: {e}")

    return {
        **state,
        "detector_score": score,
        "detector_flags": flags,
        "detector_verdict": verdict,
    }


def investigator_node(state: FraudState) -> dict:
    profile = get_user_profile(state["user_id"])
    transaction = {
        "user_id": state["user_id"],
        "amount": state["amount"],
        "country": state["country"],
        "hour": state["hour"],
        "merchant": state["merchant"],
        "method": state["method"],
    }
    result = investigate(transaction, profile)

    try:
        patch_decision(state["transaction_id"], {
            "investigator_summary": result["summary"],
            "investigator_deviation": result["deviation_score"],
        })
    except Exception as e:
        print(f"[pipeline] investigator patch failed: {e}")

    return {
        **state,
        "investigator_summary": result["summary"],
        "investigator_deviation": result["deviation_score"],
    }


def decision_node(state: FraudState) -> dict:
    detector = {
        "detector_score": state["detector_score"],
        "detector_flags": state["detector_flags"],
        "detector_verdict": state["detector_verdict"],
    }
    investigator = {
        "investigator_deviation": state["investigator_deviation"],
        "investigator_summary": state["investigator_summary"],
    }
    result = decide(detector, investigator)

    try:
        patch_decision(state["transaction_id"], {
            "decision_verdict": result["verdict"],
            "decision_confidence": result["confidence"],
            "decision_reason": result["reason"],
        })
    except Exception as e:
        print(f"[pipeline] decision patch failed: {e}")

    return {
        **state,
        "decision_verdict": result["verdict"],
        "decision_confidence": result["confidence"],
        "decision_reason": result["reason"],
    }


def _build_graph():
    graph = StateGraph(FraudState)
    graph.add_node("detector", detector_node)
    graph.add_node("investigator", investigator_node)
    graph.add_node("decision", decision_node)
    graph.set_entry_point("detector")
    graph.add_edge("detector", "investigator")
    graph.add_edge("investigator", "decision")
    graph.set_finish_point("decision")
    return graph.compile()


_graph = _build_graph()


def run_pipeline(transaction: dict) -> FraudState:
    initial_state: FraudState = {
        "transaction_id": transaction.get("transaction_id", transaction.get("id", "unknown")),
        "user_id": transaction.get("user_id", ""),
        "amount": transaction.get("amount", 0.0),
        "country": transaction.get("country", ""),
        "hour": transaction.get("hour", 0),
        "merchant": transaction.get("merchant", ""),
        "method": transaction.get("method", ""),
        "detector_score": 0,
        "detector_flags": [],
        "detector_verdict": "",
        "investigator_summary": "",
        "investigator_deviation": 0,
        "decision_verdict": "",
        "decision_confidence": 0,
        "decision_reason": "",
    }
    return _graph.invoke(initial_state)


if __name__ == "__main__":
    test_txn = {
        "transaction_id": "txn-4821",
        "user_id": "55472a7d-8980-4777-b98d-e8b65e65d33c",
        "amount": 4500.0,
        "country": "NG",
        "hour": 3,
        "merchant": "Crypto Exchange XY",
        "method": "crypto",
    }
    final_state = run_pipeline(test_txn)
    print("\n=== Final State ===")
    for k, v in final_state.items():
        print(f"  {k}: {v}")
```

- [ ] **Step 2: Verify import**

```bash
conda run -n fraudsentinel python -c "from graph.pipeline import run_pipeline; print('✅ pipeline OK')"
```

- [ ] **Step 3: Verify server still imports**

```bash
conda run -n fraudsentinel python -c "from api.main import app; print('✅ imports OK')"
```

---

## Task 7: Refactor `dashboard.py` to use `db/` layer

**Files:**
- Modify: `api/routers/dashboard.py`

- [ ] **Step 1: Rewrite `dashboard.py`**

Replace the entire file:

```python
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from db.decisions import get_decision, list_decisions
from db.transactions import get_transaction
from db.users import get_user

router = APIRouter()


# ─── HTML pages ───────────────────────────────────────────────────────────────

@router.get("/")
def index():
    return FileResponse("dashboard/templates/index.html")


@router.get("/transaction")
def transaction_page():
    return FileResponse("dashboard/templates/transaction.html")


@router.get("/user")
def user_page():
    return FileResponse("dashboard/templates/user.html")


# ─── Data endpoints ───────────────────────────────────────────────────────────

@router.get("/stats")
def get_stats():
    rows = list_decisions(select="decision_verdict")

    total = len(rows)
    approved = sum(1 for r in rows if r.get("decision_verdict") == "APPROVED")
    rejected = sum(1 for r in rows if r.get("decision_verdict") == "REJECTED")
    review   = sum(1 for r in rows if r.get("decision_verdict") == "REVIEW")
    fraud_rate = round((rejected / total * 100), 1) if total else 0.0

    return {
        "total":      total,
        "approved":   approved,
        "rejected":   rejected,
        "review":     review,
        "flagged":    review,
        "fraud_rate": fraud_rate,
    }


@router.get("/transactions")
def get_transactions():
    rows = list_decisions(
        select="transaction_id,detector_score,decision_verdict,decision_confidence,created_at",
        limit=50,
    )

    result = []
    for row in rows:
        txn  = get_transaction(row["transaction_id"]) or {}
        user = get_user(txn["user_id"], select="name") if txn.get("user_id") else {}

        result.append({
            "id":         row.get("transaction_id"),
            "user_name":  user.get("name", "Unknown") if user else "Unknown",
            "merchant":   txn.get("merchant", ""),
            "currency":   txn.get("currency", "USD"),
            "amount":     txn.get("amount", 0),
            "location":   txn.get("location", ""),
            "timestamp":  row.get("created_at"),
            "risk_score": row.get("detector_score", 0),
            "status":     row.get("decision_verdict", ""),
        })

    seen = set()
    deduped = []
    for row in result:
        if row["id"] not in seen:
            seen.add(row["id"])
            deduped.append(row)
    return deduped


@router.get("/transaction/{transaction_id}")
def get_transaction_detail(transaction_id: str):
    row = get_decision(transaction_id)
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {
        "id": row["transaction_id"],
        "decision": {
            "detector": {
                "risk_score": row.get("detector_score"),
                "flags":      row.get("detector_flags"),
            },
            "investigator": {
                "summary":       row.get("investigator_summary"),
                "deviation_score": row.get("investigator_deviation"),
            },
            "decision": {
                "verdict":    row.get("decision_verdict"),
                "confidence": row.get("decision_confidence"),
                "reason":     row.get("decision_reason"),
            },
        },
        "created_at": row.get("created_at"),
    }


@router.get("/users/{user_id}")
def get_user_detail(user_id: str):
    row = get_user(user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row


@router.get("/activity")
def get_activity():
    try:
        rows = list_decisions(
            select="transaction_id,decision_verdict,decision_confidence,created_at",
            limit=10,
        )
        results = [
            {
                "id":        row["transaction_id"] + "-" + row["created_at"],
                "agent":     "DECISION",
                "timestamp": row["created_at"],
                "message":   f"{row['decision_verdict']} — confidence {row['decision_confidence']}%",
            }
            for row in rows
        ]

        seen = set()
        deduped = []
        for row in results:
            if row["id"] not in seen:
                seen.add(row["id"])
                deduped.append(row)
        return deduped
    except Exception as e:
        print(f"[activity] error: {e}")
        return []
```

- [ ] **Step 2: Verify import**

```bash
conda run -n fraudsentinel python -c "from api.routers.dashboard import router; print('✅ dashboard OK')"
```

- [ ] **Step 3: Verify server still imports**

```bash
conda run -n fraudsentinel python -c "from api.main import app; print('✅ imports OK')"
```

---

## Task 8: Move test files to `tests/`

**Files:**
- Create: `tests/` directory
- Move: `test_connection.py`, `test_detector.py`, `test_groq.py`, `test_models.py`, `test_supabase.py`

- [ ] **Step 1: Create tests directory and move files**

```bash
mkdir -p /Users/jibinkunjumon/fraudsentinel/tests
cd /Users/jibinkunjumon/fraudsentinel
mv test_connection.py test_detector.py test_groq.py test_models.py test_supabase.py tests/
touch tests/__init__.py
```

- [ ] **Step 2: Verify server still imports**

```bash
conda run -n fraudsentinel python -c "from api.main import app; print('✅ imports OK')"
```

- [ ] **Step 3: Verify test files are importable from new location**

```bash
conda run -n fraudsentinel python -c "import tests.test_detector; print('✅ tests OK')"
```

---

## Self-Review

**Spec coverage:**
- ✅ `db/` layer created (Tasks 1–3)
- ✅ `embed.py` moved to `tools/` (Task 4)
- ✅ `profiler.py` migrated (Task 5)
- ✅ `pipeline.py` migrated (Task 6)
- ✅ `dashboard.py` migrated (Task 7)
- ✅ test files moved (Task 8)
- ✅ Server verified after every task

**Type consistency:**
- `list_decisions(select, limit)` — used consistently in Tasks 2, 7
- `patch_decision(transaction_id, data)` — used consistently in Tasks 2, 6
- `get_user(user_id, select)` — used consistently in Tasks 3, 7
- `get_transaction(txn_id)` — used consistently in Tasks 3, 7

**No placeholders:** All code blocks are complete.
