from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.infra.db.postgres.connection import create_threaded_session


async def get_session() -> AsyncGenerator:
    session = create_threaded_session()
    try:
        yield session
    finally:
        await session.close()


def get_pristine_session() -> AsyncSession:
    return create_threaded_session()


async def close_session(session: AsyncSession) -> None:
    await session.close()
