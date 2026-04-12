"""
db/contracts.py
Data shape contracts for every db/ function return type.

Why: Without this, callers guess what keys exist.
     With this, every field is explicit and type-checked.

Usage:
    from db.contracts import TransactionRow, UserRow, DecisionRow
"""

from typing import Optional
from typing_extensions import TypedDict


class TransactionRow(TypedDict):
    id:           str
    user_id:      str
    amount:       float
    currency:     str
    merchant:     str
    location:     str
    ip_address:   str
    device:       str
    status:       str
    created_at:   str


class UserRow(TypedDict):
    id:                str
    name:              str
    email:             str
    avg_spend:         float
    usual_location:    str
    usual_hours:       str
    transaction_count: int
    account_age_days:  int
    risk_profile:      str
    created_at:        str


class DecisionRow(TypedDict):
    id:                       str
    transaction_id:           str
    detector_score:           Optional[int]
    detector_flags:           Optional[list]
    investigator_summary:     Optional[str]
    investigator_deviation:   Optional[int]
    decision_verdict:         Optional[str]
    decision_confidence:      Optional[int]
    decision_reason:          Optional[str]
    detector_duration_ms:     Optional[int]
    investigator_duration_ms: Optional[int]
    decision_duration_ms:     Optional[int]
    embedding:                Optional[list]
    status:                   str
    created_at:               str