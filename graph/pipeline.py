import os
import sys

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from langgraph.graph import StateGraph

from graph.state import FraudState
from agents.detector.detector import DetectorAgent
from agents.shared.embed import embed
from agents.investigator.profiler import get_user_profile
from agents.investigator.investigator import investigate

_SUPABASE_URL = os.environ["SUPABASE_URL"]
_SUPABASE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
_HEADERS = {
    "apikey": _SUPABASE_KEY,
    "Authorization": f"Bearer {_SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

_detector = DetectorAgent()


def detector_node(state: FraudState) -> FraudState:
    transaction = {
        "id": state["transaction_id"],
        "user_id": state["user_id"],
        "amount": state["amount"],
        "country": state["country"],
        "hour": state["hour"],
        "merchant": state["merchant"],
        "method": state["method"],
    }
    user_profile = {}

    result = _detector.analyze(transaction, user_profile)

    score = result["risk_score"]
    verdict = result["verdict"]
    flags = result["flags"]

    embed_text = (
        f"verdict:{verdict} score:{score} flags:{flags} "
        f"country:{state['country']} amount:{state['amount']} hour:{state['hour']}"
    )
    embedding = embed(embed_text, input_type="passage")

    row = {
        "transaction_id": state["transaction_id"],
        "detector_score": score,
        "detector_flags": flags,
        "embedding": str(embedding),
    }

    try:
        resp = requests.post(
            f"{_SUPABASE_URL}/rest/v1/agent_decisions",
            headers=_HEADERS,
            json=row,
            timeout=10,
        )
        resp.raise_for_status()
    except Exception as e:
        print(f"[pipeline] Supabase write failed: {e}")
        print(f"[pipeline] Response body: {resp.text}")

    return {
        **state,
        "detector_score": score,
        "detector_flags": flags,
        "detector_verdict": verdict,
    }


def investigator_node(state: FraudState) -> dict:
    profile = get_user_profile(state["user_id"])
    transaction = {
        "user_id": state["user_id"],
        "amount": state["amount"],
        "country": state["country"],
        "hour": state["hour"],
        "merchant": state["merchant"],
        "method": state["method"],
    }
    result = investigate(transaction, profile)

    patch = {
        "investigator_summary": result["summary"],
        "investigator_deviation": result["deviation_score"],
    }

    try:
        resp = requests.patch(
            f"{_SUPABASE_URL}/rest/v1/agent_decisions",
            headers=_HEADERS,
            params={"transaction_id": f"eq.{state['transaction_id']}"},
            json=patch,
            timeout=10,
        )
        resp.raise_for_status()
    except Exception as e:
        print(f"[pipeline] Investigator Supabase patch failed: {e}")
        print(f"[pipeline] Response body: {resp.text}")

    return {
        **state,
        "investigator_summary": result["summary"],
        "investigator_deviation": result["deviation_score"],
    }


def _build_graph():
    graph = StateGraph(FraudState)
    graph.add_node("detector", detector_node)
    graph.add_node("investigator", investigator_node)
    graph.set_entry_point("detector")
    graph.add_edge("detector", "investigator")
    graph.set_finish_point("investigator")
    return graph.compile()


_graph = _build_graph()


def run_pipeline(transaction: dict) -> FraudState:
    initial_state: FraudState = {
        "transaction_id": transaction.get("transaction_id", transaction.get("id", "unknown")),
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
    return _graph.invoke(initial_state)


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
