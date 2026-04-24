"""
Unit + integration tests for the DETECTOR agent.
Covers: rules_engine, scorer, and DetectorAgent.analyze verdicts.

Run: conda run -n fraudsentinel pytest tests/test_detector.py -v
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.detector.rules_engine import check_rules
from agents.detector.scorer import calculate_score, get_verdict
from agents.detector.detector import DetectorAgent


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def clean_profile():
    return {
        "avg_spend": 100,
        "usual_location": "Kochi, India",
        "account_age_days": 365,
        "recent_transaction_count": 0,
    }


@pytest.fixture
def clean_transaction():
    return {
        "id": "txn-test",
        "amount": 90,
        "merchant": "Swiggy",
        "location": "Kochi, India",
        "timestamp": "2026-04-12 14:00:00",
    }


# ─── Rules Engine ─────────────────────────────────────────────────────────────

class TestAmountRule:
    def test_no_flag_below_3x(self, clean_transaction, clean_profile):
        clean_transaction["amount"] = 250  # 2.5x avg_spend=100
        flags = check_rules(clean_transaction, clean_profile)
        assert not any("above user average" in f for f in flags)

    def test_flags_above_3x(self, clean_transaction, clean_profile):
        clean_transaction["amount"] = 400  # 4x
        flags = check_rules(clean_transaction, clean_profile)
        assert any("above user average" in f for f in flags)

    def test_no_flag_when_avg_spend_zero(self, clean_transaction, clean_profile):
        clean_profile["avg_spend"] = 0
        clean_transaction["amount"] = 9999
        flags = check_rules(clean_transaction, clean_profile)
        assert not any("above user average" in f for f in flags)


class TestLocationRule:
    def test_flags_unfamiliar_location(self, clean_transaction, clean_profile):
        clean_transaction["location"] = "Lagos, Nigeria"
        flags = check_rules(clean_transaction, clean_profile)
        assert any("unfamiliar location" in f for f in flags)

    def test_no_flag_for_usual_location(self, clean_transaction, clean_profile):
        flags = check_rules(clean_transaction, clean_profile)
        assert not any("unfamiliar location" in f for f in flags)

    def test_no_flag_when_usual_location_empty(self, clean_transaction, clean_profile):
        clean_profile["usual_location"] = ""
        clean_transaction["location"] = "Lagos, Nigeria"
        flags = check_rules(clean_transaction, clean_profile)
        assert not any("unfamiliar location" in f for f in flags)


class TestTimeRule:
    def test_flags_early_morning(self, clean_transaction, clean_profile):
        clean_transaction["hour"] = 3
        flags = check_rules(clean_transaction, clean_profile)
        assert any("unusual hour" in f for f in flags)

    def test_no_flag_daytime(self, clean_transaction, clean_profile):
        clean_transaction["hour"] = 10
        flags = check_rules(clean_transaction, clean_profile)
        assert not any("unusual hour" in f for f in flags)

    def test_boundary_midnight_flagged(self, clean_transaction, clean_profile):
        clean_transaction["hour"] = 0
        flags = check_rules(clean_transaction, clean_profile)
        assert any("unusual hour" in f for f in flags)

    def test_boundary_5am_not_flagged(self, clean_transaction, clean_profile):
        clean_transaction["hour"] = 5
        flags = check_rules(clean_transaction, clean_profile)
        assert not any("unusual hour" in f for f in flags)


class TestHighRiskMerchantRule:
    @pytest.mark.parametrize("merchant", [
        "Crypto Exchange XY",
        "Online Casino Royal",
        "FX Gambling Hub",
        "Binance Forex",
        "Wire Transfer Service",
    ])
    def test_flags_risky_merchants(self, clean_transaction, clean_profile, merchant):
        clean_transaction["merchant"] = merchant
        flags = check_rules(clean_transaction, clean_profile)
        assert any("High-risk merchant" in f for f in flags)

    def test_no_flag_for_safe_merchant(self, clean_transaction, clean_profile):
        clean_transaction["merchant"] = "Amazon"
        flags = check_rules(clean_transaction, clean_profile)
        assert not any("High-risk merchant" in f for f in flags)

    def test_case_insensitive(self, clean_transaction, clean_profile):
        clean_transaction["merchant"] = "CRYPTO WALLET"
        flags = check_rules(clean_transaction, clean_profile)
        assert any("High-risk merchant" in f for f in flags)


class TestVelocityRule:
    def test_flags_at_3_or_more(self, clean_transaction, clean_profile):
        clean_profile["recent_transaction_count"] = 3
        flags = check_rules(clean_transaction, clean_profile)
        assert any("Velocity" in f for f in flags)

    def test_no_flag_below_3(self, clean_transaction, clean_profile):
        clean_profile["recent_transaction_count"] = 2
        flags = check_rules(clean_transaction, clean_profile)
        assert not any("Velocity" in f for f in flags)


class TestNewAccountRule:
    def test_flags_new_account(self, clean_transaction, clean_profile):
        clean_profile["account_age_days"] = 5
        flags = check_rules(clean_transaction, clean_profile)
        assert any("New account" in f for f in flags)

    def test_no_flag_established_account(self, clean_transaction, clean_profile):
        flags = check_rules(clean_transaction, clean_profile)
        assert not any("New account" in f for f in flags)

    def test_boundary_30_days_not_flagged(self, clean_transaction, clean_profile):
        clean_profile["account_age_days"] = 30
        flags = check_rules(clean_transaction, clean_profile)
        assert not any("New account" in f for f in flags)


class TestForeignTransactionRule:
    def test_flags_domestic_user_foreign_txn(self, clean_transaction, clean_profile):
        clean_transaction["location"] = "Lagos, Nigeria"
        flags = check_rules(clean_transaction, clean_profile)
        assert any("Foreign transaction" in f for f in flags)

    def test_no_flag_for_foreign_user(self, clean_transaction, clean_profile):
        clean_profile["usual_location"] = "Lagos, Nigeria"
        clean_transaction["location"] = "London, UK"
        flags = check_rules(clean_transaction, clean_profile)
        assert not any("Foreign transaction" in f for f in flags)


class TestHighAbsoluteAmountRule:
    def test_flags_above_3000(self, clean_transaction, clean_profile):
        clean_transaction["amount"] = 3001
        flags = check_rules(clean_transaction, clean_profile)
        assert any("High absolute amount" in f for f in flags)

    def test_no_flag_at_or_below_3000(self, clean_transaction, clean_profile):
        clean_transaction["amount"] = 3000
        flags = check_rules(clean_transaction, clean_profile)
        assert not any("High absolute amount" in f for f in flags)


class TestHighTransactionNewAccountRule:
    def test_flags_new_account_large_txn(self, clean_transaction, clean_profile):
        clean_profile["account_age_days"] = 1
        clean_transaction["amount"] = 1000
        flags = check_rules(clean_transaction, clean_profile)
        assert any("High transaction for new account" in f for f in flags)

    def test_no_flag_new_account_small_txn(self, clean_transaction, clean_profile):
        clean_profile["account_age_days"] = 1
        clean_transaction["amount"] = 499
        flags = check_rules(clean_transaction, clean_profile)
        assert not any("High transaction for new account" in f for f in flags)


# ─── Scorer ──────────────────────────────────────────────────────────────────

class TestCalculateScore:
    def test_empty_flags_is_zero(self):
        assert calculate_score([]) == 0

    def test_velocity_flag_alone_is_80(self):
        assert calculate_score(["Velocity anomaly: multiple transactions"]) == 80

    def test_amount_flag_alone_is_35(self):
        assert calculate_score(["Amount 5x above user average"]) == 35

    def test_score_capped_at_100(self):
        flags = [
            "Velocity anomaly: multiple transactions",   # 80
            "Amount 5x above user average",              # 35
            "Transaction in unfamiliar location: X",     # 25
        ]
        assert calculate_score(flags) == 100

    def test_new_account_plus_high_txn_is_40(self):
        flags = [
            "New account: 5 days old",                   # 10
            "High transaction for new account: 1000.0",  # 30
        ]
        assert calculate_score(flags) == 40


class TestGetVerdict:
    def test_rejected_at_70(self):
        assert get_verdict(70) == "REJECTED"

    def test_rejected_above_70(self):
        assert get_verdict(95) == "REJECTED"

    def test_review_at_31(self):
        assert get_verdict(31) == "REVIEW"

    def test_review_at_69(self):
        assert get_verdict(69) == "REVIEW"

    def test_approved_at_0(self):
        assert get_verdict(0) == "APPROVED"

    def test_approved_at_30(self):
        assert get_verdict(30) == "APPROVED"


# ─── DetectorAgent — Golden Dataset ──────────────────────────────────────────

class TestDetectorAgentGoldenDataset:
    """
    End-to-end verdict tests using seed transaction scenarios.
    LLM calls are NOT triggered here (scores outside 40-70 ambiguous zone,
    or profiles constructed to avoid it).
    """

    def setup_method(self):
        self.agent = DetectorAgent()

    def test_jimmy_k_obvious_fraud_rejected(self):
        txn = {
            "id": "txn-4821",
            "amount": 4500,
            "merchant": "Crypto Exchange XY",
            "location": "Lagos, Nigeria",
            "timestamp": "2026-04-06 03:14:00",
        }
        profile = {
            "avg_spend": 85,
            "usual_location": "Kochi, India",
            "account_age_days": 547,
            "recent_transactions": 0,
        }
        result = self.agent.analyze(txn, profile)
        assert result["verdict"] == "REJECTED"
        assert result["risk_score"] >= 70

    def test_mark_t_normal_approved(self):
        txn = {
            "id": "txn-4822",
            "amount": 45,
            "merchant": "Swiggy",
            "location": "Kochi, India",
            "timestamp": "2026-04-06 14:00:00",
        }
        profile = {
            "avg_spend": 45,
            "usual_location": "Kochi, India",
            "account_age_days": 820,
            "recent_transactions": 0,
        }
        result = self.agent.analyze(txn, profile)
        assert result["verdict"] == "APPROVED"
        assert result["risk_score"] <= 30

    def test_priya_s_velocity_fraud_rejected(self):
        txn = {
            "id": "txn-4824",
            "amount": 200,
            "merchant": "Lazada",
            "location": "Singapore",
            "timestamp": "2026-04-06 09:00:00",
        }
        profile = {
            "avg_spend": 200,
            "usual_location": "Singapore",
            "account_age_days": 320,
            "recent_transaction_count": 5,
        }
        result = self.agent.analyze(txn, profile)
        assert result["verdict"] == "REJECTED"
        assert any("Velocity" in f for f in result["flags"])

    def test_techcorp_high_but_normal_approved(self):
        txn = {
            "id": "txn-4828",
            "amount": 10000,
            "merchant": "AWS",
            "location": "Dubai, UAE",
            "timestamp": "2026-04-06 10:00:00",
        }
        profile = {
            "avg_spend": 9500,
            "usual_location": "Dubai, UAE",
            "account_age_days": 1825,
            "recent_transactions": 0,
        }
        result = self.agent.analyze(txn, profile)
        assert result["verdict"] == "APPROVED"

    def test_alex_r_new_user_review(self):
        txn = {
            "id": "txn-4827",
            "amount": 2000,
            "merchant": "Flipkart",
            "location": "Mumbai, India",
            "timestamp": "2026-04-06 13:00:00",
        }
        profile = {
            "avg_spend": 0,
            "usual_location": "Mumbai, India",
            "account_age_days": 1,
            "recent_transactions": 0,
        }
        result = self.agent.analyze(txn, profile)
        assert result["verdict"] == "REVIEW"
        assert any("New account" in f for f in result["flags"])

    def test_result_schema(self, clean_transaction, clean_profile):
        result = self.agent.analyze(clean_transaction, clean_profile)
        assert "transaction_id" in result
        assert "risk_score" in result
        assert "verdict" in result
        assert "flags" in result
        assert "reasoning" in result
        assert "llm_used" in result
        assert isinstance(result["flags"], list)
        assert 0 <= result["risk_score"] <= 100
        assert result["verdict"] in ("APPROVED", "REVIEW", "REJECTED")

    def test_no_llm_for_clear_approved(self):
        txn = {
            "id": "txn-safe",
            "amount": 50,
            "merchant": "Swiggy",
            "location": "Kochi, India",
            "timestamp": "2026-04-12 14:00:00",
        }
        profile = {
            "avg_spend": 60,
            "usual_location": "Kochi, India",
            "account_age_days": 500,
            "recent_transactions": 0,
        }
        result = self.agent.analyze(txn, profile)
        assert result["llm_used"] is False

    def test_no_llm_for_clear_rejected(self):
        txn = {
            "id": "txn-obvious-fraud",
            "amount": 5000,
            "merchant": "Crypto Casino",
            "location": "Lagos, Nigeria",
            "timestamp": "2026-04-12 02:00:00",
        }
        profile = {
            "avg_spend": 85,
            "usual_location": "Kochi, India",
            "account_age_days": 365,
            "recent_transactions": 5,
        }
        result = self.agent.analyze(txn, profile)
        assert result["llm_used"] is False
        assert result["verdict"] == "REJECTED"
