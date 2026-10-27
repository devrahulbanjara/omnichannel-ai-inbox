"""Model registry. Importing this package registers all tables on Base.metadata."""

from app.models.base import Base
from app.models.channel import Channel
from app.models.contact import Contact
from app.models.contact_identity import ContactIdentity
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.organization import Organization
from app.models.product import Product
from app.models.product_variant import ProductVariant
from app.models.webhook_event import WebhookEvent

__all__ = [
    "Base",
    "Channel",
    "Contact",
    "ContactIdentity",
    "Conversation",
    "Message",
    "Organization",
    "Product",
    "ProductVariant",
    "WebhookEvent",
]
