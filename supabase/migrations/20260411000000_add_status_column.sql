-- Add status column to agent_decisions to track pipeline completion state
ALTER TABLE agent_decisions
    ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'in_progress';
