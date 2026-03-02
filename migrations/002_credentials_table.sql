-- Create credentials table (was in init.sql but missing from production)

CREATE TABLE IF NOT EXISTS credentials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    credential_type TEXT NOT NULL,
    institution     TEXT NOT NULL,
    title           TEXT NOT NULL,
    year            INTEGER,
    evidence_tier   TEXT NOT NULL DEFAULT 'claimed',
    evidence_data   JSONB DEFAULT '{}',
    agent_notes     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_credential_type CHECK (credential_type IN ('degree', 'certification', 'employment')),
    CONSTRAINT valid_evidence_tier CHECK (evidence_tier IN ('confirmed', 'supported', 'claimed'))
);

CREATE INDEX IF NOT EXISTS idx_credentials_account ON credentials(account_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_credentials_unique ON credentials(account_id, credential_type, institution, title);
