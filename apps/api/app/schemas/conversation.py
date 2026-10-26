import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ConversationStatus


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    contact_name: Annotated[str, Field(description="The customer's display name on their channel")]
    channel: Annotated[
        str,
        Field(
            validation_alias="channel_type",
            description="The app the customer wrote from, e.g. rahulcoolgram",
        ),
    ]
    status: ConversationStatus
    last_message_at: Annotated[
        datetime,
        Field(description="When the latest message was sent (UTC). The inbox sorts by this"),
    ]
    last_message_text: Annotated[
        str | None, Field(description="Text of the latest message, for the preview line")
    ]
