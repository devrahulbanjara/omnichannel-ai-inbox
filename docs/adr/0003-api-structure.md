# 0003. Layered `app/` package for the API

- **Status:** Accepted
- **Date:** 2026-10-26

## Context

The API started as a few flat modules (`main.py`, `core/`, `inbox/`). With a database, a service layer
and more endpoints coming, code needs a predictable home. Two common FastAPI layouts exist: by layer
(routers, services, models…) and by domain (one folder per feature with its own router, models,
service). The by-domain layout suits large monoliths with many domains; this project has a few.

## Decision

One `app/` package in `apps/api`, organised by layer:

- `core/` (settings, database, logging, middleware, errors), `models/`, `schemas/`, `services/`,
  `routers/`, plus `dependencies.py` and `main.py` (`create_app()`).
- Services are classes that receive the request's session in `__init__` and raise `AppError`
  subclasses, never `HTTPException`. Models carry domain behaviour (`Conversation.reply_as_staff`).
- Imports are absolute (`from app.core.config import settings`).

Rejected:

- **By-domain folders:** more structure than a handful of domains needs.
- **A repository layer:** with simple queries it would only repeat the services.
- **Column mixins** (id, org_id, created_at): each model lists its own columns; easier to read.

## Consequences

- Easier: every file type has one obvious place; services are testable and reusable by future callers
  (AI tools, workers).
- Harder: a feature touches several folders (model, schema, service, router).
- Watch: if the number of domains grows a lot, revisit the by-domain layout.
