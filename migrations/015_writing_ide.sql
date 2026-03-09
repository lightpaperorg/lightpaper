-- Writing IDE: sessions, files, and messages for the Wave Method
-- Supports the structured book-writing workflow (Waves 0-5+)

CREATE TABLE IF NOT EXISTS writing_sessions (
    id TEXT PRIMARY KEY,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    current_wave INTEGER NOT NULL DEFAULT 0,
    wave_state JSONB NOT NULL DEFAULT '{}'::jsonb,
    book_config JSONB NOT NULL DEFAULT '{}'::jsonb,
    published_book_id TEXT REFERENCES books(id) ON DELETE SET NULL,
    total_tokens_used INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_ws_account ON writing_sessions(account_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_ws_status ON writing_sessions(status) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS writing_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL REFERENCES writing_sessions(id) ON DELETE CASCADE,
    wave INTEGER NOT NULL,
    file_type TEXT NOT NULL,
    chapter_number INTEGER,
    title TEXT NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    word_count INTEGER NOT NULL DEFAULT 0,
    sort_order INTEGER NOT NULL DEFAULT 0,
    parent_file_id UUID REFERENCES writing_files(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wf_session ON writing_files(session_id, wave, sort_order);
CREATE INDEX IF NOT EXISTS idx_wf_chapter ON writing_files(session_id, chapter_number) WHERE chapter_number IS NOT NULL;

CREATE TABLE IF NOT EXISTS writing_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL REFERENCES writing_sessions(id) ON DELETE CASCADE,
    wave INTEGER NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    files_generated JSONB DEFAULT '[]'::jsonb,
    tokens_used INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wm_session ON writing_messages(session_id, wave, created_at);

-- Stripe customer ID on accounts
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT;
