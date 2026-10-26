# Roadmap

> `BLUEPRINT.md` is **where we are going**. This file is **how we get there, one step at a time**.
> `PRODUCTION_GRADE.md` explains **what "industry-grade" means** and which step adds each part.
> `INTERVIEW_PREP.md` explains **how this project gets you hired**, and how we practise.

---

## 1. How to read this file

The project is split into **stages** (A, B, C …). Each stage is split into **steps**. A step is small: one to a few sessions of work. Every step has the same shape:

| Part | Meaning |
|---|---|
| **Goal** | The one thing this step makes possible. |
| **Why now** | The problem you feel *today* that this step solves. We never add a tool before we feel the need for it. |
| **Build** | What you will actually create. |
| **Learn** | The new concepts. Numbers like (§4) point to sections of `learn.md`. |
| **Production bar** | The extra 10% that separates industry work from a hobby project. Not optional. |
| **Done when** | A check anyone can run to prove the step works. |
| **Interview** | Questions you can answer well after this step. We practise them right after the step. |

### Definition of Done (applies to every step)

A step is finished only when **all** of these are true:

1. The **Done when** check passes on your machine.
2. Tests for the new behaviour exist and **CI is green**.
3. Work went through a **branch → pull request → merge**, with a clear PR description (even though you work alone; this is how teams work).
4. If you made a real decision (chose X over Y), there is an **ADR** in `docs/adr/`.
5. `docs/JOURNAL.md` has 3–5 lines: what you built, what broke, what you learned. These become interview stories.
6. The step is ticked in **Progress** at the bottom of this file.
7. **Mock interview** for that step is done (see `INTERVIEW_PREP.md`).

---

## 2. The big picture

### Where we end up

```
  RahulCoolGram (fake Instagram)                  Dashboard (Next.js)
  customer phone UI + small REST API              inbox · conversation · AI inspector
        │  webhook         ▲ reply API                  ▲ REST        ▲ WebSocket
        ▼                  │                             │             │
  ┌───────────────────────────────────────────────────────────────────────┐
  │ API (FastAPI): webhook ingress · REST · WebSocket                      │
  └───────┬───────────────────────────────────────────────────────────────┘
          │ save + enqueue in one transaction
          ▼
  ┌──────────────────┐     ┌──────────────────────────────────────────────┐
  │ Postgres         │◀───▶│ Worker (Procrastinate)                        │
  │ data · jobs ·    │     │ agent runs · analyzer · outbound sends        │
  │ vectors          │     └─────┬───────────────────────┬────────────────┘
  └──────────────────┘           │ LLM calls             │ events
                                 ▼                       ▼
                          Groq / Gemini           Redis pub/sub → WebSocket
  Everything sends telemetry → OpenTelemetry → Grafana stack (system) + Langfuse (AI)
```

### Where we start (Stage A)

```
  RahulCoolGram ──webhook──▶ API ──▶ Postgres ◀── API ◀──REST── Dashboard
     ▲                  │
     └───reply API──────┘
```

No AI, no queue, no Redis, no login. Just a real inbox with a fake customer. Every later stage adds **one** layer.

### The order of stages, and why

| Stage | Theme | Why this order |
|---|---|---|
| 0 | Engineering foundations | Habits are cheapest to set on day one. |
| A | An inbox with a simulated customer | The agent needs a world to live in: messages, conversations, a customer, a staff screen. |
| B | **The AI agent (the core)** | Your main learning goal. Comes before login and multi-store because it's the most valuable part. |
| C | An agent that sells | Turns a chatbot into an agent that *acts*: cart, quote, order. This is where "the LLM chooses, code decides" becomes real. |
| D | Team, tenancy, account linking | Makes it a real SaaS: logins, many stores, connect-your-account flow. |
| E | Production quality | Prove it works under load and failure, measure it, alert on it. |
| F | Real channels (optional) | Telegram / Instagram as new adapters. |

---

## 3. RahulCoolGram — our Instagram clone

Real Instagram needs a Meta app, app review, a business account and a public URL. That's a lot of setup and teaches little. Instead we built **RahulCoolGram** (`apps/simulator`): a small Instagram-DM clone where you play the customer.

It is deliberately **simple**: a plain FastAPI app with a few REST endpoints, SQLite, and a phone-style chat page that polls for new messages. It does **not** copy Meta's API.

