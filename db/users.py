from db import client


def get_user(user_id: str, select: str = "*") -> dict | None:
    """Fetch a single user row by id."""
    rows = client.get("users", {
        "id": f"eq.{user_id}",
        "select": select,
        "limit": 1,
    })
    return rows[0] if rows else None


def list_users(select: str = "*") -> list[dict]:
    """Fetch all users."""
    return client.get("users", {"select": select}) or []


def get_user_basics(user_id: str) -> dict | None:
    """Fetch only the fields needed for behavioral profiling."""
    return get_user(user_id, select="avg_spend,account_age_days,risk_profile,usual_location")


def increment_transaction_count(user_id: str) -> None:
    """Increment the user's transaction_count by 1."""
    row = get_user(user_id, select="transaction_count")
    if row is None:
        return
    current = row.get("transaction_count") or 0
    client.patch("users", {"id": f"eq.{user_id}"}, {"transaction_count": current + 1})
