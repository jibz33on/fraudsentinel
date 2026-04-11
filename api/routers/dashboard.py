from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

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
    try:
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
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch stats", "detail": str(e)})


@router.get("/transactions")
def get_transactions():
    try:
        rows = list_decisions(
            select="transaction_id,detector_score,decision_verdict,decision_confidence,created_at",
            limit=50,
            filters={"status": "eq.complete"},
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
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch transactions", "detail": str(e)})


@router.get("/transaction/{transaction_id}")
def get_transaction_detail(transaction_id: str):
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch transaction", "detail": str(e)})


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