### How it links to our API

```
 Customer types in RahulCoolGram
   → RahulCoolGram saves it, then POST {OMNICHANNEL_WEBHOOK_URL}         (our API receives it)
        body: {"message_id", "customer": {"id","name","username"}, "text", "sent_at"}
        header: X-RahulCoolGram-Key: <shared key>

 Staff or AI replies in our system
   → our API calls POST http://localhost:8100/api/store/messages        (RahulCoolGram shows it)
        body: {"customer_id", "text"}   header: X-RahulCoolGram-Key: <shared key>
        returns: {"message_id"}
```

Both sides use the same shared key. Full endpoint list: `apps/simulator/README.md`.

On our side, RahulCoolGram is one implementation of a `ChannelAdapter`. A real channel (Instagram, Telegram) later is another implementation; real platforms add things like signed webhooks and retries, which we learn about then.

Features are added to RahulCoolGram only when a step needs them (e.g. product cards with buttons in step 26).

---

## 4. Stage 0 — Engineering foundations

### Step 0 · Set up the workshop

- **Goal:** the repo works like a real team's repo from day one.
- **Why now:** habits added later never stick, and reviewers look at these first.
- **Build:**
  - `README.md`: one paragraph on what the project is, how to run it, link to docs. (It grows every stage.)
  - `docs/adr/0000-template.md` (Michael Nygard format: *Title, Status, Context, Decision, Consequences*), plus the first two ADRs:
    - `0001-stack.md`: FastAPI + Postgres + Procrastinate + own agent loop (copy reasons from the blueprint decision log).
    - `0002-rahulcoolgram.md`: why a simulator instead of real Instagram.
  - `docs/JOURNAL.md`: your learning log.
  - GitHub: a **Project board** with one issue per step; branch protection on `main` (PR required, CI must pass).
  - Commit style: [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- **Learn:** ADRs, PR workflow, issue tracking.
- **Done when:** first PR (`docs: add ADRs and journal`) is merged through the GitHub UI.
- **Interview:** "How do you document architectural decisions?" · "How do you work on a codebase as a team?"

---

## 5. Stage A — An inbox with a simulated customer

### Step 1 · API skeleton

- **Goal:** a running Python web server.
- **Why now:** everything else hangs off it.
- **Build:** `apps/api` created with `uv` (Python 3.14); FastAPI app with `GET /health`; settings read from environment variables with `pydantic-settings` (`.env.example` committed, `.env` git-ignored); `ruff` for lint + format; one `pytest` test; a GitHub Actions workflow running lint + tests on every PR.
- **Learn:** HTTP request/response, what a web framework does, ASGI and uvicorn, environment variables (§1, §6, §10). The *twelve-factor* rule: config lives in the environment, not in code.
- **Production bar:** CI from the very first endpoint; no secret ever in git.
- **Done when:** `curl localhost:8000/health` → `{"status":"ok"}`; `/docs` shows the endpoint; CI is green on the PR.
- **Interview:** "What happens when you type a URL and press enter?" · "Why environment variables for config?" · "What does CI give you on a one-person project?"

### Step 2 · In-memory inbox

- **Goal:** design the API shape before touching a database.
- **Why now:** it's easier to think about URLs and data shapes without SQL in the way.
- **Build:** Pydantic models `Conversation`, `Message`; endpoints `GET /conversations`, `GET /conversations/{id}/messages`, `POST /conversations/{id}/messages`, stored in a Python dict. A consistent error format (`{"error": {"code", "message"}}`). Middleware that adds a **request id** to every request and log line; logs written as **JSON to stdout**.
- **Learn:** REST resources, HTTP methods, status codes (200/201/400/404/422), Pydantic validation, middleware. **Structured logging** — the first layer of observability.
- **Production bar:** every log line has a request id; every error has the same shape.
- **Done when:** you can create and list messages from `/docs`; a bad body gives a clean 422; restart → **the data is gone**. That pain is the reason for step 3.
- **Interview:** "PUT vs PATCH vs POST?" · "What's the difference between 400, 401, 403, 404, 422?" · "Why structured logs instead of print?"

### Step 3 · Postgres in Docker

- **Goal:** data survives restarts.
- **Why now:** step 2 loses everything.
- **Build:** `infra/docker-compose.yml` with Postgres 16 (named volume, healthcheck). Hand-written SQL for `organization`, `contact`, `conversation`, `message` — **with `org_id` on every table** even though there is only one org. Split health into `GET /health/live` (process is up) and `GET /health/ready` (database reachable).
- **Learn:** Docker, images vs containers, volumes, Compose (§10); tables, primary and foreign keys, `NOT NULL`, `UNIQUE` (§3). Liveness vs readiness.
- **Production bar:** readiness checks real dependencies; schema has constraints, not just columns.
- **Done when:** rows survive an API restart; `docker compose down && up` keeps data; `/health/ready` returns 503 when Postgres is stopped.
- **Interview:** "Why Postgres and not MongoDB here?" · "What is a foreign key for?" · "Liveness vs readiness probe?"

### Step 4 · ORM and migrations

- **Goal:** the schema is code, versioned and reproducible.
- **Why now:** hand-written SQL files can't be applied safely to an existing database.
- **Build:** SQLAlchemy 2 async models; Alembic with the first migration; a FastAPI dependency that gives each request a DB session; integration tests that run against a **real** Postgres (testcontainers or the Compose DB).
- **Learn:** ORM, migrations, async/await and the event loop (§2), dependency injection (§6), transactions (§3).
- **Production bar:** CI runs `alembic upgrade head` on an empty DB and fails if models and migrations drift; tests hit real Postgres, not SQLite.
- **Done when:** `alembic upgrade head` builds the schema from zero; `alembic downgrade -1` works; API uses the ORM.
- **Interview:** "Why async for an I/O-heavy API?" · "How do you change a column on a big table without downtime?" · "What is a transaction, and when would you need one here?"

### Step 5 · Seed data

- **Goal:** realistic data to look at.
- **Build:** a `seed` command: demo org *Himal Luggage Co.*, 5 contacts, conversations with messages (reuse the dashboard's `mock-data.ts` content).
- **Learn:** transactions (all-or-nothing seed), idempotent scripts (running twice doesn't duplicate).
- **Done when:** `uv run seed` on an empty DB fills it; running it again changes nothing.
- **Interview:** "What does idempotent mean? Give an example from your project."

### Step 6 · Dashboard reads the API

- **Goal:** the two halves meet.
- **Build:** generate TypeScript types from the API's OpenAPI schema (`openapi-typescript`); replace `mock-data.ts` with TanStack Query hooks; configure CORS.
- **Learn:** CORS and why browsers enforce it; OpenAPI as a contract; client-side caching (§6, §9).
- **Production bar:** frontend types are **generated**, never hand-copied, so a backend change breaks the frontend build instead of production.
- **Done when:** the dashboard shows rows from Postgres; changing a field name in the API makes `npm run build` fail.
- **Interview:** "What is CORS and what problem does it solve?" · "How do you keep frontend and backend types in sync?"

### Step 7 · Staff can reply

- **Build:** composer → `POST` message; TanStack Query mutation with cache invalidation; the API accepts an `Idempotency-Key` header so a double-click creates one message.
- **Learn:** mutations, optimistic UI, idempotency keys (the Stripe pattern).
- **Done when:** a reply is saved and shown; sending the same request twice with the same key creates one row.
- **Interview:** "How does Stripe stop a double charge when a client retries?"

### Step 8 · Link RahulCoolGram to the API

- **Goal:** a customer who talks to the store.
- **Build:** RahulCoolGram already exists (`apps/simulator`). Add `POST /webhooks/rahulcoolgram` to our API: it receives RahulCoolGram's JSON, finds-or-creates the contact and conversation, and stores the message.
- **Learn:** webhooks (§1): who calls whom; two services with separate databases.
- **Done when:** a RahulCoolGram message appears in the dashboard after a refresh.
- **Interview:** "What's a webhook, and how is it different from polling an API?"

### Step 9 · Webhooks done right

- **Goal:** the webhook can't be faked and can't create duplicates.
- **Why now:** step 8 trusts anyone, and the same message sent twice is saved twice.
- **Build:** reject requests without the right `X-RahulCoolGram-Key` (401); store every request raw in `webhook_event`; dedupe with `UNIQUE(channel_id, external_id)` + `ON CONFLICT DO NOTHING` using RahulCoolGram's `message_id`. Test a duplicate by sending the same request twice with curl.
- **Learn:** shared-secret auth vs HMAC signatures (what real platforms use, and why), idempotent consumers, at-least-once delivery (§4, §7).
- **Production bar:** keep the raw payload for debugging and replay; a duplicate is a no-op, not an error.
- **Done when:** wrong key → 401; the same webhook twice → one message.
- **Interview:** "How do you verify a webhook came from the real sender?" · "Exactly-once vs at-least-once delivery?" · "Why store the raw payload?"

### Step 10 · Outbound messages

- **Goal:** staff replies reach the customer.
- **Build:** a `ChannelAdapter` interface with a RahulCoolGram implementation; staff reply → adapter calls RahulCoolGram's `POST /api/store/messages` (`httpx`, explicit timeout) → store the returned `message_id`; message `delivery_status` (`queued → sent → failed`).
- **Learn:** HTTP clients, timeouts, error classes (retry 5xx/429, don't retry 4xx), adapters/ports (§6).
- **Production bar:** every outbound call has a timeout; failures are visible in the UI, never silent.
- **Done when:** a full conversation works both ways; stopping RahulCoolGram shows a "failed" badge instead of an error page.
- **Interview:** "Which errors should you retry and which not?" · "Why put channels behind an interface?"

### Step 11 · Live updates

- **Goal:** no more refreshing.
- **Build:** first, polling (`refetchInterval`); then a FastAPI WebSocket with rooms (`org:{id}`, `conversation:{id}`); on reconnect the client refetches since its last seen message.
- **Learn:** polling vs SSE vs WebSocket, rooms, reconnect and resync (§5).
- **Done when:** a RahulCoolGram message appears in the dashboard instantly, and vice versa; killing and restarting the API loses nothing on screen.
- **Interview:** "Design a chat system: how do messages get pushed to clients?" · "What happens when a client reconnects?"

**Milestone A** — record a 1-minute screen capture: customer writes in RahulCoolGram → staff sees it live → replies → customer sees it. Update the README.

---

## 6. Stage B — The AI agent

This stage follows two rules from Anthropic's *Building effective agents*: **start with the simplest thing that works**, and **add complexity only when you can show it helps**. That's why we begin with one LLM call and earn our way to a full agent.

### Step 12 · LLM client

- **Build:** an `LLMClient` with one OpenAI-compatible implementation, configured for **Groq** (primary) and **Gemini** (fallback, via Gemini's OpenAI-compatible endpoint). Retries with backoff and jitter on 429/5xx/timeout, then fallback. Return text, tool calls, input/output tokens, latency, provider. A tiny CLI to chat with it.
- **Learn:** prompts, tokens, context windows, rate limits, provider fallback (§8). Free-tier limits are per **organisation**, not per key.
- **Production bar:** every call records tokens, latency and provider; secrets come from env.
- **Done when:** the CLI answers; forcing a Groq failure shows the Gemini fallback in the logs.
- **Interview:** "How do you handle LLM provider rate limits and outages?"

### Step 13 · Auto-reply, the naive way

- **Build:** when a conversation is assigned to AI, call the LLM **inside the webhook request** and send the reply.
- **Why:** to *see* why the blueprint forbids this. The LLM takes seconds, so RahulCoolGram's webhook call waits and times out. Real platforms retry on timeout; replay the same webhook with curl to see the customer get **duplicate replies**.
- **Done when:** you can reproduce the duplicate and explain it. Write it in the journal — it's an interview story.
- **Interview:** "Why must webhook handlers return fast?"

### Step 14 · Job queue

- **Build:** Procrastinate worker. The webhook now saves the message **and** enqueues `run_agent` **in one transaction**, then returns 200. The worker runs the agent and sends. Because the worker is a separate process, it publishes `message.created` to **Redis pub/sub**, and the API forwards it to WebSockets.
- **Learn:** queue vs pub/sub, workers, retries, transactional enqueue / outbox (§4).
- **Production bar:** a crash between "save" and "enqueue" is impossible (same transaction); jobs have retry limits.
- **Done when:** the webhook answers in milliseconds even when the LLM is slow; a replayed webhook causes no duplicate reply; killing the worker mid-run and restarting it still produces exactly one reply.
- **Interview:** "Why not FastAPI BackgroundTasks?" · "Queue vs pub/sub — when do you use each?" · "What is the transactional outbox pattern?"

### Step 15 · Human-like timing

- **Build:** debounce (wait ~3 s after the last customer message, so split messages get one answer); one agent run per conversation at a time (Procrastinate queueing lock + execution lock); a typing indicator in RahulCoolGram.
- **Learn:** debounce, locks, race conditions. Known pitfall: a worker that dies can leave a lock held, so add a periodic task that frees stalled jobs.
- **Done when:** sending "hi" / "do you have" / "black bags?" quickly gets **one** reply; the typing dots show.
- **Interview:** "How do you prevent two workers replying to the same conversation?"

### Step 16 · Telemetry, layer 2: traces across processes

- **Why now:** a message now passes through API → Postgres queue → worker → LLM → RahulCoolGram. When it's slow, logs alone can't tell you where.
- **Build:** OpenTelemetry in API and worker (FastAPI, SQLAlchemy and httpx auto-instrumentation); trace context passed through the job so **one trace covers webhook → job → LLM → send**; a single `grafana/otel-lgtm` container in Compose (Grafana + Prometheus + Tempo + Loki in one) for local dev.
- **Learn:** traces, spans, context propagation; the four golden signals (latency, traffic, errors, saturation) (§10).
- **Done when:** in Grafana you open one trace and see where the 4 seconds went.
- **Interview:** "A customer says replies are slow. How do you find out why?"

### Step 17 · Eval harness v0

- **Why now:** from the next step on you'll change prompts constantly. Without tests for AI behaviour you can't tell if a change helped or hurt. Industry treats evals as the main thing that separates serious AI work from demos.
- **Build:** `evals/` with 10 scripted conversations played through RahulCoolGram's API (greeting, FAQ, Nepali, Roman Nepali, "talk to a human", rude customer, prompt injection). Deterministic assertions (language, length, no invented prices). Results saved as a table you can compare between runs. LLM responses cached so re-runs are free and repeatable.
- **Learn:** golden datasets, assertions vs LLM-as-judge, regression testing for AI (§8).
- **Done when:** `uv run evals` prints a scorecard; a deliberately bad prompt makes the score drop.
- **Interview:** "How do you test an LLM application?" · "How do you know a prompt change didn't make things worse?"

### Step 18 · Knowledge in the prompt

- **Build:** business profile, FAQs, policies, tone and language rules stored in the DB and assembled into the system prompt; customer text wrapped and labelled as untrusted; prompt templates versioned.
- **Learn:** system prompt design, context assembly, prompt versioning.
- **Done when:** the agent answers store questions correctly in English, Nepali and Roman Nepali; eval score goes up.
- **Interview:** "How do you structure a system prompt for a production agent?"

### Step 19 · Tools and the agent loop

- **Build:** tools as typed Python functions with Pydantic input models (schema for the LLM *and* validation of its arguments); first tool `search_knowledge`; the loop (ask → run tools → feed results → repeat) with max steps and max cost; identity (`org_id`, `conversation_id`) injected by the server, never by the model.
- **Learn:** tool calling, the agent loop, tool design ("tool descriptions are prompts"; make wrong usage hard), workflow vs agent (§8).
- **Production bar:** invalid tool arguments are rejected and fed back to the model, not crashed on; loops always terminate.
- **Done when:** a question needing a lookup triggers `search_knowledge`, and the answer cites it; evals check *which* tools were called.
- **Interview:** "Walk me through your agent loop." · "How do you stop an agent looping forever?" · "Agent or workflow — how do you decide?"

### Step 20 · Telemetry, layer 3: AI observability

- **Why now:** you now have multi-step runs. You need to see *what the AI saw and decided*.
- **Build:**
  - `agent_run`, `tool_call` tables + an **AI run inspector** page in the dashboard (product feature: staff can see why the AI said something; also the source for billing later).
  - **Langfuse** for developer-side LLM tracing: prompts, outputs, tool calls, tokens, cost, eval scores. Start with **Langfuse Cloud (free Hobby tier)**; self-hosting needs Postgres + ClickHouse + Redis + S3, which is a later, optional exercise.
- **Learn:** LLM tracing, cost tracking, linking eval runs to traces.
- **Done when:** for any AI reply you can open its full run (context, tool calls, tokens, cost, latency) in the dashboard and in Langfuse.
- **Interview:** "How do you debug a wrong answer from an agent in production?"

### Step 21 · Handoff to humans

- **Build:** ownership (`assignee_type`: none / user / ai; only the owner can send); `handoff_to_human(reason)` tool; rule triggers (refund, complaint, "talk to a human", abuse, repeated failures); handoff writes an internal note + a timeline event and notifies staff.
- **Learn:** human-in-the-loop design, ownership locks.
- **Done when:** "I want a refund" hands off, the AI goes quiet, and the dashboard shows "Needs human"; evals cover it.
- **Interview:** "When should an AI agent give up and hand off?"

### Step 22 · Analyzer

- **Build:** after each customer turn, a cheap model returns structured JSON (intent, urgency, lead stage, signals, summary) validated by Pydantic; **lead score computed in code** from signals.
- **Learn:** structured output, model routing (cheap vs strong model), explainable scoring.
- **Done when:** inbox badges show intent/urgency/lead stage from real runs.
- **Interview:** "Why compute the score in code instead of asking the LLM for a number?"

### Step 23 · Safety

- **Build:** map defences to the **OWASP Top 10 for LLM Applications (2025)** — prompt injection (LLM01), sensitive data disclosure (LLM02), excessive agency (LLM06), system prompt leakage (LLM07), unbounded consumption (LLM10); add attack conversations to the eval set.
- **Learn:** direct vs indirect prompt injection, least privilege for tools, cost ceilings.
- **Done when:** the injection and data-leak evals pass.
- **Interview:** "How do you defend an agent against prompt injection?" · "What is excessive agency?"

### Step 24 · Ship it: first deploy

- **Build:** Dockerfiles for API, worker, web, RahulCoolGram; deploy to a cheap host with managed Postgres; secrets in the host's secret store; CD on merge to `main`; migrations run as a deploy step; a public demo link.
- **Learn:** container images, CD, zero-downtime migrations, rollback.
- **Done when:** anyone with the link can chat as a RahulCoolGram customer and watch the dashboard.
- **Interview:** "How do you deploy a database migration safely?" · "How would you roll back a bad release?"

**Milestone B** — a 2-minute demo video of the agent answering, using a tool, handing off, with the run inspector open. This is the core of your portfolio.

---

## 7. Stage C — An agent that sells

| # | Step | Build | Key lesson |
|---|---|---|---|
| 25 | Catalog | Products, variants, inventory, store API, seeded stores (luggage, clothing) | Separate module (`commerce`) that never imports AI code |
| 26 | Product cards + postbacks | Agent sends product cards; RahulCoolGram learns to show them; **Buy now** / **Details** taps come back as button events handled by code | Deterministic handling of structured input |
| 27 | Cart + sales state machine | `browsing → product_chosen → collecting_details → choosing_payment → awaiting_confirmation → order_placed`; tools allowed per state are enforced by code | "The LLM chooses, code decides" |
| 28 | Zones + quote | Delivery zones and fees; immutable quote snapshot; any change invalidates it | Never trust model arithmetic |
| 29 | Create order | One transaction: lock variants, check stock and price, next order number (row lock), insert, consume quote; idempotent on `quote_id` | Double "yes" = one order |
| 30 | Pre-send checker | Rule checks (every number appears in tool results) + small LLM judge; retry once, else suppress + hand off | Guardrails on output |
| 31 | Order status + tracking | `lookup_order` tool; public tracking page with unguessable token | Safe public endpoints |

**Done when (stage):** a full purchase through chat; saying "yes" twice creates one order; evals cover the happy path, change of mind, out of stock, unknown area.

---

## 8. Stage D — Team, tenancy, account linking

| # | Step | Build | Key lesson |
|---|---|---|---|
| 32 | Login | Users, argon2id hashing, httpOnly session cookies, CSRF protection | Authentication done right |
| 33 | Roles | owner / admin / agent checks in services | Authorization (RBAC) |
| 34 | Connect a channel | A store adds its RahulCoolGram connection (URL + key) in settings; the key is **encrypted at rest** | Storing third-party credentials safely |
| 35 | Second store + RLS | Postgres row-level security with `SET LOCAL` per transaction, `FORCE ROW LEVEL SECURITY`, `WITH CHECK`, app role without `BYPASSRLS`; a test that org A can never read org B, including across pooled connections | Multi-tenancy as a database guarantee |
| 36 | Team tools | Notes, quick replies, tickets with numbering per store | Real product features |

---

## 9. Stage E — Production quality

| # | Step | Build | Key lesson |
|---|---|---|---|
| 37 | SLOs and alerts | Define SLOs (e.g. 99% of AI replies sent within 15 s), dashboards for the golden signals + queue depth + LLM cost, alerts on SLO burn, a **runbook** per alert | Monitoring that pages for user pain, not CPU |
| 38 | Evals in CI | Eval suite runs on every PR that touches prompts/tools; LLM-judge rubrics; scores tracked over time | AI regressions caught before merge |
| 39 | RAG | Gemini embeddings + pgvector; hybrid (keyword + vector) search; retrieval metrics (recall@k) | When and why to add RAG |
| 40 | Load and chaos | k6 load test; replay duplicate webhooks; stop RahulCoolGram during sends; kill workers mid-run | Prove: no lost messages, no duplicate orders |
| 41 | Security hardening | Rate limits (Redis token bucket), audit log, PII masking, log redaction, dependency scanning | Defence in depth |
| 42 | Credits and billing | Append-only credit ledger, per-run debit, AI pauses at zero | Usage metering |
| 43 | Postmortem | Break something on purpose, fix it, write a blameless postmortem | The best interview story you'll have |

## 10. Stage F — Real channels (optional)

Telegram (easiest: free, no review) and/or Instagram as new `ChannelAdapter`s, plus a Cloudflare tunnel for a public webhook URL. Real platforms add signed webhooks, retries and OAuth account linking; those get added in the new adapter, the rest of the system stays the same.

---

## 11. Observability, layer by layer

Observability isn't one step. It grows with the system:

| Layer | Added in | Tool | Answers |
|---|---|---|---|
| Structured JSON logs + request id | Step 2 | Python logging | "What happened in this request?" |
| Health checks (live / ready) | Step 3 | FastAPI | "Is it up? Can it reach its dependencies?" |
| Traces across processes | Step 16 | OpenTelemetry → `grafana/otel-lgtm` (Tempo) | "Where did the time go?" |
| Metrics + dashboards | Step 16 | OpenTelemetry → Prometheus, Grafana | "How is the system doing overall?" |
| AI run records (product) | Step 20 | Postgres + dashboard inspector | "Why did the AI say that?" (for staff) |
| LLM tracing + eval scores | Step 20 | Langfuse | "Which prompt / model change made it better or worse?" (for developers) |
| Evals | Steps 17, 38 | Own harness (+ Langfuse datasets) | "Is the agent still good after this change?" |
| SLOs, alerts, runbooks | Step 37 | Grafana alerting | "Are users hurting right now, and what do I do?" |

See `PRODUCTION_GRADE.md` §5 for why these tools were chosen (and why LangSmith wasn't).

---

## 12. Deliberate differences from the blueprint

- **RahulCoolGram instead of real channels** until Stage F.
- **AI before login and multi-tenancy.** One hardcoded org until step 35, but `org_id` is on every table from step 3.
- **No queue or Redis until step 14**, after you've seen the naive way break.
- **Polling before WebSocket.**
- **Langfuse Cloud before self-hosting** (self-hosting needs ClickHouse + Redis + S3).
- **Flat `apps/api` package first**, split into `packages/…` once it's big enough for the split to be obvious.

---

## Progress

**Stage 0**
- [x] 0 Workshop set up (ADRs, journal, PR flow; project board skipped for now)

**Stage A**
- [ ] 1 API skeleton
- [ ] 2 In-memory inbox
- [ ] 3 Postgres in Docker
- [ ] 4 ORM and migrations
- [ ] 5 Seed data
- [ ] 6 Dashboard reads the API
- [ ] 7 Staff can reply
- [ ] 8 Link RahulCoolGram to the API
- [ ] 9 Webhooks done right
- [ ] 10 Outbound messages
- [ ] 11 Live updates
- [ ] Milestone A video

**Stage B**
- [ ] 12 LLM client
- [ ] 13 Naive auto-reply
- [ ] 14 Job queue
- [ ] 15 Human-like timing
- [ ] 16 Traces across processes
- [ ] 17 Eval harness v0
- [ ] 18 Knowledge in the prompt
- [ ] 19 Tools and agent loop
- [ ] 20 AI observability
- [ ] 21 Handoff
- [ ] 22 Analyzer
- [ ] 23 Safety
- [ ] 24 First deploy
- [ ] Milestone B video

**Stages C–F:** tracked as GitHub issues when we get there.
