import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.investigator.profiler import get_user_profile


def investigate(transaction: dict, profile: dict) -> dict:
    # LLM summary fires when deviation_score > 50 (same pattern as DETECTOR)
    # Low deviation → rule-based summary string

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

    if deviation_score > 30:
        from tools.llm_router import call_llm
        avg_spend = profile.get("avg_spend") or profile.get("avg_amount") or 0
        usual_location = ", ".join(profile.get("known_countries", [])) or "unknown"
        usual_hours = profile.get("typical_hours", [])
        hour = transaction.get("hour", 0)
        amount = transaction.get("amount", 0)
        location = transaction.get("country", "")
        prompt = f"""You are a fraud analyst reviewing behavioural deviation signals for a transaction.

User's normal behaviour:
- Average spend: ${avg_spend:.0f}
- Usual countries: {usual_location}
- Typical transaction hours: {usual_hours}

This transaction:
- Amount: ${amount:.0f}
- Country: {location}
- Hour: {hour}:00

Deviation signals detected: {', '.join(notes)}
Deviation score: {deviation_score}/100

Respond in exactly this format, no markdown, no bullet symbols:

PATTERN: [one sentence describing the user's normal behaviour]
DEVIATION: [one sentence on exactly how this transaction differs from that pattern]
RISK: [one sentence on why this deviation is or isn't suspicious]"""
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
