from typing import TypedDict


class FraudState(TypedDict):
    # Transaction fields
    transaction_id: str
    user_id: str
    amount: float
    country: str
    hour: int
    merchant: str
    method: str

    # DETECTOR output
    detector_score: int
    detector_flags: list[str]
    detector_verdict: str

    # INVESTIGATOR output
    investigator_summary: str
    investigator_deviation: int

    # DECISION output
    decision_verdict: str
    decision_confidence: int
    decision_reason: str
