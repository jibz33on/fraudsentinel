from db import client


def insert_decision(row: dict) -> dict:
    """Insert a new agent_decisions row. Returns inserted row."""
    return client.post("agent_decisions", {"status": "in_progress", **row})


def patch_status(transaction_id: str, status: str) -> None:
    """Update the pipeline status on an agent_decisions row."""
    client.patch(
        "agent_decisions",
        {"transaction_id": f"eq.{transaction_id}"},
        {"status": status},
    )


def patch_decision(transaction_id: str, data: dict) -> None:
    """Update fields on an existing agent_decisions row."""
    client.patch(
        "agent_decisions",
        {"transaction_id": f"eq.{transaction_id}"},
        data,
    )


def get_decision(transaction_id: str) -> dict | None:
    """Fetch a single agent_decisions row by transaction_id."""
    rows = client.get("agent_decisions", {
        "transaction_id": f"eq.{transaction_id}",
        "select": "*",
        "limit": 1,
    })
    return rows[0] if rows else None


def list_decisions(select: str = "*", limit: int = 50, filters: dict = None) -> list:
    """List recent agent_decisions rows ordered by created_at desc."""
    params = {
        "select": select,
        "order": "created_at.desc",
        "limit": limit,
    }
    if filters:
        params.update(filters)
    return client.get("agent_decisions", params)
