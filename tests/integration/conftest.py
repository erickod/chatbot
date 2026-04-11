import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from chatbot.settings import settings


@pytest.fixture(scope="session", autouse=True)
def test_engine():
    return create_async_engine(settings.build_database_uri(), poolclass=NullPool)


@pytest_asyncio.fixture(scope="function")
async def db(override_async_session):
    yield override_async_session


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_db(db):
    yield


@pytest_asyncio.fixture()
async def override_async_session(test_engine):
    async with test_engine.connect() as conn:
        await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()
            await conn.rollback()
