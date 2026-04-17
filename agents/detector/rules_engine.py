"""
Layer 1: Rules Engine
Pure if/else logic. No LLM. No AI.
Input: transaction dict + user_profile dict
Output: list of flag strings
"""

HIGH_RISK_KEYWORDS = ["crypto", "casino", "gambling", "forex", "wire transfer"]

DOMESTIC_INDICATORS = ["india", "kochi", "mumbai", "delhi", "bangalore", "chennai"]
INDIA_ISO_CODES = {"in", "ind"}


def check_rules(transaction: dict, user_profile: dict) -> list[str]:
    flags = []
    amount = float(transaction.get("amount", 0))
    avg_spend = float(user_profile.get("avg_spend", 0))
    location = transaction.get("country", transaction.get("location", ""))
    merchant = transaction.get("merchant", "")
    account_age_days = int(user_profile.get("account_age_days", 0))
    usual_location = user_profile.get("usual_location", "")
    recent_transactions = int(user_profile.get("recent_transaction_count", 0))
    ip_address = transaction.get("ip_address", "")
    device = transaction.get("device", "")
    currency = transaction.get("currency", "USD")

    # 1. AMOUNT ANOMALY — more than 3x user avg_spend
    if avg_spend > 0 and amount > 3 * avg_spend:
        multiple = round(amount / avg_spend, 1)
        flags.append(f"Amount {multiple}x above user average")

    # 2. LOCATION ANOMALY — transaction not in user's usual location
    # Skip if no established location (new accounts have usual_location = "Unknown")
    if usual_location and location and usual_location.lower() not in ("unknown", ""):
        if usual_location.lower() not in location.lower() and location.lower() not in usual_location.lower():
            flags.append(f"Transaction in unfamiliar location: {location}")

    # 3. TIME ANOMALY — between midnight and 5am
    hour_val = transaction.get("hour", -1)
    try:
        hour_val = int(hour_val)
    except (TypeError, ValueError):
        hour_val = -1
    if 0 <= hour_val < 5:
        flags.append(f"Transaction at unusual hour: {hour_val:02d}:00")

    # 4. HIGH RISK MERCHANT
    merchant_lower = merchant.lower()
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in merchant_lower:
            flags.append(f"High-risk merchant category: {merchant}")
            break

    # 5. VELOCITY CHECK — 3+ transactions in the last 24 hours
    if recent_transactions >= 3:
        flags.append(f"Velocity anomaly: {recent_transactions} transactions in 24h")

    # 6. NEW ACCOUNT
    if account_age_days < 30:
        flags.append(f"New account: {account_age_days} days old")

    # 7. FOREIGN TRANSACTION — domestic user transacting abroad
    usual_lower = usual_location.lower()
    location_lower = location.lower()
    is_domestic_user = any(city in usual_lower for city in DOMESTIC_INDICATORS)
    is_india_location = (
        any(city in location_lower for city in DOMESTIC_INDICATORS)
        or location_lower.strip() in INDIA_ISO_CODES
    )
    is_foreign_txn = not is_india_location
    if is_domestic_user and is_foreign_txn:
        flags.append("Foreign transaction for domestic user")

    # 8. HIGH AMOUNT ABSOLUTE
    if amount > 3000:
        flags.append(f"High absolute amount: {amount}")

    # 9. HIGH TRANSACTION FOR NEW ACCOUNT
    if account_age_days < 30 and amount > 500:
        flags.append(f"High transaction for new account: {amount}")

    # 10. IP / LOCATION MISMATCH — IP country doesn't match transaction country
    ip_country = transaction.get("ip_country", "")
    country = transaction.get("country", location)
    if ip_country and country and ip_country.lower() != country.lower():
        flags.append(f"IP/location mismatch: IP country {ip_country} vs transaction country {country}")

    # 11. NEW DEVICE
    known_devices = user_profile.get("known_devices", [])
    if device and known_devices and device not in known_devices:
        flags.append(f"New device: {device}")

    # 12. CURRENCY MISMATCH — non-USD currency for domestic user
    if currency and currency.upper() != "USD":
        is_domestic_user = any(city in usual_location.lower() for city in DOMESTIC_INDICATORS)
        if is_domestic_user and currency.upper() not in ("INR", "USD"):
            flags.append(f"Currency mismatch: {currency} for domestic user")
        elif not is_domestic_user and currency.upper() not in ("USD", "EUR", "GBP", "INR", "AUD", "CAD"):
            flags.append(f"Unusual currency: {currency}")

    return flags
