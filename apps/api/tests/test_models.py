"""Model behaviour tests (no database)."""

import uuid
from datetime import UTC, datetime

from app.models import Conversation
from app.models.enums import DeliveryStatus, Direction, SenderType


def make_conversation() -> Conversation:
    return Conversation(
        id=uuid.uuid7(),
        org_id=uuid.uuid7(),
        customer_id=uuid.uuid7(),
        channel_id=uuid.uuid7(),
        last_message_at=datetime(2026, 1, 1, tzinfo=UTC),
        unread_count=0,
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


def test_staff_reply_waits_for_delivery():
    conversation = make_conversation()

    message = conversation.reply_as_staff("Yes, we have it.")

    assert message.delivery_status == DeliveryStatus.QUEUED


def test_customer_message_is_incoming_and_keeps_the_channel_id():
    conversation = make_conversation()

    message = conversation.receive_from_customer("Hi", external_id="rcg-message-1")

    assert message.direction == Direction.IN
    assert message.sender_type == SenderType.CUSTOMER
    assert message.external_id == "rcg-message-1"
    assert message.delivery_status is None


def test_latest_message_becomes_the_preview():
    conversation = make_conversation()

    conversation.receive_from_customer("Hi", external_id="rcg-message-1")
    conversation.reply_as_staff("Hello! How can I help?")

    assert conversation.last_message_text == "Hello! How can I help?"


def test_customer_message_counts_as_unread():
    conversation = make_conversation()

    conversation.receive_from_customer("Hi", external_id="rcg-message-1")
    conversation.receive_from_customer("Anyone?", external_id="rcg-message-2")

    assert conversation.unread_count == 2


def test_mark_read_clears_the_unread_count():
    conversation = make_conversation()
    conversation.receive_from_customer("Hi", external_id="rcg-message-1")

    changed = conversation.mark_read()

    assert changed is True
    assert conversation.unread_count == 0


def test_mark_read_reports_no_change_when_nothing_is_unread():
    conversation = make_conversation()

    assert conversation.mark_read() is False


def test_ai_reply_is_outgoing_from_ai_and_queued():
    conversation = make_conversation()

    message = conversation.reply_as_ai("We have black suitcases.")

    assert message.direction == Direction.OUT
    assert message.sender_type == SenderType.AI
    assert message.delivery_status == DeliveryStatus.QUEUED
    assert conversation.last_message_text == "We have black suitcases."
