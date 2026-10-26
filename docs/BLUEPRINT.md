# AI Omnichannel Inbox & Conversational Commerce Platform — Blueprint

A multi-tenant platform where stores see customer messages from every channel in one inbox, and an autonomous AI agent sells, supports and operates like a trained staff member — within strict, code-enforced rules.

---

## 1. Core principles

1. **The LLM chooses, code decides.** Prices, totals, delivery fees, stock, IDs and statuses always come from the database or tool results — never from model text.
2. **One service, many callers.** Every action (create order, create ticket, update contact) is a single application service. The UI (REST) and the AI (tool) are thin adapters over it.
3. **The server injects identity.** `org_id`, `conversation_id`, `contact_id`, actor — never supplied by the model.
4. **Every write is idempotent.** Webhooks retry, workers retry, customers say "yes" twice.
5. **Every state change emits an event.** Events drive realtime UI, CRM sync, analytics and audit.
6. **Everything the AI does is recorded.** Runs, tool calls, tokens, cost, checker verdicts.
7. **Customer content is untrusted input.** Treat every inbound message as a possible prompt injection.

---

## 2. Stack

Locked choices are marked 🔒. The rest are proposals until decided.

| Layer | Choice |
|---|---|
| Backend API 🔒 | Python 3.14, **FastAPI**, Pydantic v2 |
| ORM / migrations 🔒 | SQLAlchemy 2 (async) + Alembic |
| Database 🔒 | **PostgreSQL 16 + pgvector** (row-level security for tenancy) |
| Background jobs 🔒 | **Procrastinate** (async, Postgres-backed; retries, scheduling, queueing locks) |
| Pub-sub / rate limits | Redis |
| Realtime | FastAPI WebSockets + Redis pub/sub fan-out |
| AI layer 🔒 | Own agent loop, no framework. Pydantic AI is the fallback if the loop outgrows itself. |
| LLM 🔒 | Hosted free tiers, no local models: **Groq** (primary), **Gemini** (fallback). One OpenAI-compatible adapter for both. |
| Embeddings | Gemini embeddings API (free tier), multilingual for Nepali / Roman Nepali |
| Dashboard 🔒 | **Next.js** (App Router) + TypeScript + Tailwind CSS v4 + shadcn/ui (Radix) + lucide-react + TanStack Query; glass UI design system (see `apps/web`) |
| Chat widget | Preact + TypeScript, single `<script>` embed, iframe-isolated |
| Object storage | MinIO (S3-compatible) |
| LLM tracing & evals | Langfuse (Cloud Hobby tier first; self-host optional later — needs ClickHouse + Redis + S3). Own eval harness. Not LangSmith (LangChain-centric, proprietary). |
| Logs / metrics / traces | OpenTelemetry → Grafana, Prometheus, Tempo, Loki (`grafana/otel-lgtm` single container in dev) |
| Testing | pytest, Playwright (E2E), k6 (load) |
| Local infra | Docker Compose; Cloudflare Tunnel for public webhook URLs |
| CI | GitHub Actions (lint, typecheck, tests, evals, migrations check) |

### Decision log

**FastAPI + Pydantic.** The hardest part is the AI agent, and Python has the strongest ecosystem for it. FastAPI is async-first, which suits an I/O-bound system (webhooks, channel APIs, LLM calls). One set of Pydantic models validates requests, webhook payloads and LLM tool arguments, and produces the OpenAPI schema the frontend client is generated from.

**PostgreSQL + pgvector.** One database for tenant data, the store catalog, embeddings and the job queue, so order creation and conversation state commit in one transaction. Row-level security makes tenant isolation a database guarantee. A separate vector store would add a sync problem without a scale benefit at this size.

**SQLAlchemy 2 + Alembic.** Mature async ORM with explicit transactions, needed for `SET LOCAL app.org_id` (RLS) and for writing data and its follow-up job atomically. Alembic gives reviewable migration history.

**Procrastinate instead of FastAPI `BackgroundTasks`.** `BackgroundTasks` runs in the API process after the response is sent: a crash or deploy loses the job, and since the webhook was already acknowledged the channel will not retry, so the customer never gets a reply. It also has no retries, no delayed jobs, no cross-instance locking and no visibility, and long agent runs would compete with API requests. A real queue fixes all of these. `BackgroundTasks` is kept only for non-critical fire-and-forget work.

