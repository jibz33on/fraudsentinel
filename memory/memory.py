"""
Vector similarity search over agent_decisions.

Requires this SQL function in Supabase (run once):

    CREATE OR REPLACE FUNCTION match_agent_decisions(
        query_embedding vector(1024),
        match_count int DEFAULT 3
    )
    RETURNS TABLE (
        id uuid,
        transaction_id text,
        detector_score float,
        detector_flags text[],
        decision_verdict text,
        decision_reason text,
        similarity float
    )
    LANGUAGE sql STABLE AS $$
        SELECT
            id, transaction_id, detector_score, detector_flags,
            decision_verdict, decision_reason,
            1 - (embedding <=> query_embedding) AS similarity
        FROM agent_decisions
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> query_embedding
        LIMIT match_count;
    $$;
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Allow running from repo root without installing the package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.shared.embed import embed

_URL = os.environ["SUPABASE_URL"]
_KEY = os.environ["SUPABASE_SERVICE_KEY"]
_HEADERS = {
    "apikey": _KEY,
    "Authorization": f"Bearer {_KEY}",
    "Content-Type": "application/json",
}


def search_similar(text: str, limit: int = 3) -> list[dict]:
    vector = embed(text, input_type="query")
    payload = {"query_embedding": vector, "match_count": limit}
    response = requests.post(
        f"{_URL}/rest/v1/rpc/match_agent_decisions",
        headers=_HEADERS,
        json=payload,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    results = search_similar("high risk crypto transaction nigeria")
    print(f"Found {len(results)} results:")
    for r in results:
        print(r)
