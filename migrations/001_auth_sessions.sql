-- Email + LinkedIn auth migration (idempotent)

-- Make firebase_uid nullable (new accounts won't have one)
ALTER TABLE accounts ALTER COLUMN firebase_uid DROP NOT NULL;
DROP INDEX IF EXISTS idx_accounts_firebase;
CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_firebase ON accounts(firebase_uid)
    WHERE firebase_uid IS NOT NULL AND deleted_at IS NULL;

-- Unique email index (for login lookup)
CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_email ON accounts(LOWER(email))
    WHERE deleted_at IS NULL;

-- LinkedIn profile ID on accounts (for LinkedIn login matching)
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS linkedin_profile_id TEXT;
CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_linkedin_profile ON accounts(linkedin_profile_id)
    WHERE linkedin_profile_id IS NOT NULL AND deleted_at IS NULL;

-- Backfill linkedin_profile_id from existing verifications
UPDATE accounts a
SET linkedin_profile_id = lv.linkedin_profile_id
FROM linkedin_verifications lv
WHERE lv.account_id = a.id AND lv.verified = true
  AND lv.linkedin_profile_id IS NOT NULL AND a.linkedin_profile_id IS NULL;

-- Email auth sessions
CREATE TABLE IF NOT EXISTS email_auth_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      TEXT UNIQUE NOT NULL,
    email           TEXT NOT NULL,
    code_hash       TEXT NOT NULL,
    display_name    TEXT,
    handle          TEXT,
    attempts        INTEGER NOT NULL DEFAULT 0,
    max_attempts    INTEGER NOT NULL DEFAULT 5,
    expires_at      TIMESTAMPTZ NOT NULL,
    verified_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_email_auth_session ON email_auth_sessions(session_id) WHERE verified_at IS NULL;

-- LinkedIn auth sessions (for login, separate from verification)
CREATE TABLE IF NOT EXISTS linkedin_auth_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      TEXT UNIQUE NOT NULL,
    state_token     TEXT UNIQUE NOT NULL,
    account_id      UUID REFERENCES accounts(id) ON DELETE CASCADE,
    api_key_plain   TEXT,
    completed_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_linkedin_auth_state ON linkedin_auth_sessions(state_token) WHERE completed_at IS NULL;

-- Drop anonymous_publishes table (no longer needed)
DROP TABLE IF EXISTS anonymous_publishes;
