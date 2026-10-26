"""Model registry. Importing this package registers all tables on Base.metadata."""

from app.models.base import Base
from app.models.contact import Contact
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.organization import Organization

__all__ = ["Base", "Contact", "Conversation", "Message", "Organization"]
