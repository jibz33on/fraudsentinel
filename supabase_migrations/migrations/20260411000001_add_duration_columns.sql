-- Add per-agent duration tracking to agent_decisions
ALTER TABLE agent_decisions
    ADD COLUMN IF NOT EXISTS detector_duration_ms INTEGER,
    ADD COLUMN IF NOT EXISTS investigator_duration_ms INTEGER,
    ADD COLUMN IF NOT EXISTS decision_duration_ms INTEGER;
