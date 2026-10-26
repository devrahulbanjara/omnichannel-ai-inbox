# Interview prep

This project is built to be **the project you talk about in interviews**. This file covers how interviews will use it, the questions to expect, how to answer, and how we practise after every step.

---

## 1. Where this project shows up in interviews

| Round | What happens | How this project helps |
|---|---|---|
| **Resume screen** | 6–10 seconds per resume | One strong bullet with real numbers (§3) |
| **"Tell me about a project"** | 2–5 minutes | Your pitch (§2) |
| **Project deep dive** | 20–45 min of follow-ups on *your* project: trade-offs, failures, scale, what you'd change | Every ADR, journal entry and test is ammunition |
| **System design** | "Design a chat system / webhook system / AI support agent" | You have actually built these parts (§5) |
| **AI engineer round** | RAG, agents, tool calling, evals, prompt injection, cost | Stage B is exactly this (§4.6) |
| **Behavioral** | "Tell me about a time…" | Real bugs and decisions from `JOURNAL.md` become STAR stories (§6) |
| **Live coding / take-home** | Build a small API or feature | You'll have written FastAPI, SQL, tests and async code many times |

Interviewers dig into trade-offs (expect **two or three levels of "why"**), failures ("what broke first?"), scale ("what changes at 10× load?") and your own decisions. They want concrete numbers, not "it was fast".

---

## 2. Your pitch (fill in as we build)

Templates. Replace the brackets with real facts **only once they're true**.

**30 seconds**
> I built an omnichannel inbox where an AI agent talks to store customers, answers questions, and places orders, and staff can take over any time. Customers chat through RahulCoolGram, a simple Instagram clone I built that sends their messages to the inbox as webhooks. The interesting part is the agent: it can only act through typed tools, prices and order totals always come from the database, and every run is traced and covered by [N] automated evals in CI.

**2 minutes:** problem → architecture in one sentence → the hardest problem → one number → what you'd do next.

**10-minute deep dive** (use the diagram in `ROADMAP.md` §2):
1. **Problem and constraints** (stores selling through DMs; AI must never invent prices; webhooks retry)
2. **Architecture** (ingress → Postgres + job queue → worker → LLM → send; WebSocket for live UI)
3. **Hardest problem** (e.g. duplicate replies from webhook retries → transactional enqueue + dedupe)
4. **Key trade-offs** (Postgres queue vs Redis queue; own agent loop vs LangChain; RahulCoolGram vs real Instagram)
5. **How I know it works** (evals, chaos test, load test, tracing)
6. **What I'd change** (be honest; interviewers love this)

---

## 3. Resume bullets (templates; fill with measured numbers only)

- Built a multi-tenant AI customer-messaging platform (FastAPI, PostgreSQL, Next.js) where an LLM agent answers and places orders through [N] typed tools; prices and totals always come from the database, never the model.
- Designed idempotent webhook ingestion (authenticated webhooks, dedupe, transactional job enqueue); chaos tests with duplicated and failed deliveries produced **0 duplicate orders and 0 lost messages** over [N] runs.
- Built an LLM eval suite of [N] scripted conversations (including prompt-injection attacks) running in CI; raised task success from [X]% to [Y]% across prompt iterations.
- Instrumented end-to-end tracing (OpenTelemetry, Grafana, Langfuse) from webhook to reply; p95 reply latency [X] s at [N] webhooks/min (k6).

> **Rule:** never write a number you didn't measure. Interviewers ask "how did you measure that?"

---

## 4. Question bank

Each question lists the step that teaches it. "Strong answer covers" lists the points that separate a good answer from an average one.

### 4.1 Backend and APIs
| Question | Step |
|---|---|
| What happens when a browser makes a request to your API? | 1 |
| PUT vs PATCH vs POST? Which are idempotent? | 2 |
| 400 vs 401 vs 403 vs 404 vs 409 vs 422? | 2 |
| Why async in Python? When does async *not* help? | 4 |
| What is dependency injection in FastAPI and why use it? | 4 |
| What is CORS? Why does the browser block your request but curl doesn't? | 6 |
| How do you keep frontend and backend types in sync? | 6 |
| How do you version an API? | 6 |

### 4.2 Databases
| Question | Step |
|---|---|
| Why Postgres here and not MongoDB? | 3 |
| What is a transaction? What isolation level does Postgres use by default? | 4 |
| How do you add a `NOT NULL` column to a big table without downtime? | 4, 24 |
| How do you generate per-store order numbers without gaps or duplicates under concurrency? | 29 |
| What is row-level security? What are its pitfalls with connection pools? | 35 |
| What indexes does the inbox list need? How do you check a query is using them? | 11 |

**Strong answer: "two requests create an order at the same moment"**
- name the race (both read stock = 1, both decrement)
- lock (`SELECT … FOR UPDATE`) or a conditional update (`… WHERE on_hand >= qty`)
- idempotency key so a retry is a no-op (`quote_id UNIQUE`)
- say how you **tested** it (concurrent test / chaos test)

