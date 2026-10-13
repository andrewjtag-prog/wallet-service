import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://wallet:wallet@localhost:5432/wallet",
)

from app.database import Base, get_session  # noqa: E402
from app.main import app  # noqa: E402

TEST_DATABASE_URL = os.environ["DATABASE_URL"]


@pytest_asyncio.fixture
async def engine():
    """Новый engine на каждый тест — свой event loop, свои соединения."""
    eng = create_async_engine(TEST_DATABASE_URL, poolclass=None)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


@pytest_asyncio.fixture
async def client(session_factory) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()