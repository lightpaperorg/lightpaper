-- Add license column to documents and books
ALTER TABLE documents ADD COLUMN IF NOT EXISTS license TEXT NOT NULL DEFAULT 'all-rights-reserved';
ALTER TABLE books ADD COLUMN IF NOT EXISTS license TEXT NOT NULL DEFAULT 'all-rights-reserved';
