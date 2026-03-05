-- Track Google Search Console indexing status per document
ALTER TABLE documents ADD COLUMN IF NOT EXISTS google_indexed BOOLEAN;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS google_index_checked_at TIMESTAMPTZ;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS google_coverage_state TEXT;
