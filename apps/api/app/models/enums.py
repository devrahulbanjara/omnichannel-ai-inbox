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
