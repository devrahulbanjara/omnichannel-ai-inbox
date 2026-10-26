from fastapi import FastAPI

from core.config import settings
from core.errors import add_error_handlers
from core.logs import configure_logging
from core.request_id import request_id_middleware
from inbox.routes import router as inbox_router

configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)
add_error_handlers(app)
app.middleware("http")(request_id_middleware)
app.include_router(inbox_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
