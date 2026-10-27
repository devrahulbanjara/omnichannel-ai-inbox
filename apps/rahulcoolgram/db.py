"""SQLite storage: customers and their messages with the store."""

import sqlite3
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime

STORE_NAME = "Himal Luggage Co."

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    id        TEXT PRIMARY KEY,
    name      TEXT NOT NULL,
    username  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id           TEXT PRIMARY KEY,
    customer_id  TEXT NOT NULL REFERENCES customers(id),
    sender       TEXT NOT NULL CHECK (sender IN ('customer', 'store')),
    text         TEXT NOT NULL,
    sent_at      TEXT NOT NULL
);
"""

PERSONAS = [
    ("sujan", "Sujan Maharjan", "sujan.mhj"),
    ("anisha", "Anisha Karki", "anisha.k"),
    ("bikash", "Bikash Thapa", "bikash_thapa"),
    ("srijana", "Srijana Shrestha", "srijana.shr"),
    ("prabin", "Prabin Gurung", "prabin.grg"),
]


@contextmanager
def connect(path: str) -> Iterator[sqlite3.Connection]:
    """Open a connection, commit if everything worked, and always close it."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db(path: str) -> None:
    """Create the tables and add the demo customers if they are missing."""
    with connect(path) as conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT OR IGNORE INTO customers (id, name, username) VALUES (?, ?, ?)", PERSONAS
        )


def list_customers(path: str) -> list[dict]:
    with connect(path) as conn:
        rows = conn.execute("SELECT * FROM customers ORDER BY rowid").fetchall()
    result = []
    for row in rows:
        result.append(dict(row))
    return result


def get_customer(path: str, customer_id: str) -> dict | None:
    with connect(path) as conn:
        row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    return dict(row) if row else None


def list_messages(path: str, customer_id: str) -> list[dict]:
    with connect(path) as conn:
        rows = conn.execute(
            "SELECT * FROM messages WHERE customer_id = ? ORDER BY sent_at, rowid",
            (customer_id,),
        ).fetchall()
    result = []
    for row in rows:
        result.append(dict(row))
    return result


def add_message(path: str, customer_id: str, sender: str, text: str) -> dict:
    message = {
        "id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "sender": sender,
        "text": text,
        "sent_at": datetime.now(UTC).isoformat(),
    }
    with connect(path) as conn:
        conn.execute(
            "INSERT INTO messages (id, customer_id, sender, text, sent_at) "
            "VALUES (:id, :customer_id, :sender, :text, :sent_at)",
            message,
        )
    return message
