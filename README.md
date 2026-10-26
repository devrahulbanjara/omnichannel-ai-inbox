# Omnichannel AI Inbox

One inbox for every customer conversation a store has, with an AI agent that answers questions, recommends products and places orders like a trained staff member. Staff can watch every conversation and take over at any time.

The agent works within strict rules: it can only act through typed tools, and prices, totals, stock and order numbers always come from the database, never from the model.

## What we simulate: RahulCoolGram

<img src="docs/assets/rahulcoolgram.png" alt="RahulCoolGram logo" width="180" align="right">

Real stores get customer messages from Instagram, Messenger, WhatsApp and similar apps. Connecting to those platforms needs app reviews, business accounts and a public server, which slows down learning. So this project ships its own social app, **RahulCoolGram**, a simple Instagram clone that plays both sides:

- **The customer's phone.** An Instagram-style DM screen: pick a customer, message the store, see replies live.
- **The platform.** A small REST API. Every customer message is sent to the inbox backend as a webhook, and the backend replies by calling RahulCoolGram's API. Both sides share a key.

To the inbox backend, RahulCoolGram is just one channel, so a real channel like Instagram or Telegram later is a new adapter, not a redesign.

<br clear="right">

## Repository

| Path | What it is | Status |
|---|---|---|
| `apps/api` | Backend: FastAPI, Python 3.14, Postgres ([structure](#backend-structure)) | Inbox, RahulCoolGram webhook and replies, live updates |
| `apps/web` | Staff dashboard: Next.js | Reads and replies through the API, updates live |
| `apps/rahulcoolgram` | RahulCoolGram, the Instagram clone ([README](apps/rahulcoolgram/README.md)) | Working |
| `docs/` | Blueprint, roadmap, production-grade guide, learning map | — |

## Backend structure

`apps/api/app` is one layered package:

| Folder | Holds |
|---|---|
| `core/` | settings, database engine, logging, request-id middleware, error handling |
| `models/` | SQLAlchemy tables, one per file, with domain behaviour (e.g. `Conversation.reply_as_staff`) |
| `schemas/` | Pydantic request and response shapes |
| `services/` | business logic as classes (`ConversationService`, `MessageService`, `WebhookService`) |
| `channels/` | adapters that send messages out through each messaging app (`RahulCoolGramAdapter`) |
| `routers/` | thin HTTP endpoints that call services |

Schema changes go through Alembic (`apps/api/migrations`). Tests run against a real Postgres database.

## Run it

```bash
# Postgres (Docker)
docker compose up -d --wait

# Backend API → http://localhost:8000 (docs at /docs)
cd apps/api
cp .env.example .env
uv run alembic upgrade head   # create the tables
uv run python -m scripts.seed # demo data (--reset to start over)
uv run fastapi dev

# Dashboard → http://localhost:3000
cd apps/web && npm install && npm run dev

# RahulCoolGram → http://localhost:8100
cd apps/rahulcoolgram && uv run fastapi dev --port 8100
```

Write as a customer in RahulCoolGram: the message appears in the dashboard at once. Reply from the dashboard (assign the conversation to yourself first): the customer sees it in RahulCoolGram.

RahulCoolGram's run instructions are in [`apps/rahulcoolgram/README.md`](apps/rahulcoolgram/README.md).

Requirements: [uv](https://docs.astral.sh/uv/) (installs Python 3.14 for you), Docker and Node.js.
