import httpx

from app.channels.base import DeliveryError
from app.core.config import settings

TIMEOUT_SECONDS = 5


class RahulCoolGramAdapter:
    async def send(self, external_user_id: str, text: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                response = await client.post(
                    f"{settings.rahulcoolgram_url}/api/store/messages",
                    json={"customer_id": external_user_id, "text": text},
                    headers={"X-RahulCoolGram-Key": settings.rahulcoolgram_api_key},
                )
        except httpx.TimeoutException as exc:
            raise DeliveryError("RahulCoolGram did not answer in time") from exc
        except httpx.HTTPError as exc:
            raise DeliveryError("Could not reach RahulCoolGram") from exc

        if response.is_error:
            raise DeliveryError(f"RahulCoolGram refused the message ({response.status_code})")
        return response.json()["message_id"]