**Procrastinate instead of Taskiq or Celery.** Jobs are rows in Postgres, so a message insert and its agent job are enqueued in the same transaction: both happen or neither does. A Redis-backed queue can drift from the database and needs an outbox to stay consistent. Procrastinate is async-native (Celery is not), supports retries, scheduled jobs and queueing locks (one agent run per conversation), and removes Redis from the critical path.

**Own agent loop, no LangChain or LangGraph.** The loop itself is about 150 lines. The difficult parts are domain rules no framework supplies: tool gating per sales state, server-injected identity, idempotent orders, the pre-send checker, handoff and credit metering. LangChain adds opaque abstractions and churn; LangGraph's checkpointing duplicates what Postgres and the job queue already provide. Pydantic AI is the only framework that fits the stack and is the planned fallback; tools are written as typed functions with Pydantic input models so that switch stays small.

**Groq primary, Gemini fallback.** Groq's free tier has the more usable rate limits and very low latency, which matters for a chat agent. Gemini covers outages and 429s. Both expose an OpenAI-compatible chat API, so a single adapter with a different base URL serves both (Gemini's tool-calling support through its compatibility layer is to be verified before relying on it).

---

## 3. System architecture

```
 Channels                                 ┌──────────────── Dashboard (Next.js) ───────────────┐
 Web widget · Telegram · Messenger ·      │ Inbox · Conversation · Sidebar · Tickets · Orders │
 Instagram · WhatsApp · Email             │ Catalog · AI settings · Analytics · Billing       │
        │ webhooks / WS                   └───────────────▲──────────────────▲────────────────┘
        ▼                                                 │ REST             │ WebSocket
 ┌──────────────┐   enqueue   ┌──────────────┐            │                  │
 │ Ingress API  │────────────▶│ Postgres jobs│      ┌─────┴──────────────────┴─────┐
 │ verify+ack   │             └──────┬───────┘      │          Core API            │
 └──────────────┘                    ▼              │ auth · RBAC · services       │
                             ┌──────────────┐       └─────┬────────────────────────┘
                             │   Workers    │             │
                             │ normalize    │◀────────────┤ application services
                             │ agent runs   │             │ (Conversation, Message, Order,
                             │ analyzer     │             │  Ticket, Contact, Catalog, Credit)
                             │ outbound     │             ▼
                             │ sync jobs    │      ┌──────────────┐   ┌──────────┐
                             └──────┬───────┘─────▶│ PostgreSQL   │   │ MinIO    │
                                    │              │ + pgvector   │   └──────────┘
                                    ▼              └──────┬───────┘
                             ┌──────────────┐   outbox    │
                             │ LLM provider │   relay     ▼
                             └──────────────┘      Redis pub/sub → WebSocket rooms
```

Layering inside the backend (dependencies point inward):

```
domain (entities, state machines, rules)
  ← application (services, use cases, events)
    ← adapters (channels, LLM, payments, courier, CRM, storage)
      ← interfaces (REST routes, webhook routes, AI tools, workers)
```

---

## 4. Tenancy, auth, permissions

- **Tenant = organization (store).** A user can belong to many orgs (org switcher).
- Every tenant table has `org_id`. Postgres **row-level security**: each request/job runs `SET LOCAL app.org_id = …`; policies filter by it.
- **Auth:** email + password (argon2id), httpOnly secure session cookies, CSRF protection; Google OAuth later. Email invites for team members.
- **Roles:** `owner`, `admin`, `agent`. Actor types: `user`, `ai`, `system`.
- **AI permission policy** (separate from human roles): which tools the AI may call, which need customer confirmation, which are forbidden (e.g. close ticket, refund, delete).

---

## 5. Data model

