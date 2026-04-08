import random
import time
import requests
from dotenv import load_dotenv

load_dotenv()

USERS = [
    {"id": "55472a7d-8980-4777-b98d-e8b65e65d33c", "name": "Jimmy K"},
    {"id": "67f045c9-658d-4e62-8300-877be9a006d1", "name": "Mark T"},
    {"id": "720b0db6-e4b4-4ca1-9989-5693728d871a", "name": "Sarah M"},
    {"id": "d5dbff76-59df-45d8-b92d-bfa4cd3a7748", "name": "Priya S"},
    {"id": "dce92994-825b-4264-8ece-67b4ca440cbe", "name": "Alex R"},
    {"id": "5f3bfd92-46d1-46b5-b82d-4bacbc42928d", "name": "TechCorp Ltd"},
]

MERCHANTS = [
    "Amazon", "Swiggy", "Flipkart", "AWS",
    "Crypto Exchange XY", "Lazada", "Apple Store",
    "Netflix", "Uber", "Steam",
]

LOCATIONS = [
    "Kochi, India", "Mumbai, India", "London, UK",
    "Singapore", "Lagos, Nigeria", "Dubai, UAE",
    "New York, US", "Tokyo, Japan",
]

METHODS = ["card", "upi", "crypto", "bank_transfer"]


def generate_transaction() -> dict:
    user = random.choice(USERS)
    txn_id = f"txn-{random.randint(100000, 999999)}"

    roll = random.random()
    if roll < 0.80:
        amount = round(random.uniform(10, 500), 2)
    elif roll < 0.95:
        amount = round(random.uniform(500, 5000), 2)
    else:
        amount = round(random.uniform(5000, 15000), 2)

    if random.random() < 0.8:
        hour = random.randint(8, 22)
    else:
        hour = random.randint(0, 7)

    return {
        "transaction_id": txn_id,
        "user_id":        user["id"],
        "amount":         amount,
        "country":        random.choice(LOCATIONS),
        "hour":           hour,
        "merchant":       random.choice(MERCHANTS),
        "method":         random.choice(METHODS),
        "_user_name":     user["name"],  # local only, not sent to API
    }


if __name__ == "__main__":
    print("FraudSentinel Simulator — Ctrl+C to stop\n")

    while True:
        txn = generate_transaction()
        user_name = txn.pop("_user_name")

        print(f"→ {txn['transaction_id']} | {user_name} | ${txn['amount']} | {txn['merchant']}")

        try:
            resp = requests.post(
                "http://localhost:8000/analyze",
                json=txn,
                timeout=60,
            )
            result = resp.json()
            verdict = result.get("verdict", "ERROR")
            confidence = result.get("confidence", "?")
            print(f"  {verdict} (confidence: {confidence}%)\n")
        except Exception as e:
            print(f"  ERROR: {e}\n")

        delay = random.uniform(5, 10)
        time.sleep(delay)
