import os
import requests as http

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

_URL = os.environ["SUPABASE_URL"]
_KEY = os.environ["SUPABASE_SERVICE_KEY"]
_HEADERS = {
    "apikey": _KEY,
    "Authorization": f"Bearer {_KEY}",
}


def _supabase_get(path: str, params: dict = None) -> list | dict:
    resp = http.get(f"{_URL}/rest/v1/{path}", headers=_HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


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
    rows = _supabase_get("agent_decisions", {"select": "decision_verdict"})

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
    # Step 1: fetch agent_decisions
    rows = _supabase_get("agent_decisions", {
        "select": "transaction_id,detector_score,decision_verdict,decision_confidence,created_at",
        "order":  "created_at.desc",
        "limit":  50,
    })

    result = []
    for row in rows:
        # Step 2: fetch matching transaction
        txn_rows = _supabase_get("transactions", {
            "id":     f"eq.{row['transaction_id']}",
            "select": "amount,merchant,location,currency,user_id",
            "limit":  1,
        })
        txn = txn_rows[0] if txn_rows else {}

        # Step 3: fetch matching user
        user = {}
        if txn.get("user_id"):
            user_rows = _supabase_get("users", {
                "id":     f"eq.{txn['user_id']}",
                "select": "name",
                "limit":  1,
            })
            user = user_rows[0] if user_rows else {}

        result.append({
            "id":         row.get("transaction_id"),
            "user_name":  user.get("name", "Unknown"),
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
def get_transaction(transaction_id: str):
    rows = _supabase_get("agent_decisions", {
        "transaction_id": f"eq.{transaction_id}",
        "select": "*",
        "limit":  1,
    })
    if not rows:
        raise HTTPException(status_code=404, detail="Transaction not found")
    row = rows[0]
    return {
        "id": row["transaction_id"],
        "decision": {
            "detector": {
                "risk_score": row.get("detector_score"),
                "flags":      row.get("detector_flags"),
            },
            "investigator": {
                "summary":   row.get("investigator_summary"),
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
def get_user(user_id: str):
    rows = _supabase_get("users", {
        "id":     f"eq.{user_id}",
        "select": "*",
        "limit":  1,
    })
    if not rows:
        raise HTTPException(status_code=404, detail="User not found")
    return rows[0]


@router.get("/activity")
def get_activity():
    try:
        rows = _supabase_get("agent_decisions", {
            "select": "transaction_id,decision_verdict,decision_confidence,created_at",
            "order":  "created_at.desc",
            "limit":  10,
        })
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
