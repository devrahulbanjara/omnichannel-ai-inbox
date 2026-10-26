from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.dependencies import SessionDep

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def ready(session: SessionDep):
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(status_code=503, content={"status": "database unavailable"})
    return {"status": "ok"}
