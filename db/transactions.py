from db import client


def get_transaction(txn_id: str) -> dict | None:
    """Fetch a single transaction row by id."""
    rows = client.get("transactions", {
        "id": f"eq.{txn_id}",
        "select": "amount,merchant,location,currency,user_id",
        "limit": 1,
    })
    return rows[0] if rows else None


def list_transactions(user_id: str, limit: int = 20) -> list:
    """Fetch recent transactions for a user, ordered by created_at desc."""
    return client.get("transactions", {
        "user_id": f"eq.{user_id}",
        "select": "amount,location,created_at,merchant,device",
        "order": "created_at.desc",
        "limit": limit,
    })
