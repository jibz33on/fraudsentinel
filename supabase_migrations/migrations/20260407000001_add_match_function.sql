CREATE OR REPLACE FUNCTION match_agent_decisions(
    query_embedding vector(1024),
    match_count int DEFAULT 3
)
RETURNS TABLE (
    id uuid,
    transaction_id text,
    detector_score int,
    detector_flags text[],
    decision_verdict text,
    decision_reason text,
    similarity float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        id,
        transaction_id,
        detector_score,
        detector_flags,
        decision_verdict,
        decision_reason,
        1 - (embedding <=> query_embedding) AS similarity
    FROM agent_decisions
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> query_embedding
    LIMIT match_count;
$$;