### 4.3 Reliability and messaging
| Question | Step |
|---|---|
| Why must a webhook handler return fast? | 13 |
| Exactly-once vs at-least-once delivery? Which can you actually get? | 9 |
| How do you make a webhook consumer idempotent? | 9 |
| Queue vs pub/sub — when do you use each? | 14 |
| What is the transactional outbox pattern and what problem does it solve? | 14 |
| Why not FastAPI `BackgroundTasks`? | 14 |
| Which errors should be retried? How do you avoid a retry storm? | 10, 12 |
| How do you stop two workers handling the same conversation? | 15 |
| What happens if a worker dies halfway through a job? | 14, 15 |

**Strong answer: "Why must webhooks return fast?"**
- the sender has a timeout; a slow response looks like failure → it **retries** → duplicates
- Meta recommends acknowledging before slow processing, retries for up to 36 h, and may batch up to 1000 events
- pattern: verify → store raw → enqueue (same transaction) → `200`; worker does the slow part
- your own evidence: "In step 13 I did it the naive way and got duplicate replies; here's how I fixed it"

### 4.4 Realtime
| Question | Step |
|---|---|
| Polling vs long polling vs SSE vs WebSocket? | 11 |
| How do you scale WebSockets to several servers? | 14 |
| How does a reconnecting client catch up on missed messages? | 11 |
| How do you keep message order within a conversation? | 11 |

### 4.5 Security and multi-tenancy
| Question | Step |
|---|---|
| How do you verify a webhook came from Meta? Why the raw body? Why constant-time compare? | 9 |
| Sessions vs JWT for a dashboard — which and why? | 32 |
| How do you store passwords? | 32 |
| What is CSRF, and how do httpOnly cookies relate to it? | 32 |
| How do you make sure store A can never see store B's data? | 35 |
| How do you store third-party access tokens safely? | 34 |
| How does OAuth authorization-code flow work? | 34 |

### 4.6 AI engineering
| Question | Step |
|---|---|
| How do you handle LLM rate limits and provider outages? | 12 |
| How do you test an LLM application? | 17 |
| How do you know a prompt change didn't make things worse? | 17, 38 |
| Walk me through your agent loop. How does it terminate? | 19 |
| Agent or workflow — how do you decide? | 19 |
| How do you design a good tool for an LLM? | 19 |
| How do you stop the model inventing prices or order numbers? | 27–30 |
| How do you defend against prompt injection, including through tool outputs? | 23 |
| What is "excessive agency" and how did you limit it? | 21, 23 |
| How do you debug a wrong answer in production? | 20 |
| How do you control cost per conversation? | 19, 42 |
| When would you add RAG? How do you evaluate retrieval? | 39 |
| Why your own agent loop instead of LangChain / LangGraph? | 19 |
| LLM-as-judge: what are its biases and how do you reduce them? | 38 |

**Strong answer: "How do you test an LLM application?"**
- three layers: unit tests for code (tools, state machine, scoring); **evals** for behaviour; production monitoring
- evals = golden dataset of scripted conversations, including adversarial ones and past failures
- check **trajectories** (right tool, right arguments, `create_order` exactly once), not just final text
- deterministic assertions where possible; LLM judge with a rubric only where needed (and know its biases)
- cached responses → reproducible, free reruns; run in CI on prompt/model changes; track scores over time

**Strong answer: "How do you stop the model inventing prices?"**
- the model **never computes** money: totals come from a `quote_order` tool backed by the DB
- `create_order` takes only a `quote_id`; server re-checks stock and price in a transaction
- pre-send checker: every number in the reply must appear in tool results
- evals measure "hallucinated-number rate"

### 4.7 Observability and operations
| Question | Step |
|---|---|
| Logs vs metrics vs traces? | 2, 16 |
| What are the four golden signals? | 16 |
| A customer says replies are slow. How do you find out why? | 16 |
| What is an SLO? Give one for this system. How do you alert on it? | 37 |
| Monitoring vs observability? | 16, 37 |
| How do you deploy a migration safely? How do you roll back? | 24 |
| Tell me about an incident you handled. | 43 |

---

## 5. System design questions this project prepares you for

Practise these as whiteboard sessions. Your edge: you can say *"in my project I did X, and here's what broke."*

| Prompt | Parts you've built |
|---|---|
| Design a unified inbox (Intercom / Zendesk / Front) | Everything in Stage A + D |
| Design a webhook ingestion system for 10M events/day | Step 9, 14, 40 |
| Design a chat / messaging system (WhatsApp, Slack) | Steps 8–11, 14 |
| Design an AI customer-support agent | Stage B |
| Design an order placement system that never double-charges | Steps 27–29 |
| Design a rate limiter | Step 41 |
| Design a notification system | Steps 11, 14, 21 |
| Design multi-tenant SaaS data isolation | Step 35 |

