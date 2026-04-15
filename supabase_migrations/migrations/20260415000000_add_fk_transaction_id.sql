-- Clean orphaned agent_decisions rows
DELETE FROM agent_decisions
WHERE transaction_id NOT IN (
    SELECT id FROM transactions
);

-- Add FK from agent_decisions.transaction_id → transactions.id
ALTER TABLE agent_decisions
DROP CONSTRAINT IF EXISTS agent_decisions_transaction_id_fkey;

ALTER TABLE agent_decisions
ADD CONSTRAINT agent_decisions_transaction_id_fkey
FOREIGN KEY (transaction_id) REFERENCES transactions(id);

-- Reload PostgREST schema cache
NOTIFY pgrst, 'reload schema';
