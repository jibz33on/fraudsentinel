import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api.models import TransactionRequest, AnalyzeResponse
from graph.pipeline import run_pipeline

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: TransactionRequest):
    try:
        result = run_pipeline(request.model_dump())
        return AnalyzeResponse(
            transaction_id=result["transaction_id"],
            verdict=result["decision_verdict"],
            confidence=result["decision_confidence"],
            reason=result["decision_reason"],
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
