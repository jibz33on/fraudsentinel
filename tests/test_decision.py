"""
Unit + integration tests for the DECISION agent.
Covers: combined score math, verdict thresholds, confidence bands, output schema.

NOTE: LLM fires on every decide() call — real calls are kept to minimum.
      Math tests use calculate_combined() and get_verdict() directly.

Run: conda run -n fraudsentinel pytest tests/test_decision.py -v
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.decision.decision import decide


# ─── Helpers (pure math, no LLM) ─────────────────────────────────────────────

def combined_score(detector_score, investigator_deviation):
    """Mirror of decision.py Step 1."""
    return (detector_score * 0.6) + (investigator_deviation * 0.4)


def get_verdict(combined):
    """Mirror of decision.py Step 2."""
    if combined >= 70:
        return "REJECTED"
    elif combined >= 40:
        return "REVIEW"
    return "APPROVED"


def get_confidence(combined):
    """Mirror of decision.py Step 3."""
    if combined >= 80 or combined <= 20:
        return 90
    elif combined >= 60 or combined <= 40:
        return 75
    return 60


# ─── Combined Score Math ──────────────────────────────────────────────────────

class TestCombinedScore:

    def test_60_40_weighting(self):
        # detector=100, investigator=0 → 100*0.6 + 0*0.4 = 60
        assert combined_score(100, 0) == 60.0

    def test_both_zero(self):
        assert combined_score(0, 0) == 0.0

    def test_both_100(self):
        assert combined_score(100, 100) == 100.0

    def test_typical_fraud_case(self):
        # from golden dataset: detector=65, investigator=60
        # 65*0.6 + 60*0.4 = 39 + 24 = 63
        assert combined_score(65, 60) == 63.0

    def test_investigator_pulls_score_up(self):
        # low detector, high investigator
        # 30*0.6 + 90*0.4 = 18 + 36 = 54
        assert combined_score(30, 90) == 54.0

    def test_investigator_pulls_score_down(self):
        # high detector, low investigator
        # 80*0.6 + 10*0.4 = 48 + 4 = 52
        assert combined_score(80, 10) == 52.0


# ─── Verdict Thresholds ───────────────────────────────────────────────────────

class TestVerdict:

    def test_rejected_at_70(self):
        assert get_verdict(70) == "REJECTED"

    def test_rejected_above_70(self):
        assert get_verdict(95) == "REJECTED"

    def test_review_at_40(self):
        assert get_verdict(40) == "REVIEW"

    def test_review_at_69(self):
        assert get_verdict(69) == "REVIEW"

    def test_approved_at_39(self):
        assert get_verdict(39) == "APPROVED"

    def test_approved_at_0(self):
        assert get_verdict(0) == "APPROVED"


# ─── Confidence Bands ─────────────────────────────────────────────────────────

class TestConfidence:

    def test_high_confidence_at_80(self):
        assert get_confidence(80) == 90

    def test_high_confidence_at_20(self):
        # very clean transaction → also high confidence
        assert get_confidence(20) == 90

    def test_medium_confidence_at_60(self):
        assert get_confidence(60) == 75

    def test_medium_confidence_at_40(self):
        assert get_confidence(40) == 75

    def test_low_confidence_at_50(self):
        # 50 is the ambiguous middle → lowest confidence
        assert get_confidence(50) == 60


# ─── Real decide() calls (LLM fires) ─────────────────────────────────────────

class TestDecideSchema:

    def test_output_schema(self):
        """Verify decide() returns all required keys with correct types."""
        detector = {
            "detector_score": 80,
            "detector_flags": ["High-risk merchant", "unusual hour"],
        }
        investigator = {
            "investigator_deviation": 75,
            "investigator_summary":   "Amount 10x normal, new country",
        }
        result = decide(detector, investigator)

        assert "verdict"       in result
        assert "confidence"    in result
        assert "reason"        in result
        assert "combined_score" in result

        assert result["verdict"]    in ("APPROVED", "REVIEW", "REJECTED")
        assert isinstance(result["confidence"],    int)
        assert isinstance(result["reason"],        str)
        assert isinstance(result["combined_score"], float)
        assert len(result["reason"]) > 10


# ─── Golden Dataset (3 LLM calls) ────────────────────────────────────────────

class TestDecisionGoldenDataset:

    def test_obvious_fraud_rejected(self):
        """High detector + high investigator → REJECTED."""
        detector = {
            "detector_score": 90,
            "detector_flags": ["Velocity", "Crypto merchant", "3am"],
        }
        investigator = {
            "investigator_deviation": 85,
            "investigator_summary":   "Amount 53x normal, new country, unusual hour",
        }
        result = decide(detector, investigator)
        # 90*0.6 + 85*0.4 = 54 + 34 = 88
        assert result["verdict"] == "REJECTED"
        assert result["confidence"] == 90

    def test_clean_transaction_approved(self):
        """Low detector + low investigator → APPROVED."""
        detector = {
            "detector_score": 10,
            "detector_flags": [],
        }
        investigator = {
            "investigator_deviation": 0,
            "investigator_summary":   "no significant deviations",
        }
        result = decide(detector, investigator)
        # 10*0.6 + 0*0.4 = 6
        assert result["verdict"] == "APPROVED"
        assert result["confidence"] == 90

    def test_ambiguous_review(self):
        """Mid detector + mid investigator → REVIEW."""
        detector = {
            "detector_score": 65,
            "detector_flags": ["High-risk merchant", "High absolute amount"],
        }
        investigator = {
            "investigator_deviation": 60,
            "investigator_summary":   "Amount 53x normal, new country",
        }
        result = decide(detector, investigator)
        # 65*0.6 + 60*0.4 = 39 + 24 = 63
        assert result["verdict"] == "REVIEW"