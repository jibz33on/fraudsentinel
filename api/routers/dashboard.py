from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from db.decisions import get_decision, list_decisions, patch_decision
from db.transactions import get_transaction
from db.users import get_user, list_users

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
            select="transaction_id,detector_score,detector_flags,decision_verdict,decision_confidence,created_at",
            limit=50,
            filters={"status": "eq.complete"},
        )

        result = []
        for row in rows:
            txn  = get_transaction(row["transaction_id"]) or {}
            user = get_user(txn["user_id"], select="name") if txn.get("user_id") else {}
            tid  = row.get("transaction_id")

            result.append({
                "transaction": {
                    "id":         tid,
                    "user_id":    txn.get("user_id", ""),
                    "user_name":  user.get("name", "Unknown") if user else "Unknown",
                    "amount":     txn.get("amount", 0),
                    "currency":   txn.get("currency", "USD"),
                    "merchant":   txn.get("merchant", ""),
                    "location":   txn.get("location", ""),
                    "ip_address": txn.get("ip_address", ""),
                    "device":     txn.get("device", ""),
                    "timestamp":  txn.get("created_at", row.get("created_at", "")),
                    "risk_score": row.get("detector_score", 0),
                    "status":     row.get("decision_verdict", "APPROVED"),
                    "created_at": txn.get("created_at", row.get("created_at", "")),
                },
                "decision": {
                    "transaction_id": tid,
                    "detector": {
                        "risk_score": row.get("detector_score", 0),
                        "flags":      row.get("detector_flags") or [],
                    },
                    "investigator": {
                        "summary":         "",
                        "deviation_score": 0,
                    },
                    "decision": {
                        "verdict":    row.get("decision_verdict", "APPROVED"),
                        "confidence": row.get("decision_confidence", 0),
                        "reason":     "",
                    },
                } if row.get("decision_verdict") else None,
            })

        seen = set()
        deduped = []
        for item in result:
            tid = item["transaction"]["id"]
            if tid not in seen:
                seen.add(tid)
                deduped.append(item)
        return deduped
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch transactions", "detail": str(e)})


@router.get("/transaction/{transaction_id}")
def get_transaction_detail(transaction_id: str):
    try:
        row = get_decision(transaction_id)
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        txn  = get_transaction(transaction_id) or {}
        user = get_user(txn["user_id"], select="name") if txn.get("user_id") else {}
        return {
            "id": transaction_id,
            "transaction": {
                "id":         transaction_id,
                "user_id":    txn.get("user_id", ""),
                "user_name":  user.get("name", "Unknown") if user else "Unknown",
                "amount":     txn.get("amount", 0),
                "currency":   txn.get("currency", "USD"),
                "merchant":   txn.get("merchant", ""),
                "location":   txn.get("location", ""),
                "ip_address": txn.get("ip_address", ""),
                "device":     txn.get("device", ""),
                "timestamp":  txn.get("created_at", row.get("created_at", "")),
                "risk_score": row.get("detector_score", 0),
                "status":     row.get("decision_verdict", ""),
                "created_at": txn.get("created_at", row.get("created_at", "")),
            },
            "decision": {
                "transaction_id": transaction_id,
                "detector": {
                    "risk_score": row.get("detector_score"),
                    "flags":      row.get("detector_flags") or [],
                },
                "investigator": {
                    "summary":         row.get("investigator_summary"),
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


@router.get("/users")
def get_users():
    try:
        return list_users()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch users", "detail": str(e)})


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


@router.get("/analytics")
def get_analytics():
    try:
        from datetime import datetime, timedelta, timezone

        rows = list_decisions(
            select="decision_verdict,detector_score,investigator_deviation,decision_confidence,detector_flags,created_at",
            limit=1000,
            filters={"status": "eq.complete"},
        )

        complete = [r for r in rows if r.get("decision_verdict")]
        total = len(complete)

        # Verdict breakdown
        approved = sum(1 for r in complete if r.get("decision_verdict") == "APPROVED")
        rejected = sum(1 for r in complete if r.get("decision_verdict") == "REJECTED")
        review   = sum(1 for r in complete if r.get("decision_verdict") == "REVIEW")

        # Avg scores
        def avg(vals):
            clean = [v for v in vals if v is not None]
            return round(sum(clean) / len(clean), 1) if clean else 0.0

        avg_detector     = avg([r.get("detector_score") for r in complete])
        avg_deviation    = avg([r.get("investigator_deviation") for r in complete])
        avg_confidence   = avg([r.get("decision_confidence") for r in complete])

        # Top flags
        flag_counts: dict = {}
        for r in complete:
            flags = r.get("detector_flags") or []
            for f in flags:
                flag_counts[f] = flag_counts.get(f, 0) + 1
        top_flags = sorted(
            [{"flag": k, "count": v} for k, v in flag_counts.items()],
            key=lambda x: x["count"],
            reverse=True,
        )[:5]

        # 7-day trend
        today = datetime.now(timezone.utc).date()
        days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
        trend = []
        for day in days:
            day_str = day.isoformat()
            day_rows = [
                r for r in complete
                if r.get("created_at", "").startswith(day_str)
            ]
            trend.append({
                "date":     day_str,
                "total":    len(day_rows),
                "approved": sum(1 for r in day_rows if r.get("decision_verdict") == "APPROVED"),
                "review":   sum(1 for r in day_rows if r.get("decision_verdict") == "REVIEW"),
                "rejected": sum(1 for r in day_rows if r.get("decision_verdict") == "REJECTED"),
            })

        return {
            "verdict_breakdown": {
                "total":      total,
                "approved":   approved,
                "review":     review,
                "rejected":   rejected,
                "fraud_rate": round(rejected / total * 100, 1) if total else 0.0,
            },
            "avg_scores": {
                "detector_score":         avg_detector,
                "investigator_deviation": avg_deviation,
                "decision_confidence":    avg_confidence,
            },
            "top_flags": top_flags,
            "daily_trend": trend,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch analytics", "detail": str(e)})


@router.post("/transaction/{transaction_id}/approve")
def approve_transaction(transaction_id: str):
    try:
        row = get_decision(transaction_id)
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        patch_decision(transaction_id, {"decision_verdict": "APPROVED"})
        return {"transaction_id": transaction_id, "verdict": "APPROVED"}
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/transaction/{transaction_id}/reject")
def reject_transaction(transaction_id: str):
    try:
        row = get_decision(transaction_id)
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        patch_decision(transaction_id, {"decision_verdict": "REJECTED"})
        return {"transaction_id": transaction_id, "verdict": "REJECTED"}
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
