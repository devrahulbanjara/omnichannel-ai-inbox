from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class RahulCoolGramCustomer(BaseModel):
    id: Annotated[str, Field(min_length=1, max_length=100)]
    name: Annotated[str, Field(min_length=1, max_length=200)]
    username: Annotated[str, Field(max_length=100)]


class RahulCoolGramWebhook(BaseModel):
    """Body RahulCoolGram sends for every customer message."""

    message_id: Annotated[str, Field(min_length=1, max_length=100)]
    customer: RahulCoolGramCustomer
    text: Annotated[str, Field(min_length=1, max_length=2000)]
    sent_at: datetime


class WebhookReceipt(BaseModel):
    status: Annotated[
        Literal["saved", "duplicate"],
        Field(description="duplicate = this message_id was already received; nothing changed"),
    ]
