"""link rahulcoolgram

Adds channels, contact identities and webhook events, and delivery fields on messages.
Existing conversations get a channel row per (org, old channel string) before channel_id
becomes NOT NULL.

Revision ID: e5e54365d7fd
Revises: 0e7a4f35d0f0
Create Date: 2026-10-26 13:30:58.123535

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e5e54365d7fd"
down_revision: str | Sequence[str] | None = "0e7a4f35d0f0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "channels",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("org_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("type IN ('rahulcoolgram')", name=op.f("ck_channels_type_valid")),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.id"], name=op.f("fk_channels_org_id_organizations")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_channels")),
    )
    op.create_index(op.f("ix_channels_org_id"), "channels", ["org_id"], unique=False)
    op.create_table(
        "contact_identities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("org_id", sa.Uuid(), nullable=False),
        sa.Column("contact_id", sa.Uuid(), nullable=False),
        sa.Column("channel_id", sa.Uuid(), nullable=False),
        sa.Column("external_user_id", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["channel_id"], ["channels.id"], name=op.f("fk_contact_identities_channel_id_channels")
        ),
        sa.ForeignKeyConstraint(
            ["contact_id"], ["contacts.id"], name=op.f("fk_contact_identities_contact_id_contacts")
        ),
        sa.ForeignKeyConstraint(
            ["org_id"],
            ["organizations.id"],
            name=op.f("fk_contact_identities_org_id_organizations"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_contact_identities")),
        sa.UniqueConstraint(
            "channel_id",
            "external_user_id",
            name=op.f("uq_contact_identities_channel_id_external_user_id"),
        ),
    )
    op.create_index(
        op.f("ix_contact_identities_contact_id"), "contact_identities", ["contact_id"], unique=False
    )
    op.create_index(
        op.f("ix_contact_identities_org_id"), "contact_identities", ["org_id"], unique=False
    )
    op.create_table(
        "webhook_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("org_id", sa.Uuid(), nullable=False),
        sa.Column("channel_id", sa.Uuid(), nullable=False),
        sa.Column("external_id", sa.String(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["channel_id"], ["channels.id"], name=op.f("fk_webhook_events_channel_id_channels")
        ),
        sa.ForeignKeyConstraint(
            ["org_id"], ["organizations.id"], name=op.f("fk_webhook_events_org_id_organizations")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_webhook_events")),
        sa.UniqueConstraint(
            "channel_id", "external_id", name=op.f("uq_webhook_events_channel_id_external_id")
        ),
    )
    op.create_index(op.f("ix_webhook_events_org_id"), "webhook_events", ["org_id"], unique=False)
    op.add_column("conversations", sa.Column("channel_id", sa.Uuid(), nullable=True))
    op.add_column("conversations", sa.Column("last_message_text", sa.String(), nullable=True))
    op.execute(
        "INSERT INTO channels (id, org_id, type, name) "
        "SELECT uuidv7(), org_id, channel, 'RahulCoolGram' FROM conversations "
        "GROUP BY org_id, channel"
    )
    op.execute(
        "UPDATE conversations c SET channel_id = ch.id FROM channels ch "
        "WHERE ch.org_id = c.org_id AND ch.type = c.channel"
    )
    op.execute(
        "UPDATE conversations c SET last_message_text = ("
        "SELECT m.text FROM messages m WHERE m.conversation_id = c.id "
        "ORDER BY m.created_at DESC LIMIT 1)"
    )
    op.alter_column("conversations", "channel_id", nullable=False)
    op.create_index(
        op.f("ix_conversations_channel_id"), "conversations", ["channel_id"], unique=False
    )
    op.create_foreign_key(
        op.f("fk_conversations_channel_id_channels"),
        "conversations",
        "channels",
        ["channel_id"],
        ["id"],
    )
    op.drop_column("conversations", "channel")
    op.add_column("messages", sa.Column("external_id", sa.String(), nullable=True))
    op.add_column("messages", sa.Column("delivery_status", sa.String(), nullable=True))
    op.add_column("messages", sa.Column("error", sa.String(), nullable=True))
    op.add_column("messages", sa.Column("idempotency_key", sa.String(), nullable=True))
    op.execute("UPDATE messages SET delivery_status = 'sent' WHERE direction = 'out'")
    op.create_check_constraint(
        op.f("ck_messages_delivery_status_valid"),
        "messages",
        "delivery_status IN ('queued', 'sent', 'failed')",
    )
    op.create_unique_constraint(
        op.f("uq_messages_conversation_id_idempotency_key"),
        "messages",
        ["conversation_id", "idempotency_key"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("uq_messages_conversation_id_idempotency_key"), "messages", type_="unique"
    )
    op.drop_constraint(op.f("ck_messages_delivery_status_valid"), "messages", type_="check")
    op.drop_column("messages", "idempotency_key")
    op.drop_column("messages", "error")
    op.drop_column("messages", "delivery_status")
    op.drop_column("messages", "external_id")
    op.add_column("conversations", sa.Column("channel", sa.VARCHAR(), nullable=True))
    op.execute(
        "UPDATE conversations c SET channel = ch.type FROM channels ch WHERE ch.id = c.channel_id"
    )
    op.alter_column("conversations", "channel", nullable=False)
    op.drop_constraint(
        op.f("fk_conversations_channel_id_channels"), "conversations", type_="foreignkey"
    )
    op.drop_index(op.f("ix_conversations_channel_id"), table_name="conversations")
    op.drop_column("conversations", "last_message_text")
    op.drop_column("conversations", "channel_id")
    op.drop_index(op.f("ix_webhook_events_org_id"), table_name="webhook_events")
    op.drop_table("webhook_events")
    op.drop_index(op.f("ix_contact_identities_org_id"), table_name="contact_identities")
    op.drop_index(op.f("ix_contact_identities_contact_id"), table_name="contact_identities")
    op.drop_table("contact_identities")
    op.drop_index(op.f("ix_channels_org_id"), table_name="channels")
    op.drop_table("channels")
