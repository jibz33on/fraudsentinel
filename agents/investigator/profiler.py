import os
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

_URL = os.environ["SUPABASE_URL"]
_KEY = os.environ["SUPABASE_SERVICE_KEY"]
_HEADERS = {
    "apikey": _KEY,
    "Authorization": f"Bearer {_KEY}",
}


def get_user_profile(user_id: str) -> dict:
    # 1. Read user row
    resp = requests.get(
        f"{_URL}/rest/v1/users",
        headers=_HEADERS,
        params={"id": f"eq.{user_id}", "select": "avg_spend,account_age_days,risk_profile"},
        timeout=10,
    )
    resp.raise_for_status()
    users = resp.json()
    user_row = users[0] if users else {}

    avg_spend = user_row.get("avg_spend", 0.0)
    account_age_days = user_row.get("account_age_days", 0)

    # 2. Read last 20 transactions
    resp = requests.get(
        f"{_URL}/rest/v1/transactions",
        headers=_HEADERS,
        params={
            "user_id": f"eq.{user_id}",
            "select": "amount,location,created_at,merchant",
            "order": "created_at.desc",
            "limit": 20,
        },
        timeout=10,
    )
    resp.raise_for_status()
    txns = resp.json()

    # 3. Build profile from transactions
    if not txns:
        return {
            "avg_amount": avg_spend,
            "avg_spend": avg_spend,
            "account_age_days": account_age_days,
            "known_countries": [],
            "known_merchants": [],
            "typical_hours": [],
            "transaction_count": 0,
        }

    amounts = [t["amount"] for t in txns if t.get("amount") is not None]
    avg_amount = sum(amounts) / len(amounts) if amounts else avg_spend

    known_countries = list({
        t["location"].split(",")[-1].strip()
        for t in txns
        if t.get("location")
    })

    known_merchants = list({t["merchant"] for t in txns if t.get("merchant")})

    typical_hours = list({
        datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")).hour
        for t in txns
        if t.get("created_at")
    })

    return {
        "avg_amount": avg_amount,
        "avg_spend": avg_spend,
        "account_age_days": account_age_days,
        "known_countries": known_countries,
        "known_merchants": known_merchants,
        "typical_hours": typical_hours,
        "transaction_count": len(txns),
    }


if __name__ == "__main__":
    profile = get_user_profile("55472a7d-8980-4777-b98d-e8b65e65d33c")
    for k, v in profile.items():
        print(f"  {k}: {v}")