```
organization(id, name, slug, timezone, currency, settings JSONB)
user(id, email, password_hash, name)
membership(user_id, org_id, role)
invite(id, org_id, email, role, token_hash, expires_at)

channel(id, org_id, type[web|telegram|messenger|instagram|whatsapp|email],
        name, external_account_id, credentials_encrypted, webhook_secret,
        ai_enabled, status, created_at)

contact(id, org_id, name, phone_e164, email, avatar_url, attributes JSONB, created_at)
contact_identity(id, org_id, contact_id, channel_id, external_user_id UNIQUE(channel_id, external_user_id),
                 username, profile JSONB)

conversation(id, org_id, contact_id, channel_id, status[open|resolved|snoozed],
             assignee_type[none|user|ai], assignee_user_id, needs_human BOOL,
             last_customer_message_at, last_message_at,
             sales_state, state JSONB /* cart, details, quote_id */,
             summary, summary_updated_at)

message(id, org_id, conversation_id, direction[in|out], sender_type[contact|user|ai|system],
        sender_user_id, content_type[text|image|file|product_card|system_event],
        text, payload JSONB, external_id, UNIQUE(channel_id, external_id),
        delivery_status[queued|sent|delivered|read|failed], error, agent_run_id, created_at)
attachment(id, message_id, storage_key, mime, size, external_url)

note(id, org_id, conversation_id, author_type[user|ai], author_user_id, body, created_at)
quick_reply(id, org_id, shortcut, body)

ticket(id, org_id, number, contact_id, conversation_id, title, description,
       priority[low|medium|high|urgent], status[open|in_progress|closed],
       assignee_user_id, due_at, created_by_type, created_at, updated_at)
ticket_comment(id, ticket_id, author_type, author_user_id, body, visibility[internal|customer])

-- store module (same schema, same RLS)
product(id, org_id, name, description, category, status, attributes JSONB)
variant(id, product_id, sku, title, options JSONB /*size,color*/, price, image_key)
inventory(variant_id, on_hand, reserved)
product_embedding(product_id, chunk, embedding vector)

delivery_zone(id, org_id, name, fee, match_rules JSONB /* areas, keywords */)
quote(id, org_id, conversation_id, items JSONB, address JSONB, zone_id,
      subtotal, delivery_fee, total, payment_method, expires_at, consumed_order_id)

order(id, org_id, number /*per-tenant*/, contact_id, conversation_id, channel_id,
      created_by_type, fulfillment_status, payment_status, payment_method,
      delivery_zone_name, shipping_address JSONB, subtotal, delivery_fee, total,
      quote_id UNIQUE, tracking_token_hash, created_at)
order_item(order_id, variant_id, name_snapshot, unit_price_snapshot, qty)
order_event(order_id, type, from_status, to_status, actor_type, actor_id, data JSONB, at)
payment(id, order_id, provider[cod|khalti|esewa|qr_manual], amount, status,
        provider_ref, verified_by_user_id, created_at)
org_counter(org_id, kind[order|ticket], value)   -- row-locked per-tenant numbering

knowledge_doc(id, org_id, kind[business|offering|faq|policy|playbook], title, body, updated_at)
knowledge_chunk(id, doc_id, org_id, text, embedding vector)
ai_settings(org_id, enabled, language_mode[auto|en|ne], tone, handoff_rules JSONB,
            model, max_turn_cost)

agent_run(id, org_id, conversation_id, trigger_message_id, status[ok|suppressed|handoff|error],
          model, input_tokens, output_tokens, cost_credits, latency_ms, trace_id, created_at)
tool_call(id, agent_run_id, name, input JSONB, output JSONB, status, error, latency_ms)
check_result(id, agent_run_id, kind[rule|llm], passed, issues JSONB)
conversation_insight(id, conversation_id, message_id, intent, urgency, lead_stage,
                     signals JSONB, score, created_at)

crm_link(contact_id, provider, external_id, sync_status, last_synced_at, error)
credit_ledger(id, org_id, delta, reason[topup|agent_run|analyzer|adjustment],
              ref_id, balance_after, created_at)
plan / subscription(org_id, plan, seats, channels_limit, period_end)

outbox(id, org_id, topic, payload JSONB, created_at, published_at)
webhook_event(id, channel_id, raw JSONB, signature_ok, received_at, processed_at, error)
audit_log(id, org_id, actor_type, actor_id, action, target, data JSONB, at)
```

---

## 6. Channels

Each channel is an adapter implementing:

```python
class ChannelAdapter(Protocol):
    def verify(request) -> bool                       # signature / secret check
    def parse(raw) -> list[InboundEvent]              # message | echo | delivery | read | postback
    async def send(conv, OutboundMessage) -> SendResult   # returns external message id
    def capabilities() -> Capabilities               # cards, buttons, typing, window rules
    def render(RichMessage) -> channel payload       # product cards, buttons, quick replies
```

