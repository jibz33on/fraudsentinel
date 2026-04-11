import os
import requests
from dotenv import load_dotenv

load_dotenv()

_URL = os.environ["SUPABASE_URL"]
_KEY = os.environ["SUPABASE_SERVICE_KEY"]

_READ_HEADERS = {
    "apikey": _KEY,
    "Authorization": f"Bearer {_KEY}",
}

_WRITE_HEADERS = {
    **_READ_HEADERS,
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def get(table: str, params: dict = None) -> list:
    resp = requests.get(
        f"{_URL}/rest/v1/{table}",
        headers=_READ_HEADERS,
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def post(table: str, data: dict) -> dict:
    resp = requests.post(
        f"{_URL}/rest/v1/{table}",
        headers=_WRITE_HEADERS,
        json=data,
        timeout=30,
    )
    resp.raise_for_status()
    result = resp.json()
    return result[0] if isinstance(result, list) else result


def patch(table: str, params: dict, data: dict) -> None:
    resp = requests.patch(
        f"{_URL}/rest/v1/{table}",
        headers=_WRITE_HEADERS,
        params=params,
        json=data,
        timeout=30,
    )
    resp.raise_for_status()
