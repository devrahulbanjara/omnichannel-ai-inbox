"""The shapes of data our API sends and receives (Pydantic models)."""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class Conversation(BaseModel):
    id: str
    contact_name: Annotated[str, Field(description="The customer's display name on their channel")]
    channel: Annotated[
        str, Field(description="The app the customer wrote from: rahulcoolgram, whatsapp")
    ]
    status: Literal["open", "resolved"]
    last_message_at: Annotated[
        datetime,
        Field(description="When the latest message was sent (UTC). The inbox sorts by this"),
    ]


class Message(BaseModel):
    id: str
    conversation_id: Annotated[str, Field(description="The conversation this message belongs to")]
    direction: Annotated[
        Literal["in", "out"],
        Field(description="in = from the customer, out = to the customer"),
    ]
    sender_type: Annotated[
        Literal["contact", "staff", "ai"],
        Field(description="contact = the customer, staff = a store employee, ai = the AI agent"),
    ]
    text: str
    created_at: Annotated[datetime, Field(description="When the message was sent (UTC)")]


class MessageCreate(BaseModel):
    """Body of a staff reply. Only the text: the server decides id, direction, sender and time."""

    text: Annotated[str, Field(min_length=1, max_length=2000)]
