from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI

from chatbot.infra.db.postgres import (
    create_thread_safe_context,
    teardown_thread_safe_context,
)
from chatbot.infra.http.routes.bot.resources import router as bot_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    create_thread_safe_context(is_single_threaded=True)
    try:
        yield
    finally:
        await teardown_thread_safe_context()


def configure_routes(application: FastAPI) -> None:
    api_router = APIRouter()
    api_router.include_router(bot_router)
    application.include_router(api_router)


def create_application() -> FastAPI:
    application = FastAPI(lifespan=lifespan, version="1.0.0")
    configure_routes(application)
    return application


app = create_application()
