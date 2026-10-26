"""Model behaviour tests (no database)."""

import uuid
from datetime import UTC, datetime

from app.models import Conversation
from app.models.enums import Direction, SenderType


def make_conversation() -> Conversation:
    return Conversation(
        id=uuid.uuid7(),
        org_id=uuid.uuid7(),
        contact_id=uuid.uuid7(),
        channel="rahulcoolgram",
        last_message_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def test_staff_reply_is_outgoing_from_staff():
    conversation = make_conversation()

    message = conversation.reply_as_staff("Yes, we have it.")

    assert message.direction == Direction.OUT
    assert message.sender_type == SenderType.STAFF
    assert message.conversation_id == conversation.id
    assert message.org_id == conversation.org_id


def test_staff_reply_becomes_the_latest_activity():
    conversation = make_conversation()

    message = conversation.reply_as_staff("Yes, we have it.")

    assert conversation.last_message_at == message.created_at
