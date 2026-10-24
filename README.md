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
| `apps/api` | Backend: FastAPI, Python 3.14 | Started |
| `apps/web` | Staff dashboard: Next.js | UI on mock data |
| `apps/simulator` | RahulCoolGram, the Instagram clone ([README](apps/simulator/README.md)) | Working |
| `docs/` | Blueprint, roadmap, production-grade guide, learning map | — |

## Run it

```bash
# Backend API → http://localhost:8000 (docs at /docs)
cd apps/api && uv run fastapi dev

# Dashboard → http://localhost:3000
cd apps/web && npm install && npm run dev
```

RahulCoolGram's run instructions are in [`apps/simulator/README.md`](apps/simulator/README.md).

Requirements: [uv](https://docs.astral.sh/uv/) (installs Python 3.14 for you) and Node.js.

## Docs

- [`docs/BLUEPRINT.md`](docs/BLUEPRINT.md): the target architecture
- [`docs/ROADMAP.md`](docs/ROADMAP.md): the step-by-step build plan and progress
- [`docs/PRODUCTION_GRADE.md`](docs/PRODUCTION_GRADE.md): what makes it production-grade, and the tool choices
- [`docs/learn.md`](docs/learn.md): the concepts behind it, in study order
