"""RahulCoolGram: a simple Instagram-DM clone.

Customers chat with one store (Himal Luggage Co.). Every customer message is forwarded to our
omnichannel API; the API replies by calling POST /api/store/messages.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import db
from settings import settings

log = logging.getLogger("rahulcoolgram")
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db.init_db(settings.database_path)
    yield


app = FastAPI(title="RahulCoolGram", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class NewCustomerMessage(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


class NewStoreMessage(BaseModel):
    customer_id: str
    text: str = Field(min_length=1, max_length=1000)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/customers")
def list_customers() -> list[dict]:
    customers = db.list_customers(settings.database_path)
    result = []
    for customer in customers:
        customer["avatar"] = avatar_url(customer["id"])
        result.append(customer)
    return result


@app.get("/api/store")
def store() -> dict:
    return {"name": db.STORE_NAME, "username": "himal.luggage"}


@app.get("/api/customers/{customer_id}/messages")
def list_messages(customer_id: str) -> list[dict]:
    require_customer(customer_id)
    return db.list_messages(settings.database_path, customer_id)


@app.post("/api/customers/{customer_id}/messages", status_code=201)
async def customer_sends(customer_id: str, body: NewCustomerMessage) -> dict:
    """A customer sends a message: save it, then tell our omnichannel API about it."""
    customer = require_customer(customer_id)
    message = db.add_message(settings.database_path, customer_id, "customer", body.text)
    await forward_to_omnichannel(customer, message)
    return message


@app.post("/api/store/messages", status_code=201)
def store_replies(
    body: NewStoreMessage,
    x_rahulcoolgram_key: Annotated[str | None, Header()] = None,
) -> dict:
    """Our omnichannel API calls this to reply to a customer as the store."""
    if x_rahulcoolgram_key != settings.rahulcoolgram_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-RahulCoolGram-Key")
    require_customer(body.customer_id)
    message = db.add_message(settings.database_path, body.customer_id, "store", body.text)
    return {"message_id": message["id"]}


def require_customer(customer_id: str) -> dict:
    customer = db.get_customer(settings.database_path, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Unknown customer")
    return customer


def avatar_url(customer_id: str) -> str:
    return f"/static/avatars/{customer_id}.svg"


async def forward_to_omnichannel(customer: dict, message: dict) -> None:
    """POST the message to our omnichannel API. If that fails, keep going: the message is saved."""
    payload = {
        "message_id": message["id"],
        "customer": {
            "id": customer["id"],
            "name": customer["name"],
            "username": customer["username"],
        },
        "text": message["text"],
        "sent_at": message["sent_at"],
    }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(
                settings.omnichannel_webhook_url,
                json=payload,
                headers={"X-RahulCoolGram-Key": settings.rahulcoolgram_api_key},
            )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        log.warning("Could not forward message %s to omnichannel API: %s", message["id"], exc)
