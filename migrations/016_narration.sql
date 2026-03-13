-- Migration 016: Audiobook narration tables
-- ElevenLabs Studio integration for book-to-audiobook conversion

CREATE TABLE IF NOT EXISTS narrations (
    id TEXT PRIMARY KEY,
    book_id TEXT NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id),
    elevenlabs_project_id TEXT,
    voice_id TEXT NOT NULL,
    voice_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    error_message TEXT,
    total_characters INTEGER NOT NULL,
    price_cents INTEGER NOT NULL,
    stripe_checkout_session_id TEXT,
    callback_token TEXT NOT NULL,
    gcs_bucket TEXT,
    audio_ready BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS narration_chapters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    narration_id TEXT NOT NULL REFERENCES narrations(id) ON DELETE CASCADE,
    document_id TEXT NOT NULL REFERENCES documents(id),
    chapter_number INTEGER NOT NULL,
    elevenlabs_chapter_id TEXT,
    elevenlabs_snapshot_id TEXT,
    audio_url TEXT,
    audio_duration_seconds INTEGER,
    character_count INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    UNIQUE(narration_id, chapter_number)
);

CREATE INDEX IF NOT EXISTS idx_narrations_book_id ON narrations(book_id);
CREATE INDEX IF NOT EXISTS idx_narrations_account_id ON narrations(account_id);
CREATE INDEX IF NOT EXISTS idx_narrations_callback_token ON narrations(callback_token);
CREATE INDEX IF NOT EXISTS idx_narration_chapters_narration_id ON narration_chapters(narration_id);
