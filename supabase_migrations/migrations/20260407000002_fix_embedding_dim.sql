-- Drop old index first
DROP INDEX IF EXISTS agent_decisions_embedding_idx;

-- Change column from 384 to 1024 dims
ALTER TABLE agent_decisions
  DROP COLUMN IF EXISTS embedding;

ALTER TABLE agent_decisions
  ADD COLUMN embedding vector(1024);

-- Recreate index
CREATE INDEX IF NOT EXISTS agent_decisions_embedding_idx
  ON agent_decisions
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 10);
