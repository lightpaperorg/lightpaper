-- Assets: hosted images (charts, photos, diagrams) for documents and books.
-- Content-addressed by SHA-256, served on-domain at /i/{sha256}.{ext}.

CREATE TABLE IF NOT EXISTS assets (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id   UUID REFERENCES accounts(id) ON DELETE SET NULL,
    sha256       TEXT NOT NULL UNIQUE,
    ext          TEXT NOT NULL,
    content_type TEXT NOT NULL,
    bytes        INTEGER NOT NULL,
    width        INTEGER,
    height       INTEGER,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_assets_account ON assets(account_id);