| Channel | Inbound | Send | Rich content | Rules / gotchas | Free dev setup |
|---|---|---|---|---|---|
| **Web widget** | WebSocket from widget | WebSocket push | Own components | Visitor token in localStorage; reconnect + resync by last message id | Built in |
| **Telegram** | `setWebhook` with `secret_token` → header `X-Telegram-Bot-Api-Secret-Token` | `sendMessage`, `sendPhoto`, `sendMediaGroup` | Inline keyboard: `url` / `callback_data` (≤64 bytes) | Answer callback queries; `sendChatAction` for typing | @BotFather |
| **Messenger** | Meta webhook: GET verify (`hub.challenge`), POST signed `X-Hub-Signature-256` (HMAC-SHA256, app secret) | Graph API `/{page-id}/messages` with page token | Generic template carousel (≤10 cards, ≤3 buttons: `web_url` / `postback`), quick replies | 24h reply window; `HUMAN_AGENT` tag allows human replies up to 7 days; `is_echo` events for page-sent messages | Meta app in development mode + own Page |
| **Instagram** | Same Meta webhook | Graph API messages endpoint | Generic template, quick replies | Same 24h / HUMAN_AGENT rules; echoes; professional account required | Same app + own professional account |
| **WhatsApp** | Cloud API webhook: `messages`, `statuses` | `/{phone-number-id}/messages` | Interactive: reply buttons (≤3), list, CTA URL; media | 24h customer-service window; outside it only approved templates | Free test number, ≤5 verified recipients |
| **Email** | IMAP poll / Gmail push; dev: Mailpit | SMTP / Gmail API | HTML | Thread by `Message-ID`, `In-Reply-To`, `References`; strip quoted replies & signatures | Mailpit in Docker |

**RahulCoolGram (our own test channel).** Until real channels are connected, customers use RahulCoolGram (`apps/rahulcoolgram`): a simple Instagram clone (customer chat UI + a small REST API). It sends each customer message to our webhook with a shared key, and our API replies through its REST endpoint. It is a normal `ChannelAdapter`, so a real channel later is a new adapter, not a redesign. See `ROADMAP.md`.

**Webhook ingress rule:** verify → store raw in `webhook_event` → enqueue → return `200` within milliseconds. Never call the LLM inside the webhook request.

**Echo handling:** after `send()`, store the returned external id on the message immediately; when an echo arrives with that id, ignore it. Echoes with unknown ids = message sent from the native app by staff → store as `sender_type=user` (outside tool).

**Reply window:** `can_send_freeform = now - last_customer_message_at < window`. Outside: use tag / template, or block with a UI explanation.

---

## 7. Inbound pipeline

```
webhook_event
  → normalize to InboundEvent
  → dedupe: UNIQUE(channel_id, external_id) — ON CONFLICT DO NOTHING
  → resolve contact_identity → contact (create if new; fetch profile name/avatar)
  → find open conversation for (contact, channel) or create one
  → insert message, download attachments to MinIO
  → update last_customer_message_at, unread counters
  → outbox: message.created
  → if conversation.assignee_type == ai and channel.ai_enabled and org AI enabled and credits > 0:
        schedule agent turn (debounced)
  → schedule analyzer
```

Postbacks (e.g. `BUY:variant_123`) are handled **deterministically** by code — they add to cart / start checkout state without LLM interpretation, then the agent continues the conversation.

---

## 8. Outbound pipeline

```
OutboundMessage (from user, AI, or system)
  → check ownership (sender must be assignee)
  → check reply window / template requirement
  → insert message (delivery_status = queued)
  → send job: adapter.render() → adapter.send()
       retry with exponential backoff on 5xx / rate limit; no retry on 4xx validation
       after N failures → failed + dead-letter + UI error badge
  → store external_id, status = sent
  → delivery / read webhooks → update status (✓ / ✓✓)
  → outbox: message.updated
```

Typing indicators (`typing_on`, `sendChatAction`) are sent while the agent is running.

---

## 9. Realtime

