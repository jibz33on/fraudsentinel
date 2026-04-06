"""
Test DETECTOR agent against all 6 golden scenarios.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agents.detector import DetectorAgent

SCENARIOS = [
    {
        "name": "Jimmy K (obvious fraud)",
        "transaction": {
            "id": "txn-4821",
            "amount": 4500,
            "currency": "USD",
            "merchant": "Crypto Exchange XY",
            "location": "Lagos, Nigeria",
            "timestamp": "2026-04-06 03:14:00",
        },
        "user_profile": {
            "name": "Jimmy K",
            "avg_spend": 85,
            "usual_location": "Kochi, India",
            "usual_hours": "9am-10pm",
            "transaction_count": 284,
            "account_age_days": 547,
        },
        "expected_verdict": "REJECTED",
    },
    {
        "name": "Mark T (normal)",
        "transaction": {
            "id": "txn-4822",
            "amount": 45,
            "currency": "INR",
            "merchant": "Swiggy",
            "location": "Kochi, India",
            "timestamp": "2026-04-06 14:00:00",
        },
        "user_profile": {
            "name": "Mark T",
            "avg_spend": 45,
            "usual_location": "Kochi, India",
            "usual_hours": "8am-9pm",
            "transaction_count": 156,
            "account_age_days": 820,
        },
        "expected_verdict": "APPROVED",
    },
    {
        "name": "Sarah M (ambiguous)",
        "transaction": {
            "id": "txn-4823",
            "amount": 890,
            "currency": "GBP",
            "merchant": "Amazon UK",
            "location": "London, UK",
            "timestamp": "2026-04-06 23:00:00",
        },
        "user_profile": {
            "name": "Sarah M",
            "avg_spend": 200,
            "usual_location": "London, UK",
            "usual_hours": "10am-11pm",
            "transaction_count": 423,
            "account_age_days": 1200,
        },
        "expected_verdict": "REVIEW",
    },
    {
        "name": "Priya S (velocity fraud)",
        "transaction": {
            "id": "txn-4824",
            "amount": 200,
            "currency": "SGD",
            "merchant": "Lazada",
            "location": "Singapore",
            "timestamp": "2026-04-06 09:00:00",
        },
        "user_profile": {
            "name": "Priya S",
            "avg_spend": 200,
            "usual_location": "Singapore",
            "usual_hours": "9am-10pm",
            "transaction_count": 98,
            "account_age_days": 320,
            "recent_transactions": 5,
        },
        "expected_verdict": "REJECTED",
    },
    {
        "name": "Alex R (new user)",
        "transaction": {
            "id": "txn-4827",
            "amount": 2000,
            "currency": "INR",
            "merchant": "Flipkart",
            "location": "Mumbai, India",
            "timestamp": "2026-04-06 13:00:00",
        },
        "user_profile": {
            "name": "Alex R",
            "avg_spend": 0,
            "usual_location": "Mumbai, India",
            "usual_hours": "unknown",
            "transaction_count": 0,
            "account_age_days": 1,
        },
        "expected_verdict": "REVIEW",
    },
    {
        "name": "TechCorp Ltd (high but normal)",
        "transaction": {
            "id": "txn-4828",
            "amount": 10000,
            "currency": "USD",
            "merchant": "AWS",
            "location": "Dubai, UAE",
            "timestamp": "2026-04-06 10:00:00",
        },
        "user_profile": {
            "name": "TechCorp Ltd",
            "avg_spend": 9500,
            "usual_location": "Dubai, UAE",
            "usual_hours": "8am-6pm",
            "transaction_count": 1240,
            "account_age_days": 1825,
        },
        "expected_verdict": "APPROVED",
    },
]


def run_tests():
    agent = DetectorAgent()
    correct = 0

    print()
    for i, scenario in enumerate(SCENARIOS, 1):
        result = agent.analyze(scenario["transaction"], scenario["user_profile"])
        expected = scenario["expected_verdict"]
        passed = result["verdict"] == expected
        if passed:
            correct += 1

        status = "✅" if passed else "❌"
        llm_label = "Yes" if result["llm_used"] else "No"

        print("─" * 44)
        print(f"Scenario {i}: {scenario['name']}")
        print(f"  Score:    {result['risk_score']}/100")
        print(f"  Verdict:  {result['verdict']} {status} (expected {expected})")
        print(f"  Flags:    {len(result['flags'])} flags raised")
        for flag in result["flags"]:
            print(f"            · {flag}")
        print(f"  LLM used: {llm_label}")
        if result["reasoning"]:
            print(f"  Reasoning: {result['reasoning'][:120]}...")

    print("─" * 44)
    print(f"\nResults: {correct}/{len(SCENARIOS)} correct")
    print()


if __name__ == "__main__":
    run_tests()
