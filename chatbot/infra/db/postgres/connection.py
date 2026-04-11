from contextvars import ContextVar
from typing import Callable

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from chatbot.settings import settings

_engine_var: ContextVar[AsyncEngine] = ContextVar("_engine_var")
_session_factory_var: ContextVar[Callable] = ContextVar("_session_factory_var")
_is_single_threaded: bool = False
_engine: AsyncEngine
_session_factory: Callable


def create_thread_safe_context(is_single_threaded: bool = False) -> None:
    engine = create_async_engine(
        settings.build_database_uri(), **settings.retrieve_engine_config()
    )
    async_session_factory = async_sessionmaker(
        bind=engine, **settings.build_session_config()
    )  # type: ignore  # noqa
    if is_single_threaded:
        global _is_single_threaded, _engine, _session_factory
        _is_single_threaded = is_single_threaded
        _engine = engine
        _session_factory = async_session_factory
    else:
        _engine_var.set(engine)
        _session_factory_var.set(async_session_factory)


def get_threaded_engine() -> AsyncEngine:
    global _is_single_threaded  # noqa: F824
    if _is_single_threaded:
        return _engine
    return _engine_var.get()  # pragma: no cover


def create_threaded_session() -> AsyncSession:
    global _is_single_threaded, _session_factory  # noqa: F824
    if _is_single_threaded:
        return _session_factory()  # type: ignore[no-any-return]
    # pragma: no cover
    return _session_factory_var.get()()  # type: ignore[no-any-return]


async def teardown_thread_safe_context() -> None:
    global _is_single_threaded, _engine  # noqa: F824
    if _is_single_threaded:
        return await _engine.dispose(close=True)  # type: ignore
    engine = _engine_var.get()  # pragma: no cover
    await engine.dispose(close=True)  # pragma: no cover