- Rooms: `org:{id}` (inbox list), `conversation:{id}` (thread + sidebar), `user:{id}` (notifications).
- **Transactional outbox:** the event row (or a Procrastinate job) is written in the same DB transaction as the change; a relay publishes it to Redis pub/sub; WebSocket servers forward to subscribed clients.
- Clients reconcile on reconnect by fetching changes since their last seen cursor.
- Event types: `message.created/updated`, `conversation.assigned/updated`, `note.created`, `ticket.*`, `order.*`, `contact.updated`, `insight.updated`, `agent.typing`.

---

## 10. Conversation ownership & handoff

- `assignee_type`: `none` → `user` | `ai`. Only the assignee can send. Others see read-only with **Assign yourself / Assign member**.
- Assignment changes write a `system_event` message into the timeline ("assigned to AI by …").
- Inbox filters: Mine, Unassigned, Needs human (handoff), AI, by channel, by status.
- **Handoff triggers** (any one):
  - agent calls `handoff_to_human(reason)`
  - rule match: refund/return, complaint, payment dispute, abusive language, explicit "talk to human"
  - checker failure after retry
  - repeated misunderstanding (N consecutive low-confidence turns)
  - credits exhausted
- On handoff: `assignee_type = none`, `needs_human = true`, AI stops, internal note with reason + summary, notify team.

---

## 11. AI system

Two roles, separate prompts, separate models.

### 11.1 Responder agent (talks and acts)

**Turn scheduling**
- **Debounce:** on each inbound message set `turn_due_at = now + 3s`; the job runs only if no newer message arrived (customers send split messages).
- **Lock:** one agent run per conversation at a time (Procrastinate queueing lock keyed by conversation id, backed by a Postgres advisory lock inside the run). New messages during a run trigger one follow-up turn.

**Context assembly**
1. System prompt: role, rules, tone, language mode, business profile, playbooks.
2. Sales state: current `sales_state`, cart, collected details, active quote.
3. Customer profile: name, phone known?, past orders, open tickets.
4. Conversation: last ~20 messages verbatim + rolling summary of older ones.
5. Retrieved knowledge: top-k chunks (FAQ, policies, offerings) via pgvector + keyword hybrid search.
6. Allowed tools for the current state.

**Agent loop**
```
loop (max 6 steps, max cost):
    response = llm.generate(context, tools=allowed_tools(state))
    if tool calls: validate input (Pydantic) → inject identity → execute service → append result
    else: draft reply → break
draft → checker → send | retry once with checker feedback | suppress + note + handoff
record agent_run, tool_calls, check_results, credits
```

**Tool catalog**

| Tool | Purpose | Guard |
|---|---|---|
| `search_knowledge(query)` | FAQ / policy lookup | read-only |
| `search_products(query, filters)` | Find products/variants | read-only |
| `get_product(product_id)` | Details, variants, stock | read-only |
| `share_products(variant_ids, message)` | Send product cards | ≤10 items, ids must exist |
| `set_cart(items)` | Replace cart | variants exist, in stock |
| `set_customer_details(name, phone, address)` | Save contact + shipping | phone format validation, no silent overwrite |
| `quote_order(payment_method?)` | Zone, fee, totals → `quote_id` | needs cart + address |
| `set_payment_method(method)` | COD / online | allowed methods only |
| `create_order(quote_id)` | Place order | state = `awaiting_confirmation`, quote valid, explicit customer yes after the confirmation question; idempotent on `quote_id` |
| `send_payment_link(order_id)` | Khalti / eSewa link | order unpaid |
| `lookup_order(order_number?)` | Status + tracking | only this contact's orders |
| `create_ticket(title, description, priority)` | Support issue | — |
| `update_lead_stage(stage)` | Pipeline | enum |
| `handoff_to_human(reason)` | Escalate | ends AI ownership |

**Sales state machine**
```
browsing ─▶ product_chosen ─▶ collecting_details ─▶ choosing_payment ─▶ awaiting_confirmation ─▶ order_placed
    ▲              │                   │                                       │
    └──────────────┴───── customer changes mind (cart edited → quote invalidated) ◀──┘
```
Tools allowed per state are enforced by code; the model is told which state it is in.

