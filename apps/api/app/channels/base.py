from typing import Protocol


class DeliveryError(Exception):
    """The channel could not be reached or refused the message. The text is shown to staff."""


class ChannelAdapter(Protocol):
    """Sends messages out through one messaging app."""

    async def send(self, external_user_id: str, text: str) -> str:
        """Send text to the customer; return the channel's id for the message."""
        ...
