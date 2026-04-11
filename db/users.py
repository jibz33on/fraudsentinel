from db import client


def get_user(user_id: str, select: str = "*") -> dict | None:
    """Fetch a single user row by id."""
    rows = client.get("users", {
        "id": f"eq.{user_id}",
        "select": select,
        "limit": 1,
    })
    return rows[0] if rows else None


def get_user_basics(user_id: str) -> dict | None:
    """Fetch only the fields needed for behavioral profiling."""
    return get_user(user_id, select="avg_spend,account_age_days,risk_profile")
