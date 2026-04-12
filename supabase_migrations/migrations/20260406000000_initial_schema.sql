-- FraudSentinel Schema
-- Run via: python supabase/run_schema.py

-- ── Table: users ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT        NOT NULL,
    email               TEXT        UNIQUE,
    avg_spend           DECIMAL     DEFAULT 0,
    usual_location      TEXT,
    usual_hours         TEXT,               -- e.g. "9am-10pm"
    transaction_count   INTEGER     DEFAULT 0,
    account_age_days    INTEGER     DEFAULT 0,
    risk_profile        TEXT        DEFAULT 'low',  -- low / medium / high
    created_at          TIMESTAMP   DEFAULT NOW()
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_bypass" ON users
    FOR ALL USING (true) WITH CHECK (true);


-- ── Table: transactions ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
    id          TEXT        PRIMARY KEY,    -- e.g. txn-4821
    user_id     UUID        REFERENCES users(id),
    amount      DECIMAL     NOT NULL,
    currency    TEXT        DEFAULT 'USD',
    merchant    TEXT,
    location    TEXT,
    ip_address  TEXT,
    device      TEXT,
    status      TEXT        DEFAULT 'PENDING',  -- PENDING / APPROVED / REVIEW / REJECTED
    created_at  TIMESTAMP   DEFAULT NOW()
);

ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_bypass" ON transactions
    FOR ALL USING (true) WITH CHECK (true);


-- ── Table: agent_decisions ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agent_decisions (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id          TEXT        REFERENCES transactions(id),
    detector_score          INTEGER,        -- 0-100
    detector_flags          TEXT[],         -- array of flag strings
    investigator_summary    TEXT,
    investigator_deviation  INTEGER,        -- 0-100
    decision_verdict        TEXT,           -- APPROVED / REVIEW / REJECTED
    decision_confidence     INTEGER,        -- 0-100
    decision_reason         TEXT,
    created_at              TIMESTAMP   DEFAULT NOW()
);

ALTER TABLE agent_decisions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_bypass" ON agent_decisions
    FOR ALL USING (true) WITH CHECK (true);
