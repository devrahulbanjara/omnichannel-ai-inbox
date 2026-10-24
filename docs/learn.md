# Learning Map

Every concept and tool this project uses, how they relate, and the order to study them.

- ⭐ marks what to learn before Phase 1.
- **(tool)** marks a specific product. Everything else is a concept.

---

## Concepts vs tools

Most confusion comes from mixing ideas with products. There are four core ideas; the rest are tools that implement them.

| Idea | What it does | Tool used here |
|---|---|---|
| **Database** | Remembers things permanently | PostgreSQL |
| **Queue** | A to-do list of work; each item done by exactly one worker | Procrastinate (on Postgres) |
| **Pub/sub** | A live announcement every listener receives; nothing is stored | Redis |
| **WebSocket** | An open line from the server to the browser | FastAPI |

- **Redis** is a fast in-memory database, used here mainly for pub/sub.
- **Message broker** is a category name for software that passes messages around (Redis, RabbitMQ, Kafka).
- **Procrastinate** is a Python library that turns a Postgres table into a queue.

### Queue vs pub/sub

|  | Queue | Pub/sub |
|---|---|---|
| Who receives it | One worker | Every subscriber |
| If nobody is listening | Waits until a worker takes it | Lost |
| Use for | Work that must happen exactly once | Telling everyone something changed |

Rule of thumb: if losing it would hurt a customer or the data, use the queue. If it is only a live screen update that can be reloaded, use pub/sub.

### Restaurant model

| Restaurant | System |
|---|---|
| Customer at the counter | Message arriving from a channel |
| Order book | Database |
| Ticket rail | Queue |
| Cooks | Workers |
| Kitchen bell | Pub/sub |
| Live status screen at each table | WebSocket to the dashboard |

1. The cashier writes the order in the book, hangs a ticket on the rail and immediately confirms to the customer.
2. One free cook takes the ticket and cooks.
3. The cook marks it ready in the book and rings the bell.
4. Waiters hear the bell and update the screens at the tables.

---

## Map

