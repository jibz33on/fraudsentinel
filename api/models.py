from pydantic import BaseModel


class TransactionRequest(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    country: str
    hour: int
    merchant: str
    method: str
    currency: str = "USD"
    ip_address: str = ""
    ip_country: str = ""
    device: str = "Unknown"


class AnalyzeResponse(BaseModel):
    transaction_id: str
    verdict: str
    confidence: int
    reason: str
