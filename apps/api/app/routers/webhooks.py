import hmac
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.exceptions import UnauthorizedError
from app.schemas.error import ERROR_RESPONSES
from app.schemas.webhook import RahulCoolGramWebhook, WebhookReceipt
from app.services.webhook import WebhookService

router = APIRouter(prefix="/webhooks", tags=["webhooks"], responses=ERROR_RESPONSES)


def check_rahulcoolgram_key(
    x_rahulcoolgram_key: Annotated[str, Header()] = "",
) -> None:
    # compare_digest takes the same time for any wrong key, so timing reveals nothing.
    if not hmac.compare_digest(x_rahulcoolgram_key, settings.rahulcoolgram_api_key):
        raise UnauthorizedError("Invalid or missing X-RahulCoolGram-Key")


@router.post("/rahulcoolgram", dependencies=[Depends(check_rahulcoolgram_key)])
async def receive_rahulcoolgram(
    body: RahulCoolGramWebhook,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> WebhookReceipt:
    webhook_service = WebhookService(session)
    saved = await webhook_service.receive_rahulcoolgram(body)
    return WebhookReceipt(status="saved" if saved else "duplicate")
