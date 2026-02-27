# Contributing to lightpaper.org

## Prerequisites

- Python 3.12+
- Docker and Docker Compose
- Git

## Local Development Setup

```bash
# Clone the repository
git clone https://github.com/lightpaperorg/lightpaper.git
cd lightpaper

# Start PostgreSQL
docker compose up -d db

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements-dev.txt

# Copy environment file
cp .env.example .env

# Initialize database
docker compose exec db psql -U lightpaper -d lightpaper -f /docker-entrypoint-initdb.d/init.sql

# Run the app
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Or run everything via Docker Compose
docker compose up
```

## Running Tests

```bash
# Start the database if not running
docker compose up -d db

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_quality.py -v
```

## Code Style

We use **ruff** for linting and formatting:

```bash
# Check for lint issues
ruff check app/ tests/

# Auto-fix lint issues
ruff check --fix app/ tests/

# Format code
ruff format app/ tests/

# Check formatting without changes
ruff format --check app/ tests/
```

## Branch Naming

- `fix/` — Bug fixes (e.g., `fix/xss-sanitization`)
- `feat/` — New features (e.g., `feat/author-export`)
- `chore/` — Maintenance tasks (e.g., `chore/update-deps`)

## Pull Request Process

1. Create a branch from `main` with the appropriate prefix
2. Make your changes with clear, focused commits
3. Ensure all tests pass (`python -m pytest tests/ -v`)
4. Ensure linting passes (`ruff check app/ tests/`)
5. Write a clear PR description explaining **what** and **why**
6. One reviewer approval is required before merging
7. CI checks must pass (lint, test, docker build)

## Security

If you discover a security vulnerability, do **not** open a public issue. See [SECURITY.md](SECURITY.md) for responsible disclosure instructions.
