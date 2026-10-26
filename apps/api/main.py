from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from core.config import settings
from core.db import SessionDep, engine
from core.errors import add_error_handlers
from core.logs import configure_logging
from core.request_id import request_id_middleware
from inbox.routes import router as inbox_router

configure_logging(settings.log_level, json=settings.log_json)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()  # close database connections on shutdown


app = FastAPI(title=settings.app_name, lifespan=lifespan)
add_error_handlers(app)
app.middleware("http")(request_id_middleware)
app.include_router(inbox_router)


@app.get("/health/live")
def live() -> dict[str, str]:
    """The process is running. A failing check here means: restart it."""
    return {"status": "ok"}


@app.get("/health/ready")
async def ready(session: SessionDep):
    """The API can do real work. A failing check here means: send no traffic yet."""
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "database unavailable"})
    return {"status": "ok"}