**How to structure any design answer:** requirements and guarantees first (what must be durable, ordered, exactly-once vs best-effort) → rough numbers → API → data model → architecture → deep dive on the hardest part → failure modes → what changes at 10×.

---

## 6. Behavioral stories (STAR)

**S**ituation · **T**ask · **A**ction · **R**esult (+ what you learned). Use "I", not "we". Pick real failures, not humblebrags.

Fill this table from `JOURNAL.md` as you go. Aim for 6–8 strong stories by Milestone B.

| Prompt | Likely story from this project | Filled? |
|---|---|---|
| A hard bug you solved | Duplicate replies from webhook retries (step 13–14) | ☐ |
| A trade-off you made | Postgres queue vs Redis/Celery; own agent loop vs LangChain | ☐ |
| A time you were wrong | Something you designed, then changed after testing | ☐ |
| A time you improved quality | Eval score before/after a prompt or tool change | ☐ |
| A time you learned something fast | First time with OpenTelemetry / RLS / WebSockets | ☐ |
| A failure | The postmortem (step 43) | ☐ |
| Prioritising | Choosing RahulCoolGram over real Instagram; AI before auth | ☐ |
| Handling ambiguity | Deciding when the agent should hand off | ☐ |

Story template:
```
Title:
Situation (1–2 lines):
Task — what I had to do:
Action — what I did, step by step, and why:
Result — numbers if possible:
What I learned / would do differently:
```

---

## 7. How we practise (real mock interviews)

After each step we do a **mock interview** right here in the terminal. Say **"interview me on step N"** (or "mock deep dive", "mock system design", "mock behavioral").

**Format**
1. I ask **one question at a time** (3–5 per step), the way a real interviewer would, including follow-ups ("why?", "what if it fails?", "what at 10×?").
2. You answer **in your own words** without looking at the docs (typing is fine; speaking it out loud first is better).
3. I grade each answer and show what a strong answer adds.

**Rubric (each 1–4)**

| | 1 | 4 |
|---|---|---|
| **Correctness** | Wrong or vague | Accurate, precise terms |
| **Depth** | Says *what* | Explains *why*, and the alternatives |
| **Evidence** | Generic | Uses this project: "in step 9 I…" |
| **Trade-offs & failure** | Ignores them | Names costs, failure modes, what changes at scale |
| **Communication** | Rambling | Structured: answer first, then detail |

**Practice types by stage**

| After | Practise |
|---|---|
| Each step | 3–5 questions on that step |
| Milestone A | 30-second + 2-minute pitch; system design: "Design a chat system" |
| Milestone B | Full 30-min project deep dive; AI round; system design: "Design an AI support agent" |
| Stage C | "Design order placement that never double-charges" |
| Stage D–E | Security/tenancy round; "tell me about an incident"; full mock loop |

Weak spots get logged in `JOURNAL.md` and come back in later mocks.

---

## 8. Honesty rules

- Never claim a scale, metric or feature you haven't built and measured.
- It's fine — good, even — to say "I haven't done X; here's how I would approach it."
- Know every line you wrote. If AI helped write code, you must still be able to explain it and defend it.
- RahulCoolGram is a strength, not a weakness: "I built a small Instagram clone so I could drive real conversations end to end, and replay duplicate or failed webhooks on purpose."

---

## Sources

- Project deep dives: [Ashby — past-projects deep dive](https://www.ashbyhq.com/resources/engineer-past-projects-deep-dive) · [Yusuf Aytas — technical deep dives](https://yusufaytas.com/technical-deep-dives) · [PracHub — trade-offs, scale, hardest part](https://prachub.com/interview-questions/senior-engineer-project-deep-dive-trade-offs-scale-challenges-hardest-part)
- AI engineer interviews: [letsdatascience — 50 LLM/AI engineer questions](https://letsdatascience.com/blog/50-llm-and-ai-engineer-interview-questions-for-2026) · [PracHub — RAG, agents, evals, production](https://prachub.com/resources/ai-engineer-interview-questions-2026-rag-agents-evals-and-production-systems) · [techscreen — LLM, RAG and agents](https://techscreen.app/articles/ai-engineer-llm-interview-questions-2026)
- System design: [Hello Interview — messenger](https://www.hellointerview.com/community/questions/messenger-chat-system/cm4szunov00303g2e2gomqo2j) · [Educative — webhook system design](https://www.educative.io/blog/webhook-system-design) · [Educative — chat system design](https://www.educative.io/blog/chat-system-design)
- Behavioral: [techinterview.org — STAR method](https://www.techinterview.org/post/3233460435/behavioral-interview-star-method/) · [Leland — software engineer behavioral](https://www.joinleland.com/library/a/how-to-nail-software-engineer-behavioral-interview-questions-with-examples)
- Idempotency interview angle: [Stripe's approach explained](https://arpitbhayani.me/videos/designing-idempotent-api-endpoints-stripe)
- Meta webhook behaviour: [Instagram webhooks setup](https://developers.facebook.com/documentation/instagram-platform/webhooks/setup)
- Agents: [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
