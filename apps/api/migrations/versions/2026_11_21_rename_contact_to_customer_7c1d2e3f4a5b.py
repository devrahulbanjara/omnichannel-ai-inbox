"""rename contact to customer

Renames the contacts and contact_identities tables, the contact_id columns, their constraints
and indexes, and the 'contact' sender type. Rows are kept.

Revision ID: 7c1d2e3f4a5b
Revises: 99f842189a41
Create Date: 2026-11-21 14:45:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7c1d2e3f4a5b"
down_revision: str | Sequence[str] | None = "99f842189a41"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# (table, old name, new name) for every constraint and index named after "contact".
CONSTRAINTS = [
    ("customers", "pk_contacts", "pk_customers"),
    ("customers", "fk_contacts_org_id_organizations", "fk_customers_org_id_organizations"),
    ("customer_identities", "pk_contact_identities", "pk_customer_identities"),
    (
        "customer_identities",
        "fk_contact_identities_org_id_organizations",
        "fk_customer_identities_org_id_organizations",
    ),
    (
        "customer_identities",
        "fk_contact_identities_contact_id_contacts",
        "fk_customer_identities_customer_id_customers",
    ),
    (
        "customer_identities",
        "fk_contact_identities_channel_id_channels",
        "fk_customer_identities_channel_id_channels",
    ),
    (
        "customer_identities",
        "uq_contact_identities_channel_id_external_user_id",
        "uq_customer_identities_channel_id_external_user_id",
    ),
    (
        "conversations",
        "fk_conversations_contact_id_contacts",
        "fk_conversations_customer_id_customers",
    ),
]
INDEXES = [
    ("ix_contacts_org_id", "ix_customers_org_id"),
    ("ix_contact_identities_org_id", "ix_customer_identities_org_id"),
    ("ix_contact_identities_contact_id", "ix_customer_identities_customer_id"),
    ("ix_conversations_contact_id", "ix_conversations_customer_id"),
]


def upgrade() -> None:
    """Upgrade schema."""
    op.rename_table("contacts", "customers")
    op.rename_table("contact_identities", "customer_identities")
    op.alter_column("customer_identities", "contact_id", new_column_name="customer_id")
    op.alter_column("conversations", "contact_id", new_column_name="customer_id")

    for table, old_name, new_name in CONSTRAINTS:
        op.execute(f"ALTER TABLE {table} RENAME CONSTRAINT {old_name} TO {new_name}")
    for old_name, new_name in INDEXES:
        op.execute(f"ALTER INDEX {old_name} RENAME TO {new_name}")

    # The check constraint must allow the new value before the rows change.
    op.drop_constraint(op.f("ck_messages_sender_type_valid"), "messages", type_="check")
    op.execute("UPDATE messages SET sender_type = 'customer' WHERE sender_type = 'contact'")
    op.create_check_constraint(
        op.f("ck_messages_sender_type_valid"),
        "messages",
        "sender_type IN ('customer', 'staff', 'ai')",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("ck_messages_sender_type_valid"), "messages", type_="check")
    op.execute("UPDATE messages SET sender_type = 'contact' WHERE sender_type = 'customer'")
    op.create_check_constraint(
        op.f("ck_messages_sender_type_valid"),
        "messages",
        "sender_type IN ('contact', 'staff', 'ai')",
    )

    for old_name, new_name in INDEXES:
        op.execute(f"ALTER INDEX {new_name} RENAME TO {old_name}")
    for table, old_name, new_name in CONSTRAINTS:
        op.execute(f"ALTER TABLE {table} RENAME CONSTRAINT {new_name} TO {old_name}")

    op.alter_column("conversations", "customer_id", new_column_name="contact_id")
    op.alter_column("customer_identities", "customer_id", new_column_name="contact_id")
    op.rename_table("customer_identities", "contact_identities")
    op.rename_table("customers", "contacts")
