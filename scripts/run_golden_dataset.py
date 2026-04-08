import sys
import os
import time

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.pipeline import run_pipeline

TRANSACTIONS = [
    {"transaction_id": "txn-4821", "user_id": "55472a7d-8980-4777-b98d-e8b65e65d33c", "amount": 4500, "country": "NG", "hour": 3,  "merchant": "Crypto Exchange XY", "method": "crypto"},
    {"transaction_id": "txn-4822", "user_id": "67f045c9-658d-4e62-8300-877be9a006d1", "amount": 45,   "country": "IN", "hour": 14, "merchant": "Swiggy",            "method": "card"},
    {"transaction_id": "txn-4823", "user_id": "720b0db6-e4b4-4ca1-9989-5693728d871a", "amount": 890,  "country": "GB", "hour": 22, "merchant": "Amazon UK",          "method": "card"},
    {"transaction_id": "txn-4824", "user_id": "d5dbff76-59df-45d8-b92d-bfa4cd3a7748", "amount": 200,  "country": "SG", "hour": 10, "merchant": "Lazada",             "method": "card"},
    {"transaction_id": "txn-4825", "user_id": "d5dbff76-59df-45d8-b92d-bfa4cd3a7748", "amount": 200,  "country": "SG", "hour": 10, "merchant": "Lazada",             "method": "card"},
    {"transaction_id": "txn-4826", "user_id": "d5dbff76-59df-45d8-b92d-bfa4cd3a7748", "amount": 200,  "country": "SG", "hour": 10, "merchant": "Lazada",             "method": "card"},
    {"transaction_id": "txn-4827", "user_id": "dce92994-825b-4264-8ece-67b4ca440cbe", "amount": 2000, "country": "IN", "hour": 23, "merchant": "Flipkart",           "method": "card"},
    {"transaction_id": "txn-4828", "user_id": "5f3bfd92-46d1-46b5-b82d-4bacbc42928d", "amount": 10000,"country": "AE", "hour": 11, "merchant": "AWS",               "method": "wire"},
]

if __name__ == "__main__":
    print(f"Running {len(TRANSACTIONS)} transactions through pipeline...\n")

    for i, txn in enumerate(TRANSACTIONS):
        print(f"[{i+1}/8] {txn['transaction_id']} ...", flush=True)
        result = run_pipeline(txn)
        reason_preview = result.get("decision_reason", "")[:80]
        print(
            f"  verdict:    {result.get('decision_verdict')}\n"
            f"  confidence: {result.get('decision_confidence')}\n"
            f"  reason:     {reason_preview}\n"
        )
        if i < len(TRANSACTIONS) - 1:
            time.sleep(2)

    print("Done.")
