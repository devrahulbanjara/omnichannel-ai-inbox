<p align="center">
  <img src="static/brand/logo-512.webp" alt="RahulCoolGram" width="180">
</p>

# RahulCoolGram

A simple Instagram-DM clone that plays the **customer side** of the omnichannel inbox.
Customers chat with one store, **Himal Luggage Co.** Every message a customer sends is forwarded
to our omnichannel API, and the API answers by calling RahulCoolGram back. This lets us build the
inbox and the AI agent without connecting real Instagram.

```
 customer (phone UI) ──POST message──▶ RahulCoolGram ──POST webhook──▶ omnichannel API
                                            ▲                                  │
                                            └──── POST /api/store/messages ────┘
```

## Run it

From `apps/rahulcoolgram`:

```bash
uv sync
uv run fastapi dev --port 8100
```

- Phone UI: http://localhost:8100 (tap your avatar or username to switch customer)
- API docs: http://localhost:8100/docs

Data lives in `rahulcoolgram.db` (SQLite). Five demo customers are created on startup. Delete
the file to start fresh.

## Settings

Environment variables, or a `.env` file (see `.env.example`):

| Variable | Default | Meaning |
|---|---|---|
| `OMNICHANNEL_WEBHOOK_URL` | `http://localhost:8000/webhooks/rahulcoolgram` | Where customer messages are forwarded |
| `RAHULCOOLGRAM_API_KEY` | `dev-secret` | Shared secret, sent and checked in the `X-RahulCoolGram-Key` header |
| `DATABASE_PATH` | `rahulcoolgram.db` | SQLite file |

## API

### Used by the phone UI

| Method | Path | Body | Returns |
|---|---|---|---|
| `GET` | `/api/customers` | | `[{"id", "name", "username", "avatar"}]` |
| `GET` | `/api/store` | | `{"name", "username"}` |
| `GET` | `/api/customers/{customer_id}/messages` | | chat history, oldest first |
| `POST` | `/api/customers/{customer_id}/messages` | `{"text"}` | the saved message (`201`) |

A message looks like:

```json
{"id": "…uuid…", "customer_id": "sujan", "sender": "customer", "text": "Do you have black bags?",
 "sent_at": "2026-10-24T10:35:00+00:00"}
```

`sender` is `"customer"` or `"store"`.

### What RahulCoolGram sends to the omnichannel API

When a customer sends a message, RahulCoolGram saves it and then makes this request:

```http
POST {OMNICHANNEL_WEBHOOK_URL}
X-RahulCoolGram-Key: dev-secret
Content-Type: application/json

{
  "message_id": "…uuid…",
  "customer": {"id": "sujan", "name": "Sujan Maharjan", "username": "sujan.mhj"},
  "text": "Do you have black bags?",
  "sent_at": "2026-10-24T10:35:00+00:00"
}
```

If the omnichannel API is not running or answers with an error, the message is still saved and
a warning is logged. There are no retries.

### How the omnichannel API replies

```http
POST /api/store/messages
X-RahulCoolGram-Key: dev-secret
Content-Type: application/json

{"customer_id": "sujan", "text": "Yes! We have three sizes in black."}
```

Returns `201 {"message_id": "…"}`. A wrong or missing key gives `401`, an unknown customer
gives `404`. The reply shows up in the customer's phone within about 1.5 s (the UI polls).

Try it without the omnichannel API:

```bash
curl -X POST localhost:8100/api/store/messages \
  -H 'X-RahulCoolGram-Key: dev-secret' -H 'Content-Type: application/json' \
  -d '{"customer_id": "sujan", "text": "Namaste! How can we help?"}'
```

## Develop

```bash
uv run pytest
uv run ruff check . && uv run ruff format --check .
```

## Files

| File | What it does |
|---|---|
| `main.py` | FastAPI app and all routes |
| `db.py` | SQLite tables (`customers`, `messages`), demo customers, queries |
| `settings.py` | Settings from environment variables |
| `static/` | Phone UI (`index.html`, `app.js`, `style.css`), logo and avatars |
| `tests/` | API tests |
