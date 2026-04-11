import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.investigator.profiler import get_user_profile


def investigate(transaction: dict, profile: dict) -> dict:
    # TODO: LLM-enhanced summary (add after pipeline is complete)
    # Current: rule-based summary string
    #   "Amount 53x normal, new country, unusual hour"
    # Future: pass deviation signals to LLM for natural language summary
    #   "This transaction is highly unusual for Jimmy.
    #    He typically spends $85 in Kochi during business hours.
    #    This $4500 crypto purchase from Nigeria at 3am
    #    matches no prior behavior."
    # Only fire LLM if deviation_score > 50 (same pattern as DETECTOR)

    signals = {}
    notes = []

    # 1. Amount deviation
    avg_spend = profile.get("avg_spend") or profile.get("avg_amount") or 0
    amount = transaction.get("amount", 0)
    if avg_spend > 0:
        ratio = amount / avg_spend
        if ratio > 10:
            signals["amount"] = 25
            notes.append(f"Amount {ratio:.0f}x normal")
        elif ratio > 5:
            signals["amount"] = 20
            notes.append(f"Amount {ratio:.0f}x normal")
        elif ratio > 3:
            signals["amount"] = 15
            notes.append(f"Amount {ratio:.0f}x normal")
        elif ratio > 2:
            signals["amount"] = 10
            notes.append(f"Amount {ratio:.0f}x normal")
        else:
            signals["amount"] = 0
    else:
        signals["amount"] = 0

    # 2. Country deviation
    known_countries = profile.get("known_countries", [])
    country = transaction.get("country", "")
    if not known_countries:
        signals["country"] = 0
    elif country not in known_countries:
        signals["country"] = 25
        notes.append("new country")
    else:
        signals["country"] = 0

    # 3. Hour deviation
    typical_hours = profile.get("typical_hours", [])
    hour = transaction.get("hour", 0)
    if not typical_hours:
        signals["hour"] = 0
    else:
        avg_hour = sum(typical_hours) / len(typical_hours)
        diff = abs(hour - avg_hour)
        # wrap around midnight
        diff = min(diff, 24 - diff)
        if diff > 8:
            signals["hour"] = 20
            notes.append("unusual hour")
        elif diff > 4:
            signals["hour"] = 10
            notes.append("unusual hour")
        else:
            signals["hour"] = 0

    # 4. Merchant deviation
    known_merchants = profile.get("known_merchants", [])
    merchant = transaction.get("merchant", "")
    if not known_merchants:
        signals["merchant"] = 0
    elif merchant not in known_merchants:
        signals["merchant"] = 15
        notes.append("new merchant")
    else:
        signals["merchant"] = 0

    deviation_score = sum(signals.values())

    if deviation_score > 50:
        from tools.llm_router import call_llm
        avg_spend = profile.get("avg_spend") or profile.get("avg_amount") or 0
        usual_location = ", ".join(profile.get("known_countries", [])) or "unknown"
        usual_hours = profile.get("typical_hours", [])
        hour = transaction.get("hour", 0)
        amount = transaction.get("amount", 0)
        location = transaction.get("country", "")
        prompt = (
            f"User normally spends ${avg_spend:.0f} in {usual_location} "
            f"during hours {usual_hours}. Today spent ${amount:.0f} in "
            f"{location} at hour {hour}. Deviation signals: {', '.join(notes)}. "
            f"How suspicious is this? One sentence explanation."
        )
        try:
            summary = call_llm(prompt)
        except Exception:
            summary = ", ".join(notes) if notes else "no significant deviations"
    else:
        summary = ", ".join(notes) if notes else "no significant deviations"

    return {
        "deviation_score": deviation_score,
        "summary": summary,
        "signals": signals,
    }


if __name__ == "__main__":
    user_id = "55472a7d-8980-4777-b98d-e8b65e65d33c"
    profile = get_user_profile(user_id)

    transaction = {
        "user_id": user_id,
        "amount": 4500.0,
        "country": "NG",
        "hour": 3,
        "merchant": "Crypto Exchange XY",
        "method": "crypto",
    }

    result = investigate(transaction, profile)
    print(f"deviation_score: {result['deviation_score']}")
    print(f"summary:         {result['summary']}")
    print(f"signals:         {result['signals']}")
