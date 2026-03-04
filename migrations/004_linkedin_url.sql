-- Add linkedin_url column for clickable LinkedIn badge links
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS linkedin_url TEXT;
