-- lightpaper.org database schema

CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Accounts (Firebase Auth backed)
CREATE TABLE accounts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    firebase_uid    TEXT UNIQUE NOT NULL,
    handle          TEXT UNIQUE,
    display_name    TEXT,
    email           TEXT,
    bio             TEXT,
    avatar_url      TEXT,
    tier            TEXT NOT NULL DEFAULT 'free',
    verified_domain TEXT,
    verified_linkedin BOOLEAN DEFAULT false,
    orcid_id        TEXT,
    gravity_level   INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

CREATE INDEX idx_accounts_firebase ON accounts(firebase_uid) WHERE deleted_at IS NULL;

-- API keys (scoped to accounts)
CREATE TABLE api_keys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    key_hash        TEXT NOT NULL UNIQUE,
    key_prefix      TEXT NOT NULL,
    tier            TEXT NOT NULL DEFAULT 'free',
    label           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    revoked_at      TIMESTAMPTZ
);

CREATE INDEX idx_api_keys_prefix ON api_keys(key_prefix) WHERE revoked_at IS NULL;
CREATE INDEX idx_api_keys_account ON api_keys(account_id);

-- Documents
CREATE TABLE documents (
    id              TEXT PRIMARY KEY,
    account_id      UUID REFERENCES accounts(id),
    slug            TEXT UNIQUE,
    title           TEXT NOT NULL,
    subtitle        TEXT,
    format          TEXT NOT NULL DEFAULT 'markdown',
    current_version INTEGER NOT NULL DEFAULT 1,
    authors         JSONB DEFAULT '[]',
    metadata        JSONB DEFAULT '{}',
    tags            JSONB DEFAULT '[]',
    listed          BOOLEAN DEFAULT true,
    quality_score   INTEGER,
    quality_detail  JSONB,
    author_gravity  INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ,
    search_vector   tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(subtitle, '')), 'B')
    ) STORED
);

CREATE INDEX idx_documents_search ON documents USING GIN(search_vector);
CREATE INDEX idx_documents_tags ON documents USING GIN(tags);
CREATE INDEX idx_documents_slug ON documents(slug) WHERE deleted_at IS NULL;
CREATE INDEX idx_documents_account ON documents(account_id);
CREATE INDEX idx_documents_quality ON documents(quality_score) WHERE deleted_at IS NULL AND listed = true;
CREATE INDEX idx_documents_created ON documents(created_at DESC) WHERE deleted_at IS NULL AND listed = true;
CREATE INDEX idx_documents_title_trgm ON documents USING GIN(title gin_trgm_ops);

-- Document versions
CREATE TABLE document_versions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id     TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL,
    content         TEXT NOT NULL,
    content_hash    TEXT NOT NULL,
    rendered_html   TEXT,
    word_count      INTEGER,
    reading_time    INTEGER,
    toc             JSONB,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(document_id, version)
);

CREATE INDEX idx_versions_document ON document_versions(document_id, version);

-- Citations (document A references document B)
CREATE TABLE citations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_doc_id   TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    target_doc_id   TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(source_doc_id, target_doc_id)
);

CREATE INDEX idx_citations_target ON citations(target_doc_id);

-- Anonymous publish tracking (rate limiting)
CREATE TABLE anonymous_publishes (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ip_address      TEXT NOT NULL,
    document_id     TEXT REFERENCES documents(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_anon_publishes_ip ON anonymous_publishes(ip_address, created_at);

-- Domain verification tokens
CREATE TABLE domain_verifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id      UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    domain          TEXT NOT NULL,
    txt_token       TEXT NOT NULL,
    verified        BOOLEAN DEFAULT false,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_domain_verifications_account ON domain_verifications(account_id);

-- LinkedIn verification tokens (OAuth state)
CREATE TABLE linkedin_verifications (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id          UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    state_token         TEXT UNIQUE NOT NULL,
    verified            BOOLEAN DEFAULT false,
    linkedin_profile_id TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_linkedin_verifications_state ON linkedin_verifications(state_token) WHERE verified = false;
CREATE INDEX idx_linkedin_verifications_account ON linkedin_verifications(account_id);

-- Agent-driven credential verification
CREATE TABLE credentials (
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
