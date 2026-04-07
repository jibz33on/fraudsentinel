-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column to agent_decisions
-- 1024 dims = nvidia/nv-embedqa-e5-v5
ALTER TABLE agent_decisions
  ADD COLUMN IF NOT EXISTS embedding vector(1024);

-- Index for fast similarity search
CREATE INDEX IF NOT EXISTS agent_decisions_embedding_idx
  ON agent_decisions
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 10);
