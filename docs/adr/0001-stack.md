# 0001. Core stack: FastAPI, Postgres, Procrastinate, own agent loop

- **Status:** Accepted
- **Date:** 2026-10-26

## Context

The product is an inbox where an AI agent answers customers and places orders. Most work is waiting on
I/O: webhooks, channel APIs and LLM calls. The agent must never lose a customer message, and an order
and its follow-up work must be saved together. One person builds it, so fewer moving parts matter.

## Decision

- **Backend: FastAPI + Pydantic (Python 3.14).** Python has the best AI ecosystem. FastAPI is async,
  which suits I/O-bound work. One set of Pydantic models validates requests, webhook payloads and LLM
  tool arguments, and gives an OpenAPI schema for the frontend.
- **Database: PostgreSQL + pgvector.** One database for tenant data, catalog, embeddings and the job
  queue, so related writes commit in one transaction. A separate vector store would add a sync problem
  with no benefit at this size.
- **ORM: SQLAlchemy 2 (async) + Alembic.** Explicit transactions and reviewable migrations.
- **Job queue: Procrastinate.** Jobs are rows in Postgres, so "save message" and "enqueue agent run"
  succeed or fail together. Rejected:
  - FastAPI `BackgroundTasks`: a crash or deploy loses the job, with no retries or locking.
  - Celery / Taskiq on Redis: the queue can drift from the database; Celery is not async-native.
- **Agent: our own loop, no LangChain or LangGraph.** The loop is small; the hard parts are our own
  rules (tool gating, injected identity, idempotent orders, handoff). LangChain adds hidden layers and
  churn. Pydantic AI is the fallback if we ever need a framework.
- **LLM: Groq first, Gemini as fallback**, through one OpenAI-compatible client.
- **Dashboard: Next.js + Tailwind + shadcn/ui.**

## Consequences

- Easier: one database to back up and reason about; transactions cover messages, orders and jobs.
- Easier: no framework magic around the agent, so every step is visible and testable.
- Harder: we write the agent loop, retries and tracing ourselves.
- Watch: Postgres carries the queue load too. Fine at this scale; revisit if job volume grows a lot.
- Watch: Gemini tool-calling through its OpenAI-compatible API must be tested before we rely on it.