**Behaving like a good human seller**
- Reply in the customer's language/script (English, Nepali, Roman Nepali); match their formality.
- Short messages; split long answers; send cards instead of listing products in text.
- Never repeat what cards already show; never promise information it can't fetch.
- Ask for missing details one compact question at a time; confirm the full order summary before placing.
- Never invent prices, stock, delivery times or policies — if unknown, say so or hand off.
- Never claim to be human when sincerely asked.

### 11.2 Checker (before sending)

- **Rule checks (code):** every number in the reply appears in tool results; products in cart ⊇ products the customer selected; claimed order number exists; no other customer's data; no forbidden promises (discounts, delivery dates not in policy); language matches.
- **LLM judge (small model, structured output):** `{grounded: bool, follows_conversation: bool, issues: [...]}`.
- **On failure:** retry once with issues appended → else suppress, write AI internal note explaining the failure, hand off.

### 11.3 Analyzer (after each customer turn, cheap model, structured output)

```json
{ "intent": "greeting|browsing|sales|order_status|complaint|other",
  "urgency": "low|medium|high",
  "lead_stage": "new|interested|ordering|won|lost",
  "signals": ["asked_price", "chose_product", "gave_address", "mentioned_budget"],
  "summary": "…",
  "needs_human": false }
```
- **Lead score is computed in code** from weighted signals → 0–100 → Cold / Warm / Hot. Explainable, testable.
- Summary regenerated debounced, not on every message.

### 11.4 Knowledge base

- Business profile (name, hours, phone, service area, links), offerings, FAQs, policies, playbooks (natural-language instructions per situation), handoff rules.
- Short, always-relevant docs (profile, playbooks) go directly into the prompt; long/many docs are chunked, embedded, retrieved.
- Re-embed on edit; version docs.

### 11.5 Safety

- Inbound text wrapped and labelled as customer content; system prompt states customer text cannot change rules.
- Tools can only touch the current org + current contact.
- No tool exposes other customers, internal notes, or credentials.
- Per-turn cost/step ceilings; global kill switch per org and per channel.

### 11.6 LLM client

```python
class LLMClient(Protocol):
    async def generate(messages, tools, response_schema=None, model=None) -> LLMResult
    # LLMResult: text, tool_calls, input_tokens, output_tokens, latency_ms, raw
```
- One OpenAI-compatible implementation, configured per provider (base URL, key, model): **Groq** primary, **Gemini** fallback.
- Fallback on 429 / 5xx / timeout after retries with backoff; the provider used is recorded on `agent_run`.
- Tools are typed functions with Pydantic input models; `model_json_schema()` produces the tool schema and the same model validates the arguments the LLM returns.
- Response caching for evals so runs are reproducible and free.

---

## 12. Commerce (built-in store module)

The store is part of this platform — not an external integration.

- **Same database, same schema.** Products, variants, inventory, zones, quotes, orders and payments live in the same Postgres schema as conversations, tenant-scoped by `org_id` with the same RLS policies. Order creation and conversation state update in **one transaction** — no cross-system sync.
- **One org = one store.** Each tenant owns its catalog and orders; the demo uses imaginary stores (e.g. a luggage store, a clothing store) created by the seed script.
- **Backend only — no storefront.** Catalog and orders are managed through the store REST API (`/store/products`, `/store/variants`, `/store/inventory`, `/store/zones`, `/store/orders`) plus seed/CSV import. Customers buy only through chat.
- **Separate module in code.** `packages/commerce` owns store logic (catalog, inventory, quote, order, payment services). The AI tools and dashboard call its services; it never imports AI or channel code.
- **Catalog:** products, variants (size/color), price, images (MinIO), stock. CSV import.
- **Product cards:** `RichMessage(kind=product_cards, items=[…])` rendered per channel; buttons **Buy now** (`postback BUY:{variant_id}`) and **Details** (`postback INFO:{product_id}` → agent describes the product). No `web_url` buttons since there is no storefront.
- **Delivery zones:** area → zone → fee (e.g. inside ring road free, outside valley Rs X). Unknown area → ask customer.
- **Quote:** immutable snapshot of items, address, zone, fees, totals, expiry. Any cart/address change invalidates it.
- **Order creation (transaction):** lock variants → check stock and price vs quote → decrement/reserve stock → next per-tenant number from `org_counter` (row lock) → insert order + items (snapshots) → mark quote consumed → outbox `order.created`.
- **Statuses (independent):**
  - `fulfillment_status`: pending → confirmed → packed → dispatched → out_for_delivery → delivered | returned | cancelled
  - `payment_status`: unpaid → paid → refunded
