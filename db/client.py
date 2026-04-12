"""
db/client.py
Single Supabase client for the entire project.
All db/ files use this — nowhere else touches Supabase directly.
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_URL = os.environ["SUPABASE_URL"]
_KEY = os.environ["SUPABASE_SERVICE_KEY"]

# Single shared client instance
supabase: Client = create_client(_URL, _KEY)


def get(table: str, params: dict = None) -> list:
    """
    Read rows from a table.
    params keys map to PostgREST filters:
      - select, order, limit  → query modifiers
      - id=eq.xxx             → row filters
    """
    params = params or {}

    query = supabase.table(table).select(params.pop("select", "*"))

    # Apply filters (e.g. id=eq.xxx, user_id=eq.yyy)
    for key, value in params.items():
        if key in ("order", "limit"):
            continue
        # value format: "eq.xxx" → split into operator and value
        if "." in str(value):
            operator, val = str(value).split(".", 1)
            if operator == "eq":
                query = query.eq(key, val)
        else:
            query = query.eq(key, value)

    # Apply order
    if "order" in params:
        col, *direction = params["order"].split(".")
        query = query.order(col, desc=("desc" in direction))

    # Apply limit
    if "limit" in params:
        query = query.limit(int(params["limit"]))

    result = query.execute()
    return result.data or []


def post(table: str, data: dict) -> dict:
    """Insert a row. Returns the inserted row."""
    result = supabase.table(table).insert(data).execute()
    rows = result.data
    return rows[0] if rows else {}


def patch(table: str, params: dict, data: dict) -> None:
    """Update rows matching params with data."""
    query = supabase.table(table).update(data)

    for key, value in params.items():
        if "." in str(value):
            operator, val = str(value).split(".", 1)
            if operator == "eq":
                query = query.eq(key, val)
        else:
            query = query.eq(key, value)

    query.execute()