```
SYSTEM
│
├── 1. WEB BASICS ⭐ ─────────────── how programs talk over the internet
│   ├── HTTP ⭐                      A request/response protocol: a client asks, a server answers, then it's done.
│   │   ├── Methods ⭐               GET reads, POST creates, PATCH updates, DELETE removes.
│   │   ├── Status codes ⭐          How it went: 200 OK, 4xx the caller's mistake, 5xx the server's mistake.
│   │   └── JSON ⭐                  The text format both sides use to send structured data.
│   ├── API / REST ⭐                A set of URLs a server offers so other programs can use it.
│   ├── Webhook ⭐                   An HTTP request another service (Meta, Telegram) sends you when something happens.
│   └── Cookie / Session ⭐          How a server remembers a logged-in browser between requests.
│
├── 2. RUNNING CODE ─────────────── how work happens at the same time
│   ├── Process                      A running program with its own memory; the API and worker are separate processes.
│   ├── Thread                       A lighter unit of work inside a process.
│   └── Async / await ⭐             Lets one process handle many waiting tasks without blocking.
│       └── Event loop               The engine in Python that switches between waiting async tasks.
│
├── 3. DATA STORAGE ⭐ ───────────── remembering things permanently
│   ├── Relational database ⭐       Stores data in tables of rows and columns that link to each other.
│   │   ├── PostgreSQL (tool) ⭐     The relational database used here.
│   │   ├── SQL ⭐                   The language for reading and writing tables.
│   │   ├── Primary / foreign key ⭐ A row's unique ID / a column pointing to a row in another table.
│   │   ├── Index                    A lookup structure that makes searches fast.
│   │   ├── Constraint (UNIQUE) ⭐   A rule the database enforces, e.g. no two messages with the same external id.
│   │   ├── Transaction ⭐           A group of writes that all succeed or all fail together.
│   │   ├── Lock                     Stops two processes changing the same thing at the same time.
│   │   ├── JSONB                    A column type that stores flexible JSON inside Postgres.
│   │   ├── Row-Level Security       Database rules that hide rows from the wrong tenant automatically.
│   │   └── pgvector (tool)          A Postgres extension that stores embeddings and finds similar ones.
│   ├── ORM ⭐                       Work with rows as Python objects instead of raw SQL.
│   │   └── SQLAlchemy (tool) ⭐     The ORM used here.
│   ├── Migration ⭐                 A versioned script that changes the database structure safely.
│   │   └── Alembic (tool) ⭐        The migration tool for SQLAlchemy.
│   └── In-memory store              Very fast storage kept in RAM; fast but not permanent.
│       └── Redis (tool)             Used here for pub/sub and rate-limit counters.
│
├── 4. MESSAGING ⭐ ──────────────── passing work and news between parts of the system
│   ├── Message broker               Category name for software that delivers messages between programs.
│   │
│   ├── QUEUE ⭐ (point-to-point)    A to-do list; each item is done by exactly one worker and kept until done.
│   │   ├── Job ⭐                   One unit of work, e.g. "run the agent for conversation 42".
│   │   ├── Producer ⭐              The code that adds jobs (the API).
│   │   ├── Worker / consumer ⭐     A process that takes jobs and does them.
│   │   ├── Retry ⭐                 Trying a failed job again later, automatically.
│   │   ├── Scheduled job            A job set to run at a future time (used for debounce).
│   │   ├── Dead-letter queue        Where jobs go after failing too many times, for a human to inspect.
│   │   ├── Queueing lock            Only one job with the same key runs at once (one agent run per conversation).
│   │   └── Tools: Procrastinate ⭐ (used here, jobs in Postgres) · Celery · Taskiq · RabbitMQ
│   │
│   ├── PUB/SUB ⭐ (broadcast)        A live announcement every listener receives; nothing is stored.
│   │   ├── Channel / topic          The named stream messages are published on, e.g. conversation:42.
│   │   ├── Publisher                The code that announces something happened.
│   │   ├── Subscriber               The code listening on a channel.
│   │   └── Tools: Redis pub/sub (used here) · Postgres LISTEN/NOTIFY · Kafka
│   │
│   └── Reliability patterns
│       ├── Idempotency ⭐            Doing the same thing twice has the same result as doing it once.
│       ├── Transactional outbox      Saving data and its follow-up record in one transaction.
│       └── Debounce                  Waiting briefly so a burst of events triggers one action.
│
├── 5. REAL-TIME TO THE BROWSER ─── getting updates onto the screen instantly
│   ├── Polling                      The browser keeps asking "anything new?" every few seconds.
│   ├── SSE                          A one-way stream from server to browser.
│   └── WebSocket ⭐                 A two-way connection that stays open so the server can push any time.
│       └── Room                     A group of connections that receive the same updates.
│
├── 6. BACKEND FRAMEWORK ⭐
│   ├── FastAPI (tool) ⭐            The Python web framework that turns functions into API endpoints.
│   ├── Pydantic (tool) ⭐           Defines data shapes as Python classes and validates data against them.
│   ├── Dependency injection         FastAPI passing a function what it needs (database session, current user).
│   └── OpenAPI                      An auto-generated description of the API that tools turn into a typed client.
│
├── 7. SECURITY & TENANCY
│   ├── Authentication               Proving who a user is.
│   ├── Authorization / RBAC         Deciding what that user may do (owner, admin, agent).
│   ├── Password hashing (argon2)    Storing passwords so they can't be read even if the database leaks.
│   ├── CSRF                         Another site tricking a browser into sending requests; tokens prevent it.
│   ├── HMAC signature               A secret-based checksum proving a webhook really came from the sender.
│   ├── Multi-tenancy ⭐             Many stores share one system without seeing each other's data.
│   └── Encryption at rest           Storing secrets such as channel tokens scrambled in the database.
│
├── 8. AI ───────────────────────── the agent
│   ├── LLM ⭐                       A model that reads text and predicts a reply (Groq, Gemini).
│   │   ├── Prompt / system prompt ⭐ The instructions and context sent to the model.
│   │   ├── Token                    The unit LLMs count text in; drives cost and limits.
│   │   ├── Context window           The maximum amount of text the model reads at once.
│   │   └── Rate limit / fallback    Provider request caps / switching provider when one fails.
│   ├── Tool (function) calling ⭐   The model asks the code to run a function and uses the result.
│   ├── Structured output ⭐         Making the model reply in an exact JSON shape defined by Pydantic.
│   ├── Agent loop ⭐                Ask the model → run requested tools → return results → repeat until it answers.
│   ├── Embedding                    A list of numbers representing a text's meaning; similar texts are close.
│   ├── RAG                          Retrieve relevant documents by embedding and give them to the model as context.
│   ├── Guardrails / checker         Rules and a reviewer that block bad replies before they are sent.
│   ├── Evals                        Automated tests that score the agent on scripted conversations.
│   └── Tracing (Langfuse, tool)     Records every prompt, tool call and cost for debugging.
│
├── 9. FRONTEND (built)
│   ├── React                        A UI library built from components.
│   ├── Next.js (tool)               The React framework the dashboard runs on.
│   └── TanStack Query (tool)        Fetches and caches API data in the frontend.
│
└── 10. RUNNING & OPERATING
    ├── Docker ⭐                    Packages a program with everything it needs so it runs the same anywhere.
    │   └── Docker Compose ⭐        Starts several containers together (Postgres, Redis, API, worker).
    ├── Environment variables ⭐     Settings and secrets passed to a program from outside the code.
    ├── Tunnel (Cloudflare, tool)    Gives a laptop a public URL so Meta and Telegram can reach it.
    ├── CI (GitHub Actions, tool)    Runs tests automatically on every push.
    └── Observability                Seeing inside a running system.
        ├── Logs                     Text records of what happened.
        ├── Metrics                  Numbers over time, such as queue size and latency.
        └── Traces (OpenTelemetry)   One request's full path across all services, step by step.
```