- **Payments:** COD (paid on courier remittance); Khalti / eSewa sandbox (verify server-side via provider lookup API, never trust redirect params); QR manual (customer sends screenshot → staff verifies → mark paid; AI may only pre-read the screenshot).
- **Tracking:** public endpoint `GET /track/{token}` served by the API (minimal server-rendered page, no frontend app) — random token (`secrets.token_urlsafe(16)`), only hash stored, masked phone/address, status timeline from `order_event`. Customers can also ask the agent (`lookup_order`).
- **Courier:** mock courier service with booking API + status webhooks to exercise the full lifecycle.

---

## 13. Tickets, notes, quick replies

- Tickets: create from conversation (human or AI), number per tenant, priority, assignee, due date, statuses open → in_progress → closed, internal comments, customer-visible updates sent through the channel, email notification to assignee.
- Notes: internal only, never sent; AI writes notes for suppressed replies and handoffs.
- Quick replies: `/shortcut` expansion in composer; no AI cost.

---

## 14. CRM

- Built-in: contacts, lead stage pipeline, score, tags, orders, tickets, timeline across channels.
- **Contact merge:** same phone/email across channels → suggest merge; manual confirm; moves identities, conversations, orders.
- External CRM sync (optional adapter): event-driven job on `contact.updated` / `lead_stage.changed`, retries, `crm_link` status shown in sidebar.

---

## 15. Dashboard screens

1. Inbox list — channel icons, filters, unread, assignee, lead stage badge.
2. Conversation — timeline (messages, cards, system events), summary banner, intent/urgency tags, composer (quick replies, product picker, attachments), ownership footer.
3. Sidebar — profile + score, contact info, notes, tickets, CRM, orders (each a live widget).
4. Tickets board · Orders list/detail (status updates, mark paid) · Contacts. Catalog is managed via the store API, not the dashboard.
5. AI settings — master toggle, per-channel toggles, business knowledge, offerings, FAQs, playbooks, language, tone, handoff rules, playground to test the agent.
6. Channels — connect/disconnect, health, webhook status.
7. Analytics · Billing & credits · Team & roles.
8. AI run inspector — per message: prompt context, tool calls, checker verdict, tokens, cost, latency.

---

## 16. Analytics

- Operational: messages in/out, conversations by channel, unread, first-response time, resolution time, tickets by status/priority.
- AI: % conversations fully handled by AI, handoff rate and reasons, suppressed replies, tool error rate, cost per conversation, cost per order.
- Sales: orders and revenue by channel, by AI vs human, conversion funnel (interested → ordering → won), AOV.

---

## 17. Credits & billing

- Append-only `credit_ledger`; balance = last `balance_after` (row lock on write).
- Debit per agent run from actual token usage × model rate (analyzer billed separately).
- Pre-check balance before a run; at zero → AI pauses, conversations route to humans.
- Plans limit seats and channels; enforced in services.

---

## 18. Security

- Channel tokens encrypted at rest (envelope encryption; key from env/KMS).
- Webhook signature verification on every channel; reject + log on failure.
- RLS tenancy + service-level `org_id` checks (defense in depth).
- Rate limits per IP, per org, per channel (Redis token bucket).
- PII: masked phone numbers for restricted roles, audit log on reveal, retention policy + hard delete job.
- Public endpoints (widget, tracking) use unguessable tokens; no sequential IDs exposed.
- Secrets never in prompts or logs; log redaction.

---

## 19. Reliability

- Idempotency everywhere: `UNIQUE(channel_id, external_id)`, `quote_id`, job dedupe keys, `Idempotency-Key` header on mutating REST calls.
- Transactional outbox for events; at-least-once delivery + idempotent consumers.
- Job retries with exponential backoff + jitter; dead-letter queue with admin replay.
- Timeouts on every external call; circuit breaker for LLM and channel APIs.
- Graceful degradation: LLM down → handoff to humans; channel down → queued sends.

---

## 20. Observability & evals

