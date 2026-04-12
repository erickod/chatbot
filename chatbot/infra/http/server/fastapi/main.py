from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI

from chatbot.infra.http.routes.bot.resources import router as bot_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


def configure_routes(application: FastAPI) -> None:
    api_router = APIRouter()
    api_router.include_router(bot_router)
    application.include_router(api_router)


def create_application() -> FastAPI:
    application = FastAPI(lifespan=lifespan, version="1.0.0")
    configure_routes(application)
    return application


app = create_application()
