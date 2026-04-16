from datetime import datetime
from db.users import get_user_basics
from db.transactions import list_transactions


def get_user_profile(user_id: str) -> dict:
    user_row = get_user_basics(user_id) or {}

    avg_spend = user_row.get("avg_spend", 0.0)
    account_age_days = user_row.get("account_age_days", 0)

    txns = list_transactions(user_id, limit=30)

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
        "avg_spend": avg_amount,
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
