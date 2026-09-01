# Resume Bullets — Google XYZ Format

Bullets written in Google's recommended structure:

> **Accomplished [X] as measured by [Y] by doing [Z].**

Every number below was reproduced by running the code, or read directly out of the
source. Nothing here is estimated. Claims that could not be substantiated are listed
in [What not to claim](#what-not-to-claim) so they never reach a resume or a screen.

Companion documents: [`INTERVIEW.md`](INTERVIEW.md) for the design deep dives and
anticipated questions, and the portfolio at <https://dhruvaaher.dev/>.

---

## Which projects to put on a one-page resume

A one-page intern resume fits roughly three projects. Ranked by the strength of the
signal they send for a Google SWE intern screen:

| # | Project | Why it earns the slot |
|---|---------|----------------------|
| 1 | **UnderWrite** | Open-source contribution to a major project (DataHub), graph traversal, and a security boundary that is deterministic by construction. Rare for an intern candidate. |
| 2 | **RedisLite** | Systems fundamentals with a reproducible benchmark. Small enough (978 lines) to defend every line under questioning. |
| 3 | **Aura** | Distributed-systems depth — leases, leader election, reconciliation — backed by 223 passing tests. |

Keep **JusticeQueue** or **PRBeliefs** in reserve for AI/ML-leaning teams, and
**FlowBoard** or **DRRGT** if the role is explicitly full-stack or data/infra.

---

## 1. UnderWrite — ML deployment authorization gate

**Stack:** Python, FastAPI, LangGraph, DataHub, GraphQL, Docker, GitHub Actions, pytest

**Recommended bullets:**

- Built a fail-closed CI authorization gate for ML model deployments that blocks
  target-leakage before release, **verified by a 70-case test suite (67 running with no
  network dependency)**, by traversing DataHub column-level lineage with a
  depth-bounded DFS and cycle detection over a `visited` set.
- Eliminated the risk of an LLM approving an unsafe deployment, **measured by trust-boundary
  tests asserting that caller-supplied verdict fields are ignored and that an unreachable
  metadata server still returns `BLOCKED`**, by defaulting the verdict to `BLOCKED` and
  confining the language model to post-block remediation advice outside the decision path.
- Drove the design into upstream open source, **evidenced by three accepted-for-review
  submissions to the `datahub-project` organization** (a skills proposal, an implementation
  pull request, and a Core API issue for batch `schemaField` fetches), by isolating a
  reusable `datahub-ml-leakage` policy skill from the internal implementation.

**Shorter two-line variant:**

- Engineered a deterministic, fail-closed deployment gate that blocks ML models trained on
  post-outcome features, **validated by 70 tests and 3 documented policy rules**, by walking
  DataHub fine-grained lineage with a bounded DFS and enforcing `BLOCKED` as the default verdict.
- Contributed the pattern upstream to DataHub, **through 3 open submissions to the
  `datahub-project` org**, by extracting the leakage policy into a standalone reusable skill.

**Evidence:** `python3 -m pytest` → `67 passed, 3 skipped`. Traversal and depth bound in
`agent.py` (`GraphAcquisition`, `PolicyEvaluator`, `max_depth=6`). Default verdict at
`agent.py:172`. LLM confined to `remediation/advisor.py`. Policies `ML-LEAK-001`,
`ML-TEMPORAL-001`, `ML-FAIL-CLOSED` in `policies.yaml`. 4,469 lines of Python. Five
architectural tradeoffs written up in `ARCHITECTURAL_TRADEOFFS.md`.

**Say "open" not "merged."** All three upstream items are open at the time of writing.
State that plainly — it is still a real contribution to a real project, and being precise
about status is exactly the signal you want to send.

---

## 2. RedisLite — Redis-compatible key-value store in Go

**Stack:** Go, TCP sockets, RESP protocol, goroutines, `sync.RWMutex`, append-only file persistence

**Recommended bullets:**

- Implemented a Redis-compatible in-memory key-value store from scratch in Go supporting
  **11 commands** (`SET`, `GET`, `DEL`, `EXPIRE`, `TTL`, `HSET`, `HGET`, `LPUSH`, `LRANGE`,
  `PING`, `INFO`), **measured at 185,917 ops/sec with 0.10 ms p95 latency across 10 concurrent
  clients**, by hand-writing a RESP wire-protocol parser with no external libraries and
  serving each connection on its own goroutine.
- Achieved crash-durable state across restarts, **verified by replaying an append-only log on
  startup to reconstruct the keyspace**, by logging every mutating command to disk behind a
  dedicated mutex separate from the read path.
- Held read throughput under concurrent load, **measured by a custom TCP benchmark harness
  reporting throughput and p95 latency at a configurable read/write mix**, by guarding the
  store with a `sync.RWMutex` so reads proceed in parallel and sweeping expired keys on a
  background 100 ms ticker.

**Shorter two-line variant:**

- Built a Redis-compatible key-value store in Go from first principles, **sustaining 185,917
  ops/sec at 0.10 ms p95 over real TCP connections**, by writing a custom RESP protocol parser
  and a goroutine-per-connection concurrency model.
- Added durability and key expiry, **validated by a passing Go test suite and append-only-log
  replay on restart**, by pairing an `RWMutex`-guarded store with a 100 ms background eviction sweeper.

**Evidence:** `go test ./...` passes. Benchmark command
`go run benchmark.go -clients 10 -commands 1000 -mix 30` produced 185,917 ops/sec / 0.10 ms p95
on a cloud VM; the repository README records 74,498 ops/sec / 0.20 ms p95 on the author's
laptop. Commands enumerated from the dispatch switch in `server.go`. Eviction ticker at
`store.go:179`. AOF write and replay in `aof.go`. 978 lines of Go including 186 lines of tests.

**Quote whichever number you can defend on the day.** If you cite 185,917, be ready to say it
was measured on a cloud VM and that throughput is hardware-dependent. The conservative
"75K+ ops/sec" from your own machine is never wrong.

---

## 3. Aura — distributed job queue

**Stack:** TypeScript, Node.js, Redis, PostgreSQL, Prisma, Lua, Express, React, Docker, Vitest

**Recommended bullets:**

- Engineered a distributed job queue with at-least-once delivery across three priority tiers,
  **verified by 223 passing tests across 14 suites**, by implementing lease-based execution on
  Redis sorted sets with `ZPOPMAX` claims and atomic Lua scripts for the claim, retry, and
  promote paths.
- Guaranteed automatic recovery from worker, scheduler, and Redis failures, **covered by a
  leader-election suite that simulates a leader dying, its TTL expiring, and a follower taking
  over**, by electing a scheduler through `SET NX EX` on a 15-second lock and running reaper,
  promoter, and reconciler loops that restore Redis state from PostgreSQL as the durable source
  of truth.
- Protected the system from overload, **enforced by returning HTTP 429 when queue depth exceeds
  a ceiling derived from the observed drain rate**, by implementing adaptive backpressure with
  admission reservations and capped exponential retry backoff (`min(2^(n-1) × 1s, 60s)`) into a
  dead-letter queue.

**Shorter two-line variant:**

- Built a lease-based distributed job queue on Redis sorted sets and PostgreSQL, **validated by
  223 passing tests**, by implementing atomic Lua claim/retry scripts, Redis leader election, and
  a reconciler that rebuilds queue state from the durable store after a Redis flush.
- Added adaptive backpressure and a dead-letter path, **rejecting overload with HTTP 429 based on
  measured drain rate**, by tracking admission reservations and applying capped exponential backoff.

**Evidence:** `npx vitest run` in `apps/worker` → `Test Files 14 passed, Tests 223 passed`
(requires `prisma generate` first). Lua scripts in `packages/redis/src/lua.ts`, backoff formula
at line 69. Leader election tested in `apps/worker/src/__tests__/SchedulerLock.test.ts`.
Backpressure and 429 responses in `apps/api/src/routes/jobs.ts`. 7,219 lines of TypeScript,
36 distinct Redis key patterns.

**Do not claim a throughput number.** The load-test harness supports five scenarios
(burst, steady, mixed, priority-storm, failure-flood) and reports P50/P95/P99, but no measured
results are committed to the repository. Lead with 223 tests instead — it is stronger anyway,
because it is reproducible in front of the interviewer.

---

## 4. JusticeQueue — AI legal triage pipeline

**Stack:** Next.js 14, React, MongoDB Atlas Vector Search, Google Vertex AI, Gemini, Firebase Auth, Upstash Redis, Vercel

**Recommended bullets:**

- Built a model-directed triage pipeline that ranks legal-aid intake by urgency, **executing a
  13-step workflow in which Gemini makes 8 distinct routing decisions per run** (strategy, tool
  selection, case selection, retrieval sufficiency, and self-critique), by constraining the model
  to choose paths within a predefined step graph rather than plan freely.
- Grounded LLM triage in retrieved precedent, **using MongoDB Atlas `$vectorSearch` over 768-dimension
  `text-embedding-004` embeddings with cosine similarity and a 10× candidate oversample**, by
  persisting a pre-retrieval baseline score alongside the final score so retrieval's contribution
  is measurable rather than asserted.
- Made scoring auditable instead of opaque, **via a deterministic 0–100 function weighting four
  dimensions — deadline (40), client vulnerability (25), case type (20), and precedent similarity (15)**,
  by keeping the score a pure function and recording a full step-and-decision trace for every run.

**Evidence:** Step plan and decision points in `app/api/agent/docket/route.js`. Scoring function and
weights in `lib/urgencyScore.js`. Vector search parameters in `lib/vectorSearch.js`. Rate limiting via
Upstash in `lib/ratelimit.js`. 24 API route files exposing 30 handlers, 5 Mongoose models,
~16,000 lines of JavaScript and JSX.

**Do not claim the 60-case audit.** The README's "32 cases improved / +6 average / 4 critical
upgrades" is computed live from a deployed database through `/api/stats/public`; no result file is
committed. If you cite it, say it came from your deployment, not from the repository. Also note in
interviews that this project has **no automated tests and no CI** — volunteer it before it is found.

---

## 5. Receipts — verification for AI coding-agent claims

**Stack:** Node.js, React, Vite, Tailwind CSS, Codex CLI, GPT-5.6, Git, GitHub Actions

**Recommended bullets:**

- Built a tool that independently verifies what coding agents claim they did, **passing 15 pipeline
  tests enforced on every push by CI**, by extracting executable claims from agent transcripts, re-running
  the referenced commands, and diffing the repository for contradicting evidence.
- Caught agents reporting success on weakened test suites, **detecting three specific evasion patterns —
  skipped tests, removed assertions, and failures masked with `|| true`** — by inspecting `git diff` against
  test-file paths rather than trusting reported exit codes.
- Made verification safe to run on untrusted input, **restricting execution to an allowlist of test and
  build commands with a 30-second timeout and a 64 KiB output cap**, by rejecting shell metacharacters and
  running extraction inside an isolated read-only sandbox.

**Evidence:** `node --test server/pipeline/pipeline.test.mjs` → `15 pass, 0 fail`. CI at
`.github/workflows/verify.yml` runs `npm ci && npm run verify` (tests plus build). Detection logic in
`server/pipeline/diff.mjs`. Allowlist and caps in `server/pipeline/runner.mjs`. Verdict precedence
(FIX > RE-RUN > ESCALATE > MERGE) in `server/pipeline/verdict.mjs`. Three byte-stable frozen fixtures.

**Do not claim the stage timings.** The 9,876 ms / 214 ms / 61 ms / 10,152 ms figures appear only in
README prose; no timing artifact is committed. The `--measure` flag exists, so you can regenerate them —
but only quote them if you have re-run it.

---

## 6. PRBeliefs — AI code review GitHub App

**Stack:** Python, FastAPI, Redis, SQLite, Docker Compose, Groq, LLaMA 3.3 70B, GitHub Apps API, pytest

**Recommended bullets:**

- Shipped a GitHub App that reviews pull requests against a team's own past decisions, **covered by
  30 passing tests and installable from the GitHub Marketplace**, by persisting review rulings as
  retrievable "beliefs" and applying them to new pull requests automatically.
- Cut review wall-clock time relative to sequential execution, **by running 5 specialized review agents
  (security, performance, style, architecture, dependency) concurrently through `asyncio.gather`**, and
  aggregating their findings into a single ranked comment.
- Kept webhook ingestion resilient to burst traffic, **decoupling delivery from processing through a
  Redis-backed job queue**, by verifying each payload's HMAC-SHA256 `X-Hub-Signature-256` signature before
  enqueueing and rate-limiting per installation.

**Evidence:** `python3 -m pytest --asyncio-mode=auto` → `30 passed`. Parallel dispatch at
`orchestrator.py:37`. Signature verification exercised in `tests/test_main.py`. Live at
<https://github.com/apps/prbeliefs>. 2,226 lines of Python.

**Do not claim "sub-second reviews."** The README says it, but there is no benchmark artifact. Describe
the parallelism as a design choice instead of quoting a latency number.

---

## 7. FlowBoard — multi-tenant collaborative SaaS

**Stack:** FastAPI, async SQLAlchemy, PostgreSQL, Redis, WebSockets, Celery, Alembic, React, TypeScript, TanStack Query, Zustand, Docker

**Recommended bullets:**

- Built a multi-tenant collaborative workspace platform exposing **34 REST endpoints across 7 data models**,
  by enforcing workspace-scoped isolation on every query so no request can read another tenant's data.
- Implemented role-based access control across four roles (owner, admin, member, viewer), **enforced through
  an explicit permission matrix and role hierarchy rather than scattered inline checks**, by centralizing
  authorization in a single permissions module and covering it with unit tests.
- Delivered real-time multi-client collaboration, **synchronizing Kanban and document state across
  connected clients**, by fanning out updates over WebSockets with Redis pub/sub and offloading
  notification work to Celery workers.

**Evidence:** Role hierarchy and permission matrix in `backend/app/core/permissions.py`. 34 route
decorators across the backend, 7 models in `backend/app/models/`, 2 Alembic migrations.
4,081 lines of Python and 4,292 lines of TypeScript. `pytest` runs 12 unit tests green; the 42
integration tests require a live PostgreSQL instance and were not executed in this environment —
say exactly that if asked.

---

## 8. DRRGT — FEMA disaster relief analytics

**Stack:** Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, Celery, Redis, Pandas, NumPy, SciPy, scikit-learn, Terraform, AWS (ECS, RDS, ElastiCache, ALB, S3, ECR, CloudWatch), Docker, GitHub Actions

**Recommended bullets:**

- Built an ETL and analytics platform quantifying how long federal disaster aid takes to reach U.S.
  counties, **reducing per-county upserts to a single batched statement across ~3,200 counties** via
  PostgreSQL `INSERT … ON CONFLICT`, by joining OpenFEMA declarations and Public Assistance records to
  Census demographics on FIPS codes.
- Made the API respond without request-time computation, **serving analytics endpoints from a
  precomputed cache table plus a Redis layer invalidated after each ETL run**, by shifting quintile,
  trend, and correlation aggregation into a nightly Celery job scheduled at 06:00 UTC.
- Provisioned the full production environment as code, **declaring 33 AWS resources in Terraform** —
  ECS services, RDS PostgreSQL, ElastiCache Redis, an application load balancer, S3, ECR, autoscaling
  policies, and CloudWatch alarms — with GitHub Actions building images to ECR and deploying to ECS on merge.
- Kept third-party ingestion resilient, **paginating OpenFEMA at 1,000 records per page with three-attempt
  exponential backoff and 5,000-row batch inserts**, by falling back to committed sample data when an
  upstream API is unavailable.

**Evidence:** Batch upsert and 5,000-row batching in `backend/app/etl/pipeline.py`. Pagination and backoff
in `backend/app/etl/ingest.py`. Peer-county matching (same rural/urban class, population and median income
within ±25%, nearest five) in `backend/app/etl/insights.py`. Celery schedule in `worker/celery_app.py`.
33 `aws_*` resources in `infra/main.tf`. 19 API handlers, 8 tables, 10 backend tests, 2,752 lines of Python.

**Do not claim "810K+ records analyzed."** That number appears nowhere in the repository — only as a
memory-sizing comment in Terraform. Use the 3,200-county figure and the pagination/batching mechanics,
which are real.

---

## ATS keyword bank

Applicant tracking systems match on literal terms. These all correspond to something genuinely
present in the repositories — do not pad with anything you cannot point at in code.

**Languages:** Go, Python, TypeScript, JavaScript, SQL, Lua, Bash, HCL

**Backend & APIs:** FastAPI, Node.js, Express, Next.js, REST API, GraphQL, WebSockets, gRPC-style RPC,
asyncio, SQLAlchemy, Prisma, Mongoose, Alembic, Celery, Pydantic, JWT, OAuth 2.0, HMAC, RBAC, webhooks,
rate limiting, pagination, exponential backoff, idempotency

**Distributed systems:** distributed systems, job queue, task scheduler, leader election, distributed
locking, lease-based execution, at-least-once delivery, backpressure, dead-letter queue, crash recovery,
reconciliation, pub/sub, concurrency, goroutines, mutex, TCP, RESP protocol, caching, sharding

**Data & storage:** PostgreSQL, Redis, MongoDB, MongoDB Atlas Vector Search, SQLite, ETL, data pipeline,
batch processing, database indexing, query optimization, schema migrations, Pandas, NumPy, SciPy

**AI & ML:** LLM, large language models, AI agents, multi-agent systems, agentic workflows, RAG,
retrieval-augmented generation, vector search, embeddings, semantic search, LangGraph, Google Gemini,
Vertex AI, GPT-5.6, LLaMA, prompt engineering, model evaluation, data lineage, ML governance

**Cloud & DevOps:** AWS, ECS, RDS, ElastiCache, S3, ECR, CloudWatch, Application Load Balancer, GCP,
Google Cloud, Terraform, Infrastructure as Code, Docker, Docker Compose, CI/CD, GitHub Actions, Vercel,
observability, monitoring, autoscaling

**Frontend:** React, Next.js, TypeScript, Tailwind CSS, TanStack Query, Zustand, Vite, WebSockets,
responsive design

**Practices:** unit testing, integration testing, pytest, Vitest, test-driven development, code review,
open source contribution, system design, API design, fail-closed design, threat modeling, technical documentation

---

## What not to claim

Numbers that appear in project READMEs or on the portfolio but are **not** substantiated by anything
committed to the repositories. Leaving these off is what makes everything else credible.

| Claim | Status | Use instead |
|---|---|---|
| Aura: "20,000+ concurrent tasks" | Load-test configuration, not a recorded result | 223 passing tests; five load-test scenarios |
| Aura: "6,000+ tasks recovered in <2 s" | No evidence anywhere in the repository | Reaper/reconciler design and its test coverage |
| DRRGT: "810K+ records analyzed" | Only a Terraform sizing comment | ~3,200 counties; 1,000-per-page pagination |
| DRRGT: "millions of records" | README prose only | Same as above |
| Receipts: "19 tests" | Actual count is 15 | 15 passing tests, enforced by CI |
| Receipts: stage timings (9,876 ms etc.) | README prose; no committed artifact | Re-run with `--measure`, or omit |
| PRBeliefs: "sub-second reviews" | No benchmark artifact | Parallel agents via `asyncio.gather`; 30 tests |
| JusticeQueue: 60-case audit (32/+6/4) | Computed live from a deployment; not committed | Attribute to your deployment explicitly |
| UnderWrite: "upstreamed into DataHub" | All three submissions are open, not merged | "Proposed upstream"; three open submissions |

---

## Verification appendix

Every command below was run against a fresh clone. Results are reproducible.

| Project | Command | Result |
|---|---|---|
| UnderWrite | `python3 -m pytest` | 67 passed, 3 skipped (70 total) |
| RedisLite | `go test ./...` | ok |
| RedisLite | `go run benchmark.go -clients 10 -commands 1000 -mix 30` | 185,917 ops/sec, 0.10 ms p95 |
| Aura | `npx prisma generate` then `npx vitest run` | 14 files, 223 tests passed |
| Receipts | `node --test server/pipeline/pipeline.test.mjs` | 15 passed, 0 failed |
| PRBeliefs | `python3 -m pytest --asyncio-mode=auto` | 30 passed |
| FlowBoard | `python3 -m pytest --asyncio-mode=auto` | 12 unit passed; 42 integration need PostgreSQL |
| UnderWrite upstream | GitHub API on the three submissions | All exist, authored by `Dhruva-Aher`, all open |
| Live demos | HTTP status check | JusticeQueue, Aura, PRBeliefs app page, portfolio all return 200 |
