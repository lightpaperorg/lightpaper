-- Migration 003: Rename document formats
-- markdown -> post, academic -> paper, report -> paper, tutorial -> post
-- Idempotent: UPDATE with WHERE clause is safe to run multiple times.

UPDATE documents SET format = 'post' WHERE format = 'markdown';
UPDATE documents SET format = 'paper' WHERE format = 'academic';
UPDATE documents SET format = 'paper' WHERE format = 'report';
UPDATE documents SET format = 'post' WHERE format = 'tutorial';
