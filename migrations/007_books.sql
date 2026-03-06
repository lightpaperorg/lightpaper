-- Book publishing tables
-- Migration 007: books + book_chapters + document.book_id

CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    account_id UUID NOT NULL REFERENCES accounts(id),
    slug TEXT UNIQUE,
    title TEXT NOT NULL,
    subtitle TEXT,
    description TEXT,
    format TEXT NOT NULL DEFAULT 'post',
    authors JSONB DEFAULT '[]'::jsonb,
    tags JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    cover_image_url TEXT,
    listed BOOLEAN DEFAULT TRUE,
    quality_score INTEGER,
    quality_detail JSONB,
    author_gravity INTEGER NOT NULL DEFAULT 0,
    chapter_count INTEGER NOT NULL DEFAULT 0,
    total_word_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    search_vector TSVECTOR GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(subtitle, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(description, '')), 'C')
    ) STORED
);

CREATE INDEX IF NOT EXISTS idx_books_account_id ON books(account_id);

CREATE INDEX IF NOT EXISTS idx_books_slug ON books(slug) WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_books_search_vector ON books USING gin(search_vector);

CREATE INDEX IF NOT EXISTS idx_books_listed ON books(listed, quality_score) WHERE deleted_at IS NULL;

CREATE TABLE IF NOT EXISTS book_chapters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id TEXT NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chapter_number INTEGER NOT NULL,
    chapter_title TEXT,
    UNIQUE(book_id, document_id),
    UNIQUE(book_id, chapter_number)
);

CREATE INDEX IF NOT EXISTS idx_book_chapters_book_id ON book_chapters(book_id, chapter_number);

ALTER TABLE documents ADD COLUMN IF NOT EXISTS book_id TEXT REFERENCES books(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_documents_book_id ON documents(book_id) WHERE book_id IS NOT NULL;