---

## Message flow, end to end

1. Instagram sends a webhook. The API saves the message, adds a job to the queue in the same transaction, and replies "received" immediately.
2. One worker takes the job.
3. The worker runs the agent: it calls the LLM, which calls tools such as `search_products`.
4. The worker saves the reply and adds a "send this reply" job to the queue.
5. The worker publishes "new message in conversation 42" on pub/sub.
6. The API server holding the staff member's WebSocket receives it and pushes it to the browser.

---

## Study order

Each step builds on the previous one. Steps 1–6 cover everything Phase 1 needs.

| # | Topic | Section | Goal |
|---|---|---|---|
| 1 | HTTP, REST, JSON, webhooks | 1 | Understand requests, responses and who calls whom |
| 2 | Async/await in Python | 2 | Write code that waits on network calls without blocking |
| 3 | SQL and Postgres: tables, keys, UNIQUE, transactions | 3 | Model data and make writes all-or-nothing |
| 4 | FastAPI and Pydantic | 6 | Build a small CRUD API with validated input |
| 5 | SQLAlchemy and Alembic | 3 | Connect the API to Postgres and evolve the schema |
| 6 | Docker and Docker Compose | 10 | Run Postgres and Redis without installing them |
| 7 | Queues: job, worker, retry | 4 | Run one Procrastinate job end to end |
| 8 | Pub/sub and WebSocket | 4, 5 | Push a message from a terminal to a browser |
| 9 | Idempotency and transactional outbox | 4 | Understand why data and its job are saved together |
| 10 | LLM tool calling and the agent loop | 8 | Call Groq with one tool and loop until it answers |
| 11 | Security, tenancy, observability | 7, 10 | Learned while building |
