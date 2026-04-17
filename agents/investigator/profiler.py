from datetime import datetime, timezone, timedelta
from db.users import get_user_basics
from db.transactions import list_transactions


def get_user_profile(user_id: str) -> dict:
    user_row = get_user_basics(user_id) or {}

    avg_spend = user_row.get("avg_spend", 0.0)
    account_age_days = user_row.get("account_age_days", 0)
    usual_location = user_row.get("usual_location", "")

    txns = list_transactions(user_id, limit=30)

    if not txns:
        return {
            "avg_amount": avg_spend,
            "avg_spend": avg_spend,
            "account_age_days": account_age_days,
            "usual_location": usual_location,
            "known_countries": [],
            "known_merchants": [],
            "known_devices": [],
            "typical_hours": [],
            "transaction_count": 0,
            "recent_transaction_count": 0,
        }

    amounts = [t["amount"] for t in txns if t.get("amount") is not None]
    avg_amount = sum(amounts) / len(amounts) if amounts else avg_spend

    known_countries = list({
        t["location"].split(",")[-1].strip()
        for t in txns
        if t.get("location")
    })

    known_merchants = list({t["merchant"] for t in txns if t.get("merchant")})

    known_devices = list({t["device"] for t in txns if t.get("device")})

    def _parse_utc(ts: str) -> datetime:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    typical_hours = list({
        _parse_utc(t["created_at"]).hour
        for t in txns
        if t.get("created_at")
    })

    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    recent_transaction_count = sum(
        1 for t in txns
        if t.get("created_at") and _parse_utc(t["created_at"]) > cutoff
    )

    return {
        "avg_amount": avg_amount,
        "avg_spend": avg_spend,
        "account_age_days": account_age_days,
        "usual_location": usual_location,
        "known_countries": known_countries,
        "known_merchants": known_merchants,
        "known_devices": known_devices,
        "typical_hours": typical_hours,
        "transaction_count": len(txns),
        "recent_transaction_count": recent_transaction_count,
    }


if __name__ == "__main__":
    profile = get_user_profile("55472a7d-8980-4777-b98d-e8b65e65d33c")
    for k, v in profile.items():
        print(f"  {k}: {v}")
