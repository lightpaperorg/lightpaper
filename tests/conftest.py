"""Test fixtures: async HTTP client using httpx ASGITransport."""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import app.database as db_module
from app.config import settings
from app.main import app

# Replace the global engine with NullPool to avoid connection reuse issues
# across async test boundaries (prevents "another operation is in progress" errors)
_test_engine = create_async_engine(settings.database_url, echo=False, poolclass=NullPool)
_test_session = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)
db_module.engine = _test_engine
db_module.async_session = _test_session


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
