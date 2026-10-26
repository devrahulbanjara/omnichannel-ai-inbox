# 0004. Linking RahulCoolGram: webhooks in, adapter out, live updates

- **Status:** Accepted
- **Date:** 2026-10-26

## Context

Customer messages must flow from RahulCoolGram into the inbox, staff replies must flow back, and the dashboard must update without a refresh. There is no login, no worker and no Redis yet; one API process serves everything.

## Decision

- **Channels table.** A webhook finds its organization through a `channels` row. Contacts link to a channel account through `contact_identities` (`UNIQUE(channel_id, external_user_id)`), so a customer's messages always land in the same conversation.
- **Inbound.** `POST /webhooks/rahulcoolgram` checks the shared `X-RahulCoolGram-Key` before reading the body, stores the body in `webhook_events`, and dedupes with `UNIQUE(channel_id, external_id)` + `ON CONFLICT DO NOTHING`. Saving the event and the message is one transaction, so a resend is a no-op and a failure stores nothing.
- **Outbound.** A staff reply is committed as `queued` first, then sent through a `ChannelAdapter` (`RahulCoolGramAdapter`, httpx, 5 s timeout) inside the request, and marked `sent` or `failed` with the reason. An `Idempotency-Key` header (`UNIQUE(conversation_id, idempotency_key)`) makes a resent reply return the first one.
- **Live updates.** A WebSocket at `/live` and an in-process `EventHub`. Events say only *what changed* (`message.created` / `message.updated` + conversation id); the dashboard refetches that data, and refetches everything after a reconnect.

Rejected:

- **Polling only:** simpler, but every dashboard asks every few seconds and updates still lag.
- **Redis pub/sub now:** needed only once there are several API processes.
- **Retrying failed deliveries inside the request:** a slow channel would block the staff member; retries belong to the background worker.
- **HMAC signatures:** what real platforms use; a shared key is enough for our own test channel.

## Consequences

- Real tenancy plumbing exists: every query is scoped to an organization. Without login the "current" organization is the oldest one.
- Delivery failures are visible on the message (`failed` + reason), never silent, but nothing retries them yet.
- The event hub lives in one process: a second API process would not see the other's events (Redis pub/sub fixes this later). Every connected dashboard gets every event until login exists.
- Two webhooks for the same *new* customer at the same moment can race on contact creation; the unique key turns the loser into an error rather than a duplicate contact.
