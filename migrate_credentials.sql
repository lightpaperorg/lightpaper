-- Migration: Add credentials table for agent-driven credential verification
-- Run via Cloud Run job (same pattern as linkedin_verifications migration)

CREATE TABLE IF NOT EXISTS credentials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    credential_type TEXT NOT NULL,  -- 'degree', 'certification', 'employment'
    institution     TEXT NOT NULL,
    title           TEXT NOT NULL,  -- e.g. 'Bachelor of Science in Computer Science'
    year            INTEGER,
    evidence_tier   TEXT NOT NULL DEFAULT 'claimed',  -- 'confirmed', 'supported', 'claimed'
    evidence_data   JSONB DEFAULT '{}',  -- API responses, URLs, verification details
    agent_notes     TEXT,  -- free-text notes from the verifying agent
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_credential_type CHECK (credential_type IN ('degree', 'certification', 'employment')),
    CONSTRAINT valid_evidence_tier CHECK (evidence_tier IN ('confirmed', 'supported', 'claimed'))
);

CREATE INDEX idx_credentials_account ON credentials(account_id);
CREATE UNIQUE INDEX idx_credentials_unique ON credentials(account_id, credential_type, institution, title);
