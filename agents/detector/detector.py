"""
DETECTOR Agent — Layer 3
Combines rules engine + scorer, calls LLM only for ambiguous cases (score 40-70).
"""

from .rules_engine import check_rules
from .scorer import calculate_score, get_verdict

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from tools.logger import get_logger

logger = get_logger("DETECTOR")

LLM_AMBIGUOUS_LOW = 40
LLM_AMBIGUOUS_HIGH = 70

LLM_PROMPT = """\
You are a fraud analyst.
Transaction: {transaction}
User profile: {user_profile}
Flags raised: {flags}
Risk score: {score}

In 2 sentences explain why this transaction needs human review. Be specific."""


class DetectorAgent:

    def analyze(self, transaction: dict, user_profile: dict) -> dict:
        txn_id = transaction.get("id", "unknown")

        #Layer 0 — pgvector memory search 
        try:
            from memory.memory import search_similar
            query = f"{transaction.get('merchant', '')} {transaction.get('location', '')}"
            similar = search_similar(query, limit=3)
            past_frauds = [r for r in similar if r.get("decision_verdict") == "REJECTED"]
            if len(past_frauds) >= 2:
                flags.append("similar_past_fraud: matched past rejected transaction")
        except Exception as e:
            logger.warning(f"Memory Search failed for {txn_id}: {e}")
        # Layer 1: rules
        flags = check_rules(transaction, user_profile)

        # Layer 2: scoring
        score = calculate_score(flags)
        verdict = get_verdict(score)

        # Layer 3: LLM only for ambiguous zone
        reasoning = None
        llm_used = False

        if LLM_AMBIGUOUS_LOW <= score <= LLM_AMBIGUOUS_HIGH:
            try:
                from tools.llm_router import call_llm
                prompt = LLM_PROMPT.format(
                    transaction=transaction,
                    user_profile=user_profile,
                    flags=flags,
                    score=score,
                )
                reasoning = call_llm(prompt)
                llm_used = True
            except Exception as e:
                logger.warning(f"LLM call failed for {txn_id}: {e}")

        logger.info(
            f"[DETECTOR] txn-{txn_id} | score: {score} | verdict: {verdict} | flags: {len(flags)}"
        )

        return {
            "transaction_id": txn_id,
            "risk_score": score,
            "verdict": verdict,
            "flags": flags,
            "reasoning": reasoning,
            "llm_used": llm_used,
        }
