from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import engine
from app.core.errors import add_error_handlers
from app.core.logging import configure_logging
from app.core.middleware import request_id_middleware
from app.routers import conversations, health


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    configure_logging(settings.log_level, json=settings.log_json)

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    add_error_handlers(app)
    app.middleware("http")(request_id_middleware)
    app.include_router(health.router)
    app.include_router(conversations.router)
    return app


app = create_app()
