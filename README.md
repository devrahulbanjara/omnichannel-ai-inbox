# Omnichannel AI Inbox

One inbox for every customer conversation a store has, with an AI agent that answers questions, recommends products and places orders like a trained staff member. Staff can watch every conversation and take over at any time.

The agent works within strict rules: it can only act through typed tools, and prices, totals, stock and order numbers always come from the database, never from the model.

## What we simulate: RahulCoolGram

<img src="docs/assets/rahulcoolgram.png" alt="RahulCoolGram logo" width="180" align="right">

Real stores get customer messages from Instagram, Messenger, WhatsApp and similar apps. Connecting to those platforms needs app reviews, business accounts and a public server, which slows down learning. So this project ships its own social app, **RahulCoolGram**, a fake Instagram that plays both sides:

- **The customer's phone.** A DM-style chat screen: pick a customer, message a store, see replies, tap product cards and buttons.
- **The platform.** A fake version of Meta's messaging API that behaves like the real one: signed webhooks, the URL verification handshake, retries, duplicate and batched deliveries, a Send API with access tokens, read receipts, button postbacks, and a "connect your account" flow.

The inbox backend talks to RahulCoolGram exactly as it would talk to Instagram, so a real channel later is just a new adapter. RahulCoolGram can also misbehave on purpose (duplicates, delays, failures) to prove the backend never loses or duplicates a message.

<br clear="right">

## Repository

| Path | What it is | Status |
|---|---|---|
| `apps/api` | Backend: FastAPI, Python 3.14 | Started |
| `apps/web` | Staff dashboard: Next.js | UI on mock data |
| `apps/simulator` | RahulCoolGram simulator ([README](apps/simulator/README.md)) | In progress |
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