- **Tracing:** one trace per inbound message: webhook → queue → agent run (each LLM call + tool call as spans) → checker → send.
- **Metrics:** queue depth, job latency, webhook failures, send failures, agent latency p50/p95, tokens and cost.
- **LLM traces:** Langfuse — prompts, outputs, tool calls, scores.
- **Evals (run in CI on prompt/model changes):**
  - Dataset of scripted conversations: happy-path purchase, change of mind, missing details, out of stock, unknown area, order status lookup, complaint → ticket, refund → handoff, Roman Nepali, mixed language, prompt injection, other-customer data request, abusive user.
  - Deterministic assertions: correct tools, correct args, `create_order` exactly once, no ungrounded numbers, handoff when required.
  - LLM-judge rubrics: helpfulness, tone, language match, brevity.
  - Metrics: task success rate, tool-call accuracy, hallucinated-number rate, handoff precision/recall, cost and latency per conversation.

---

## 21. Testing

- Unit: state machines, quote/zone math, score computation, adapters' `parse`/`render`.
- Integration: services against real Postgres (testcontainers), RLS isolation tests (org A can never read org B).
- Contract: recorded webhook payloads per channel replayed through ingress.
- E2E: Playwright — widget message → AI reply → order appears in sidebar.
- Load: k6 — 1,000 webhooks/min sustained; measure end-to-end reply latency and queue depth.
- Chaos: kill workers mid-run, duplicate webhooks, LLM 429 storms → verify no duplicate orders or lost messages.

---

## 22. Local environment (free)

```
docker compose up:
  postgres(+pgvector) · redis · minio · mailpit · langfuse · grafana stack
  api (FastAPI) · worker (Procrastinate) · ws (WebSocket server) · web (Next.js) · widget dev server
cloudflared tunnel → api (for Telegram / Meta webhooks)
```
Seed script: demo org, team users, catalog (luggage store), delivery zones, FAQs, playbooks, sample conversations.

---

## 23. Repository layout

```
/apps
  /api            FastAPI app: routes, webhooks, websockets
  /worker         Procrastinate tasks: ingest, agent, analyzer, outbound, sync
  /web            Next.js dashboard
  /widget         embeddable chat widget
/packages (python)
  /domain         entities, enums, state machines, rules
  /app            services, events, outbox
  /commerce       store module: catalog, inventory, zones, quotes, orders, payments
  /adapters       channels/, llm/, payments/, courier/, crm/, storage/
  /ai             prompts/, tools/, agent loop, checker, analyzer, retrieval
  /db             models, migrations (Alembic), RLS policies
/evals            datasets, runners, rubrics
/infra            docker-compose, grafana dashboards, k6 scripts
/docs             this blueprint, ADRs
```

---

## 24. Build phases

| # | Phase | Delivers | Done when |
|---|---|---|---|
| 1 | Foundation | Compose stack, auth, orgs, roles, RLS, inbox UI, web widget, realtime | Widget message appears live in the dashboard; staff reply reaches widget |
| 2 | Channels | Telegram, Messenger, Instagram adapters; ingress, dedupe, echoes, delivery status, contacts & identities | Same customer flow works on 3 external channels; duplicate webhooks create nothing |
| 3 | Team ops | Assignment, ownership lock, system events, notes, quick replies, tickets | Two staff can't reply over each other; ticket lifecycle with notifications |
| 4 | AI agent v1 | LLM client, knowledge base + retrieval, responder, analyzer, handoff, run inspector, credits | AI answers FAQs, hands off correctly, every run is inspectable and billed |
| 5 | Commerce | Store module + store API, seeded imaginary stores, product cards, postbacks, cart, zones, quotes, state machine, orders, tracking endpoint, checker | End-to-end chat purchase; double "yes" yields one order; checker blocks bad replies |
| 6 | Quality | Eval suite in CI, Langfuse, OpenTelemetry, dashboards, analytics | Eval scores tracked per commit; one trace per message end to end |
| 7 | Expansion | WhatsApp, email, Khalti/eSewa sandbox, mock courier, contact merge | All six channels + online payment + courier lifecycle |
| 8 | Hardening | Rate limits, encryption, retention, load + chaos tests, deploy | k6 targets met; chaos tests pass with no duplicates or loss |
