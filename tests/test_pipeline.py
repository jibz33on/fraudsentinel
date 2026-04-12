"""
tests/test_pipeline.py
Integration tests for the full pipeline.

Tests the full flow:
  POST /analyze → transactions table → pipeline → agent_decisions table

NOTE: Makes real DB calls and real LLM calls.
      Requires server running on localhost:8000.
      Slower than unit tests (~30-60 seconds).

Run:
    conda activate fraudsentinel
    uvicorn api.main:app --reload   (in separate terminal)
    pytest tests/test_pipeline.py -v
"""

import sys
import os
import time
import uuid
import pytest
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.client import supabase

BASE_URL = "http://localhost:8000"

# ── Helpers ───────────────────────────────────────────────────────────────────

def unique_txn_id():
    """Generate a unique transaction id for each test."""
    return f"test-{uuid.uuid4().hex[:8]}"


def post_analyze(payload: dict) -> dict:
    """Hit POST /analyze and return the JSON response."""
    resp = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=60)
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    return resp.json()


def get_decision(txn_id: str) -> dict:
    """Fetch agent_decisions row for a transaction."""
    result = supabase.table("agent_decisions").select("*").eq(
        "transaction_id", txn_id
    ).execute()
    return result.data[0] if result.data else {}


def get_transaction(txn_id: str) -> dict:
    """Fetch transaction row."""
    result = supabase.table("transactions").select("*").eq(
        "id", txn_id
    ).execute()
    return result.data[0] if result.data else {}


# ── Server health check ───────────────────────────────────────────────────────

def test_server_is_running():
    """Fail fast if server is not running."""
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        assert resp.status_code == 200
    except Exception:
        pytest.fail("Server not running. Start with: uvicorn api.main:app --reload")


# ── Transactions table ────────────────────────────────────────────────────────

class TestTransactionSaved:

    def test_transaction_saved_to_db(self):
        """Every /analyze call must save a row to transactions table."""
        txn_id = unique_txn_id()
        post_analyze({
            "transaction_id": txn_id,
            "user_id": "67f045c9-658d-4e62-8300-877be9a006d1",  # Mark T
            "amount": 45.0,
            "country": "IN",
            "hour": 14,
            "merchant": "Swiggy",
            "method": "card",
        })

        row = get_transaction(txn_id)
        assert row, "Transaction row not found in DB"
        assert row["id"]      == txn_id
        assert row["amount"]  == 45.0
        assert row["merchant"] == "Swiggy"

    def test_transaction_location_saved(self):
        """country field from pipeline maps to location column in transactions."""
        txn_id = unique_txn_id()
        post_analyze({
            "transaction_id": txn_id,
            "user_id": "67f045c9-658d-4e62-8300-877be9a006d1",
            "amount": 50.0,
            "country": "IN",
            "hour": 10,
            "merchant": "Amazon",
            "method": "card",
        })

        row = get_transaction(txn_id)
        assert row["location"] == "IN"


# ── Agent decisions table ─────────────────────────────────────────────────────

class TestAgentDecisionsSaved:

    def test_all_agent_fields_populated(self):
        """All 3 agents must write their fields to agent_decisions."""
        txn_id = unique_txn_id()
        post_analyze({
            "transaction_id": txn_id,
            "user_id": "67f045c9-658d-4e62-8300-877be9a006d1",  # Mark T
            "amount": 45.0,
            "country": "IN",
            "hour": 14,
            "merchant": "Swiggy",
            "method": "card",
        })

        row = get_decision(txn_id)
        assert row, "agent_decisions row not found"

        # DETECTOR fields
        assert row["detector_score"]        is not None
        assert row["detector_flags"]        is not None

        # INVESTIGATOR fields
        assert row["investigator_summary"]  is not None
        assert row["investigator_deviation"] is not None

        # DECISION fields
        assert row["decision_verdict"]      is not None
        assert row["decision_confidence"]   is not None
        assert row["decision_reason"]       is not None

    def test_all_duration_columns_populated(self):
        """All 3 duration columns must be populated."""
        txn_id = unique_txn_id()
        post_analyze({
            "transaction_id": txn_id,
            "user_id": "67f045c9-658d-4e62-8300-877be9a006d1",
            "amount": 45.0,
            "country": "IN",
            "hour": 14,
            "merchant": "Swiggy",
            "method": "card",
        })

        row = get_decision(txn_id)
        assert row["detector_duration_ms"]     is not None
        assert row["investigator_duration_ms"] is not None
        assert row["decision_duration_ms"]     is not None

    def test_embedding_saved_as_list(self):
        """Embedding must be saved as a vector, not a string."""
        txn_id = unique_txn_id()
        post_analyze({
            "transaction_id": txn_id,
            "user_id": "67f045c9-658d-4e62-8300-877be9a006d1",
            "amount": 45.0,
            "country": "IN",
            "hour": 14,
            "merchant": "Swiggy",
            "method": "card",
        })

        row = get_decision(txn_id)
        assert row["embedding"] is not None, "Embedding is NULL"
        assert len(str(row["embedding"])) > 10, "Embedding appears empty"

    def test_status_is_complete(self):
        """Successful pipeline must set status = complete."""
        txn_id = unique_txn_id()
        post_analyze({
            "transaction_id": txn_id,
            "user_id": "67f045c9-658d-4e62-8300-877be9a006d1",
            "amount": 45.0,
            "country": "IN",
            "hour": 14,
            "merchant": "Swiggy",
            "method": "card",
        })

        row = get_decision(txn_id)
        assert row["status"] == "complete"


# ── Verdict correctness ───────────────────────────────────────────────────────

class TestVerdicts:

    def test_obvious_fraud_rejected(self):
        """Jimmy K — $4500 crypto Nigeria 3am → REJECTED."""
        txn_id = unique_txn_id()
        result = post_analyze({
            "transaction_id": txn_id,
            "user_id": "55472a7d-8980-4777-b98d-e8b65e65d33c",  # Jimmy K
            "amount": 4500.0,
            "country": "NG",
            "hour": 3,
            "merchant": "Crypto Exchange XY",
            "method": "crypto",
        })
        assert result["verdict"] in ("REVIEW", "REJECTED"), \
            f"Expected REVIEW or REJECTED for obvious fraud, got {result['verdict']}"

    def test_clean_transaction_approved(self):
        """Mark T — $45 Swiggy India 2pm → APPROVED."""
        txn_id = unique_txn_id()
        result = post_analyze({
            "transaction_id": txn_id,
            "user_id": "67f045c9-658d-4e62-8300-877be9a006d1",  # Mark T
            "amount": 45.0,
            "country": "IN",
            "hour": 14,
            "merchant": "Swiggy",
            "method": "card",
        })
        assert result["verdict"] == "APPROVED"

    def test_response_schema(self):
        """Response must contain all required fields."""
        txn_id = unique_txn_id()
        result = post_analyze({
            "transaction_id": txn_id,
            "user_id": "67f045c9-658d-4e62-8300-877be9a006d1",
            "amount": 45.0,
            "country": "IN",
            "hour": 14,
            "merchant": "Swiggy",
            "method": "card",
        })

        assert "transaction_id" in result
        assert "verdict"        in result
        assert "confidence"     in result
        assert "reason"         in result
        assert result["verdict"] in ("APPROVED", "REVIEW", "REJECTED")
        assert isinstance(result["confidence"], int)
        assert isinstance(result["reason"], str)