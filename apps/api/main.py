from fastapi import FastAPI

from core.config import settings
from inbox.routes import router as inbox_router

app = FastAPI(title=settings.app_name)
app.include_router(inbox_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
