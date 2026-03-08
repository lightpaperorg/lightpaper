-- Make book slug uniqueness only apply to non-deleted books
ALTER TABLE books DROP CONSTRAINT IF EXISTS books_slug_key;
DROP INDEX IF EXISTS books_slug_key;
CREATE UNIQUE INDEX IF NOT EXISTS books_slug_active_key ON books (slug) WHERE deleted_at IS NULL;
