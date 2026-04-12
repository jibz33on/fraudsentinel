"""
Unit + integration tests for the INVESTIGATOR agent.
Covers: amount/country/hour/merchant deviation signals, scoring, LLM trigger.

Run: conda run -n fraudsentinel pytest tests/test_investigator.py -v
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.investigator.investigator import investigate


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def normal_profile():
    """A well-established user with clear history."""
    return {
        "avg_spend":        100.0,
        "avg_amount":       100.0,
        "account_age_days": 365,
        "known_countries":  ["India"],
        "known_merchants":  ["Swiggy", "Amazon"],
        "typical_hours":    [9, 10, 11, 14],
    }


@pytest.fixture
def normal_transaction():
    """A clean, low-risk transaction."""
    return {
        "id":       "txn-test",
        "amount":   90.0,
        "country":  "India",
        "hour":     10,
        "merchant": "Swiggy",
    }


# ─── Amount Deviation ─────────────────────────────────────────────────────────

class TestAmountDeviation:

    def test_above_10x_scores_25(self, normal_transaction, normal_profile):
        normal_transaction["amount"] = 1100   # 11x avg_spend=100
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["amount"] == 25

    def test_above_5x_scores_20(self, normal_transaction, normal_profile):
        normal_transaction["amount"] = 600    # 6x
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["amount"] == 20

    def test_above_3x_scores_15(self, normal_transaction, normal_profile):
        normal_transaction["amount"] = 350    # 3.5x
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["amount"] == 15

    def test_above_2x_scores_10(self, normal_transaction, normal_profile):
        normal_transaction["amount"] = 210    # 2.1x
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["amount"] == 10

    def test_below_2x_scores_0(self, normal_transaction, normal_profile):
        normal_transaction["amount"] = 150    # 1.5x
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["amount"] == 0

    def test_no_avg_spend_scores_0(self, normal_transaction, normal_profile):
        normal_profile["avg_spend"] = 0
        normal_profile["avg_amount"] = 0
        normal_transaction["amount"] = 9999
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["amount"] == 0


# ─── Country Deviation ────────────────────────────────────────────────────────

class TestCountryDeviation:

    def test_new_country_scores_25(self, normal_transaction, normal_profile):
        normal_transaction["country"] = "Nigeria"
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["country"] == 25

    def test_known_country_scores_0(self, normal_transaction, normal_profile):
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["country"] == 0

    def test_no_known_countries_scores_0(self, normal_transaction, normal_profile):
        normal_profile["known_countries"] = []
        normal_transaction["country"] = "Nigeria"
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["country"] == 0


# ─── Hour Deviation ───────────────────────────────────────────────────────────

class TestHourDeviation:

    def test_large_hour_diff_scores_20(self, normal_transaction, normal_profile):
        # avg typical hour ≈ 11, diff of 3am = 8 hours away
        normal_transaction["hour"] = 2
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["hour"] == 20

    def test_medium_hour_diff_scores_10(self, normal_transaction, normal_profile):
        # avg typical hour ≈ 11, diff of 6am = ~5 hours away
        normal_transaction["hour"] = 6
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["hour"] == 10

    def test_normal_hour_scores_0(self, normal_transaction, normal_profile):
        # same as typical hours
        normal_transaction["hour"] = 10
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["hour"] == 0

    def test_no_typical_hours_scores_0(self, normal_transaction, normal_profile):
        normal_profile["typical_hours"] = []
        normal_transaction["hour"] = 3
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["hour"] == 0


# ─── Merchant Deviation ───────────────────────────────────────────────────────

class TestMerchantDeviation:

    def test_new_merchant_scores_15(self, normal_transaction, normal_profile):
        normal_transaction["merchant"] = "Crypto Exchange XY"
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["merchant"] == 15

    def test_known_merchant_scores_0(self, normal_transaction, normal_profile):
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["merchant"] == 0

    def test_no_known_merchants_scores_0(self, normal_transaction, normal_profile):
        normal_profile["known_merchants"] = []
        normal_transaction["merchant"] = "Crypto Exchange XY"
        result = investigate(normal_transaction, normal_profile)
        assert result["signals"]["merchant"] == 0


# ─── Deviation Score ──────────────────────────────────────────────────────────

class TestDeviationScore:

    def test_clean_transaction_scores_0(self, normal_transaction, normal_profile):
        result = investigate(normal_transaction, normal_profile)
        assert result["deviation_score"] == 0

    def test_all_signals_stack(self, normal_transaction, normal_profile):
        # amount 11x=25 + new country=25 + 3am=20 + new merchant=15 = 85
        normal_transaction["amount"]   = 1100
        normal_transaction["country"]  = "Nigeria"
        normal_transaction["hour"]     = 2
        normal_transaction["merchant"] = "Crypto Exchange XY"
        result = investigate(normal_transaction, normal_profile)
        assert result["deviation_score"] == 85

    def test_result_schema(self, normal_transaction, normal_profile):
        result = investigate(normal_transaction, normal_profile)
        assert "deviation_score" in result
        assert "summary"         in result
        assert "signals"         in result
        assert isinstance(result["signals"], dict)
        assert isinstance(result["summary"], str)
        assert isinstance(result["deviation_score"], int)


# ─── LLM Trigger ─────────────────────────────────────────────────────────────

class TestLLMTrigger:

    def test_no_llm_below_50(self, normal_transaction, normal_profile):
        """Clean transaction — deviation 0, summary is rule-based."""
        result = investigate(normal_transaction, normal_profile)
        assert result["deviation_score"] <= 50
        # summary should be plain text, not LLM narrative
        assert result["summary"] == "no significant deviations"

    def test_summary_populated_above_50(self, normal_transaction, normal_profile):
        """High deviation — LLM fires, summary should be a non-empty string."""
        normal_transaction["amount"]   = 1100   # 11x → 25
        normal_transaction["country"]  = "Nigeria"  # new → 25
        normal_transaction["hour"]     = 3          # 3am → 20
        result = investigate(normal_transaction, normal_profile)
        assert result["deviation_score"] > 50
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 10   # not empty


# ─── Golden Dataset ───────────────────────────────────────────────────────────

class TestInvestigatorGoldenDataset:

    def test_jimmy_k_obvious_fraud(self):
        """$4500 crypto in Nigeria at 3am vs normal $85 in India at 10am."""
        txn = {
            "amount":   4500,
            "country":  "Nigeria",
            "hour":     3,
            "merchant": "Crypto Exchange XY",
        }
        profile = {
            "avg_spend":       85,
            "avg_amount":      85,
            "known_countries": ["India"],
            "known_merchants": ["Swiggy", "Amazon"],
            "typical_hours":   [9, 10, 11],
        }
        result = investigate(txn, profile)
        assert result["deviation_score"] >= 70
        assert "Amount" in result["summary"] or len(result["summary"]) > 10

    def test_mark_t_normal_transaction(self):
        """Normal spend, known location, normal hour → deviation near 0."""
        txn = {
            "amount":   45,
            "country":  "India",
            "hour":     14,
            "merchant": "Swiggy",
        }
        profile = {
            "avg_spend":       50,
            "avg_amount":      50,
            "known_countries": ["India"],
            "known_merchants": ["Swiggy"],
            "typical_hours":   [12, 13, 14],
        }
        result = investigate(txn, profile)
        assert result["deviation_score"] == 0
        assert result["summary"] == "no significant deviations"

    def test_priya_s_new_country(self):
        """Normal amount and hour but in a brand new country."""
        txn = {
            "amount":   200,
            "country":  "UK",
            "hour":     10,
            "merchant": "Lazada",
        }
        profile = {
            "avg_spend":       200,
            "avg_amount":      200,
            "known_countries": ["Singapore"],
            "known_merchants": ["Lazada"],
            "typical_hours":   [9, 10, 11],
        }
        result = investigate(txn, profile)
        assert result["signals"]["country"] == 25
        assert result["deviation_score"] == 25