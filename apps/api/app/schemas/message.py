import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Direction, SenderType


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: Annotated[
        uuid.UUID, Field(description="The conversation this message belongs to")
    ]
    direction: Annotated[
        Direction, Field(description="in = from the customer, out = to the customer")
    ]
    sender_type: Annotated[
        SenderType,
        Field(description="contact = the customer, staff = a store employee, ai = the AI agent"),
    ]
    text: str
    created_at: Annotated[datetime, Field(description="When the message was sent (UTC)")]


class MessageCreate(BaseModel):
    """Staff reply body. All other message fields are set by the server."""

    text: Annotated[str, Field(min_length=1, max_length=2000)]
