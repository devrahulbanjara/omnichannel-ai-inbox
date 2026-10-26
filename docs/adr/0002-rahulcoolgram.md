# 0002. Simulate a social channel with RahulCoolGram

- **Status:** Accepted
- **Date:** 2026-10-26

## Context

The inbox needs customer messages from a social app to be useful. Connecting a real one (Instagram,
Messenger, WhatsApp) needs a business account, app review, a public HTTPS server and real test users.
That is days of setup before the first message arrives, and every test depends on someone else's
platform. The goal right now is to learn and build the inbox and the AI agent, not platform paperwork.

## Decision

Build our own small Instagram clone, **RahulCoolGram** (`apps/simulator`):

- A customer chat UI that looks like Instagram DMs.
- A plain FastAPI REST API. Each customer message is POSTed to our webhook with a shared key
  (`X-RahulCoolGram-Key`); our API replies through `POST /api/store/messages`.
- Our API talks to it only through a `ChannelAdapter`, never by reading its database.

Rejected:

- **Real Instagram / Telegram now:** too much setup before any learning happens.
- **A faithful copy of Meta's Graph API:** tried it; too complex for what it teaches. Simple REST is enough.
- **No simulator, just curl:** works for tests, but we can't see a real conversation.

## Consequences

- Easier: run everything locally, test any scenario, reset data any time.
- Easier: the `ChannelAdapter` boundary is real from day one, so a real channel later is a new adapter.
- Harder: RahulCoolGram is friendlier than a real platform. Real channels will bring surprises
  (signatures, rate limits, retries, message formats) that we must handle when we add them.
- Watch: never let the API depend on RahulCoolGram internals, or the adapter boundary becomes fake.
