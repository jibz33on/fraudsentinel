import os
import sys

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

from langgraph.graph import StateGraph

from graph.state import FraudState
from agents.detector.detector import DetectorAgent
from tools.embed import embed
from agents.investigator.profiler import get_user_profile
from agents.investigator.investigator import investigate
from agents.decision.decision import decide
from db.decisions import insert_decision, patch_decision, patch_status

_detector = DetectorAgent()


def detector_node(state: FraudState) -> FraudState:
    try:
        transaction = {
            "id": state["transaction_id"],
            "user_id": state["user_id"],
            "amount": state["amount"],
            "country": state["country"],
            "hour": state["hour"],
            "merchant": state["merchant"],
            "method": state["method"],
        }
        start = time.time()
        result = _detector.analyze(transaction, {})
        detector_duration_ms = int((time.time() - start) * 1000)

        score = result["risk_score"]
        verdict = result["verdict"]
        flags = result["flags"]

        embed_text = (
            f"verdict:{verdict} score:{score} flags:{flags} "
            f"country:{state['country']} amount:{state['amount']} hour:{state['hour']}"
        )
        embedding = embed(embed_text, input_type="passage")

        try:
            insert_decision({
                "transaction_id": state["transaction_id"],
                "detector_score": score,
                "detector_flags": flags,
                "embedding": str(embedding),
                "detector_duration_ms": detector_duration_ms,
            })
        except Exception as e:
            print(f"[pipeline] detector insert failed: {e}")

        return {
            **state,
            "detector_score": score,
            "detector_flags": flags,
            "detector_verdict": verdict,
        }
    except Exception as e:
        print(f"[pipeline] detector agent failed: {e}")
        return {
            **state,
            "detector_score": 0,
            "detector_flags": [],
            "detector_verdict": "REVIEW",
        }


def investigator_node(state: FraudState) -> dict:
    try:
        profile = get_user_profile(state["user_id"])
        transaction = {
            "user_id": state["user_id"],
            "amount": state["amount"],
            "country": state["country"],
            "hour": state["hour"],
            "merchant": state["merchant"],
            "method": state["method"],
        }
        start = time.time()
        result = investigate(transaction, profile)
        investigator_duration_ms = int((time.time() - start) * 1000)

        try:
            patch_decision(state["transaction_id"], {
                "investigator_summary": result["summary"],
                "investigator_deviation": result["deviation_score"],
                "investigator_duration_ms": investigator_duration_ms,
            })
        except Exception as e:
            print(f"[pipeline] investigator patch failed: {e}")

        return {
            **state,
            "investigator_summary": result["summary"],
            "investigator_deviation": result["deviation_score"],
        }
    except Exception as e:
        print(f"[pipeline] investigator agent failed: {e}")
        return {
            **state,
            "investigator_summary": "unavailable",
            "investigator_deviation": 0,
        }


def decision_node(state: FraudState) -> dict:
    try:
        detector = {
            "detector_score": state["detector_score"],
            "detector_flags": state["detector_flags"],
            "detector_verdict": state["detector_verdict"],
        }
        investigator = {
            "investigator_deviation": state["investigator_deviation"],
            "investigator_summary": state["investigator_summary"],
        }
        start = time.time()
        result = decide(detector, investigator)
        decision_duration_ms = int((time.time() - start) * 1000)

        try:
            patch_decision(state["transaction_id"], {
                "decision_verdict": result["verdict"],
                "decision_confidence": result["confidence"],
                "decision_reason": result["reason"],
                "decision_duration_ms": decision_duration_ms,
            })
        except Exception as e:
            print(f"[pipeline] decision patch failed: {e}")

        return {
            **state,
            "decision_verdict": result["verdict"],
            "decision_confidence": result["confidence"],
            "decision_reason": result["reason"],
        }
    except Exception as e:
        print(f"[pipeline] decision agent failed: {e}")
        return {
            **state,
            "decision_verdict": "REVIEW",
            "decision_confidence": 0,
            "decision_reason": "unavailable",
        }


def _build_graph():
    graph = StateGraph(FraudState)
    graph.add_node("detector", detector_node)
    graph.add_node("investigator", investigator_node)
    graph.add_node("decision", decision_node)
    graph.set_entry_point("detector")
    graph.add_edge("detector", "investigator")
    graph.add_edge("investigator", "decision")
    graph.set_finish_point("decision")
    return graph.compile()


_graph = _build_graph()


def run_pipeline(transaction: dict) -> FraudState:
    transaction_id = transaction.get("transaction_id", transaction.get("id", "unknown"))
    initial_state: FraudState = {
        "transaction_id": transaction_id,
        "user_id": transaction.get("user_id", ""),
        "amount": transaction.get("amount", 0.0),
        "country": transaction.get("country", ""),
        "hour": transaction.get("hour", 0),
        "merchant": transaction.get("merchant", ""),
        "method": transaction.get("method", ""),
        "detector_score": 0,
        "detector_flags": [],
        "detector_verdict": "",
        "investigator_summary": "",
        "investigator_deviation": 0,
        "decision_verdict": "",
        "decision_confidence": 0,
        "decision_reason": "",
    }
    try:
        result = _graph.invoke(initial_state)
        patch_status(transaction_id, "complete")
        return result
    except Exception as e:
        print(f"[pipeline] pipeline failed for {transaction_id}: {e}")
        try:
            patch_status(transaction_id, "failed")
        except Exception:
            pass
        raise


if __name__ == "__main__":
    test_txn = {
        "transaction_id": "txn-4821",
        "user_id": "55472a7d-8980-4777-b98d-e8b65e65d33c",
        "amount": 4500.0,
        "country": "NG",
        "hour": 3,
        "merchant": "Crypto Exchange XY",
        "method": "crypto",
    }

    final_state = run_pipeline(test_txn)
    print("\n=== Final State ===")
    for k, v in final_state.items():
        print(f"  {k}: {v}")
