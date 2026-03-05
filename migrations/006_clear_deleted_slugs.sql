-- Free up slugs from soft-deleted documents so they can be reused
UPDATE documents SET slug = NULL WHERE deleted_at IS NOT NULL AND slug IS NOT NULL;
