from pydantic import BaseModel


class TransactionRequest(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    country: str
    hour: int
    merchant: str
    method: str


class AnalyzeResponse(BaseModel):
    transaction_id: str
    verdict: str
    confidence: int
    reason: str
