"""Enumerations. StrEnum values store and serialize as plain strings."""

from enum import StrEnum


class ConversationStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"


class Direction(StrEnum):
    IN = "in"  # from the customer
    OUT = "out"  # to the customer


class SenderType(StrEnum):
    CONTACT = "contact"  # the customer
    STAFF = "staff"  # a store employee
    AI = "ai"  # the AI agent


class ChannelType(StrEnum):
    RAHULCOOLGRAM = "rahulcoolgram"


class DeliveryStatus(StrEnum):
    """Outgoing messages only. Incoming messages have no delivery status."""

    QUEUED = "queued"  # saved, not yet handed to the channel
    SENT = "sent"  # the channel accepted it
    FAILED = "failed"  # the channel could not be reached or refused it
