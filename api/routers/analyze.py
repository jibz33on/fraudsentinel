import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api.models import TransactionRequest, AnalyzeResponse
from db.client import supabase
from db.users import increment_transaction_count
from graph.pipeline import run_pipeline

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: TransactionRequest):
    try:
        supabase.table("transactions").insert({
            "id":         request.transaction_id,
            "user_id":    request.user_id,
            "amount":     request.amount,
            "currency":   request.currency,
            "merchant":   request.merchant,
            "location":   request.country,
            "ip_address": request.ip_address,
            "device":     request.device,
            "status":     "complete",
            "created_at": datetime.utcnow().isoformat(),
        }).execute()

        increment_transaction_count(request.user_id)

        result = run_pipeline(request.model_dump())
        return AnalyzeResponse(
            transaction_id=result["transaction_id"],
            verdict=result["decision_verdict"],
            confidence=result["decision_confidence"],
            reason=result["decision_reason"],
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
