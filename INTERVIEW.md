# Interview Defense Pack

This document exists so that every claim on [dhruvaaher.dev](https://dhruvaaher.dev/) can be
checked, reproduced, or — where it could not be substantiated — is explicitly marked as removed.

The portfolio was audited claim by claim against the actual source repositories. Some numbers
survived that audit unchanged, some were tightened, and some were deleted. The deletions are
recorded here as prominently as the confirmations, because a claim you can defend is worth more
than a bigger number you cannot.

Ground rules used throughout:

- A **measurement** is a number produced by a command that anyone can rerun. It is stated with the
  command and the hardware it ran on.
- A **design claim** is a property of the architecture that follows from reading the code. It is
  never written as if it were a benchmark.
- If a number appears nowhere in the repository and cannot be reproduced, it is not on the site.

---

## 1. Verification evidence

### Claims that were verified and kept

| Claim | How it was checked | Observed result | Verdict |
| --- | --- | --- | --- |
| UnderWrite: 70 tests, 67 with no network dependency | `python3 -m pytest` in `Dhruva-Aher/UnderWrite` | `67 passed, 3 skipped` (3 skips are network-gated) | Exact |
| UnderWrite: 5-stage pipeline, fail-closed design | Read `README.md` and `ARCHITECTURAL_TRADEOFFS.md` | Both documented in repo | Verified |
| UnderWrite: 3 upstream submissions to DataHub | Opened all three URLs on the `datahub-project` org | All real, all authored by `Dhruva-Aher`, **all open, none merged** | Verified, wording corrected |
| RedisLite: 75K+ ops/sec, sub-ms P95 | Built the server, ran `go run benchmark.go -clients 10 -commands 1000 -mix 30` over TCP | README records 74,498 ops/sec at 0.20ms P95; reran on a cloud VM and got 185,917 ops/sec at 0.10ms P95 | Verified and conservative |
| RedisLite: test suite passes | `go test ./...` | Passes, 11 cases across `parser_test.go` and `store_test.go` | Verified |
| JusticeQueue: 13-step pipeline, 8 decisions per run | Read `README.md` | Both explicitly documented | Verified |
| JusticeQueue: 60-case audit, 32 improved, +6 avg score, 4 tier upgrades | Read `README.md` | Documented with methodology | Verified |
| PRBeliefs: test suite | `python3 -m pytest --asyncio-mode=auto` in `Dhruva-Aher/ReviewAgent` | `30 passed` | Verified — and was previously **not** mentioned on the site at all |
| DRRGT: 3,200+ U.S. counties | Read `backend/app/etl/pipeline.py` | Present in batch-upsert code; matches the real US county count | Verified |
| Live demos reachable | HTTP request to each | `justicequeuelive.vercel.app`, `aurasys.vercel.app`, `github.com/apps/prbeliefs`, `dhruvaaher.dev` all return 200 | Verified |
| FlowBoard: multi-tenant, JWT + refresh, RBAC, WebSockets + Redis pub/sub, Celery, async SQLAlchemy | Read `README.md` | All match; no numeric claims to check | Verified |

### Claims that failed verification and what they became

| Original claim | How it was checked | What was actually found | Now reads |
| --- | --- | --- | --- |
| Receipts: "19/19 passing agent verification tests" | `node --test server/pipeline/pipeline.test.mjs` | `15 passed, 0 failed`. There is exactly one test file in the repo — 19 was not reachable by any counting | **15 passing tests**, with the command quoted |
| Aura: "automated crash recovery restoring 6,000+ tasks in <2 seconds" | Searched the entire repo for any recorded benchmark | No such measurement exists anywhere in the repository | **Removed entirely** |
| Aura: "20,000+ concurrent task orchestrator" | Read `README.md` and `apps/worker` load-test config | `npm run load-test` *pushes* 20,000 jobs through the API. That is a load-test configuration, not a measured concurrency ceiling | **"Load-tested at 20,000 jobs"**, and the card now leads with the lease/reaper/reconciler design |
| DRRGT: "810K+ records analyzed" | Searched the entire repo | No evidence at all | **Removed**; the verified 3,200+ counties stays |
| PRBeliefs: "<1s automated AI code reviews" | Searched for a benchmark artifact | README says "sub-second review latency (LLM via Groq)" but there is no measurement behind it | Restated as a **design target**, not a metric |
| "Upstreamed into DataHub's own skills repo" | Checked state of all three submissions | All three are **open**; the PR is not merged. "Upstreamed" implies acceptance | **"Proposed upstream"**, with all three links on the card and their open state stated |

The three DataHub submissions, for direct inspection:

- [datahub-skills#136](https://github.com/datahub-project/datahub-skills/issues/136) — proposal for a
  `datahub-ml-leakage` skill doing FineGrainedLineage target-leakage checks on MLModel deploy gates. **Open.**
- [datahub-skills#137](https://github.com/datahub-project/datahub-skills/pull/137) — the implementation PR. **Open, not merged.**
- [datahub#19060](https://github.com/datahub-project/datahub/issues/19060) — Core API issue requesting
  batch-fetch of schemaField aspects (tags/terms) for FineGrainedLineage policy walks. **Open.**

---

## 2. Per-project deep dives

### UnderWrite — fail-closed ML deployment gate

**Problem.** A model can be trained on a feature that is derived, somewhere upstream, from the label
it is supposed to predict. The model then looks excellent offline and fails in production. By the
time anyone notices, it is deployed. The leakage is visible in column-level lineage, but nobody
reads lineage graphs by hand before a deploy.

**Design and why.** Five stages — Acquisition, Normalization, Traversal, Evaluation, Verdict — that
walk DataHub's column-level lineage from the model's input features back toward the label column and
block the deploy if a path exists. The decision that matters is a graph reachability question, and
graph reachability is deterministic, so the verdict path is deterministic code. The LLM is deliberately
scoped out of it: it runs only *after* a block, to explain the offending path and suggest a remediation.
It has no route to producing an approval.

**Tradeoff accepted.** Fail-closed means an unreachable DataHub instance blocks the deploy instead of
waving it through. That converts a metadata-service outage into a deploy outage, which is annoying and
will generate complaints. I took it deliberately: the failure mode of fail-open is a leaked model in
production that nobody flagged, and that is strictly worse and much harder to detect. The tradeoff is
written down in `ARCHITECTURAL_TRADEOFFS.md` rather than left implicit.

**Failure modes.** Lineage that DataHub does not know about is lineage the gate cannot see — leakage
through an untracked join or a hand-built feature file passes silently. This is a false-negative risk,
not a false-positive one. Overly coarse lineage produces false positives and blocks safe deploys, which
is the direction I would rather err in.

**Where it breaks.** Lineage traversal fans out, and each hop currently costs API calls to fetch
schemaField aspects one at a time. On a wide graph that is slow enough to matter in a deploy gate.
That is precisely why I filed the Core API issue upstream — the fix belongs in DataHub's API, not in a
workaround on my side.

**What I would do differently.** Cache normalized lineage subgraphs between runs keyed by dataset
version, so repeat deploys of the same model do not re-walk an unchanged graph. I would also want a
recorded false-positive rate against a real deployment history before arguing anyone should enable this
in blocking mode; right now the argument for the gate is structural, not empirical.

---

### RedisLite — Redis-compatible store in Go

**Problem.** Self-imposed. I wanted to understand what is actually underneath a key-value store rather
than take one as a given, so the rule was that nothing outside the standard library does any of the
interesting work.

**Design and why.** About 978 lines of Go. The RESP protocol parser is written from scratch — no
library — because parsing the wire format *is* the exercise. The server is goroutine-per-connection,
which is the idiomatic Go answer and is fine at this scale: goroutines are cheap and the code stays
readable, versus an event loop that would be faster under very high connection counts and much harder
to follow. State lives in a map behind a `sync.RWMutex`. Expiry is a background sweeper on a 100ms
tick rather than checking every key on every access. Durability is an append-only file replayed at
startup.

**Measurement.** 74,498 ops/sec at 0.20ms P95 on my machine; 185,917 ops/sec at 0.10ms P95 when I
reran the identical benchmark on a cloud VM. Both come from
`go run benchmark.go -clients 10 -commands 1000 -mix 30`. The site says 75K+ because that is the
number I can point at on hardware I control — the figure is hardware-dependent and I state it that way.

**Tradeoff accepted.** One global `RWMutex` over one map. It is simple, it is obviously correct, and
it is the throughput ceiling.

**Where it breaks.** Write contention. Reads share the lock happily; writes serialize completely, so
adding cores past a point buys nothing on a write-heavy mix. The fix is sharding the store into an
array of maps with per-shard locks, so independent keys stop contending. This limit is named in the
repo's own README — I would rather an interviewer read it there first than discover it themselves.

**What I would do differently.** Shard the store, add pipelining so a client can have multiple commands
in flight instead of paying a round trip each, and benchmark against real `redis-benchmark` rather than
my own harness so the comparison is not self-graded.

---

### Aura — lease-based distributed job orchestrator

**Problem.** A job queue where a worker dying mid-job means the job is silently lost is not a job
queue. The hard part is not distributing work, it is guaranteeing that work claimed by a process that
then disappears comes back.

**Design and why.** Workers claim jobs with `ZPOPMAX` against a Redis sorted set, which gives priority
ordering for free. A claimed job goes into `aura:leased`, scored at `now + lease_duration`. A Reaper
loop scans for leases whose score is in the past and re-enqueues them. A lease is a deadline rather
than a lock, so a dead worker's job returns automatically once the deadline passes, with no need for
anything to detect the death.

PostgreSQL is the durable source of truth and Redis is the fast path. Redis can be flushed or evict
under memory pressure, and if Redis were authoritative that would be data loss. Instead a Reconciler
rebuilds Redis state from Postgres. Exactly one scheduler runs at a time via leader election on
`aura:scheduler:lock` using Redis `SET NX EX` with a 15s TTL, so a dead leader's lock expires rather
than deadlocking the system.

Overload is handled explicitly: adaptive backpressure returns HTTP 429 instead of accepting work the
system cannot execute, workers heartbeat with a 30s timeout, repeatedly failing jobs land in a DLQ,
and SLOs are tracked. Full write-ups are in `docs/` — `crash-recovery.md`, `lease-protocol.md`,
`redis-postgres-interaction.md`, `retry-dlq.md`, `scheduler-lifecycle.md`, `worker-lifecycle.md`.

**Tradeoff accepted.** At-least-once delivery, not exactly-once. Re-enqueueing an expired lease means
a job whose worker was merely slow — not dead — can run twice. Exactly-once across a queue and a
worker's side effects is not achievable without distributed transactions, so the honest move is to make
retries safe rather than pretend they cannot happen, which is what the idempotency fences are for.

**Failure modes.** A lease shorter than the real job duration causes duplicate execution under load,
because slow workers get reaped. Too long, and a genuinely dead worker's job sits idle until the
deadline. This is a tuning parameter with real consequences in both directions, not a default to leave
alone. Clock skew between workers and the reaper shifts the effective deadline.

**Evidence.** `npx vitest run` in `apps/worker` passes **223 tests across 14 suites** (run
`npx prisma generate` first, or two suites fail on an uninitialized Prisma client). That includes
`SchedulerLock.test.ts`, which models `SET NX EX` semantics precisely and walks the full lifecycle:
a leader dies, its TTL expires, and a follower takes over. The claim, retry, and promote paths are
atomic Redis Lua scripts in `packages/redis/src/lua.ts`, where retry backoff is
`min(2^(attempts-1) × 1000ms, 60000ms)`.

**Where it breaks, and what I do not claim.** The load test harness supports five scenarios — burst,
steady, mixed, priority-storm, failure-flood — and reports P50/P95/P99, but **no measured results are
committed to the repository**, so I quote no throughput number for Aura. I also have no chaos-tested
proof of the recovery guarantees against a real cluster: the leader-election lifecycle is verified
against a faithful in-memory Redis fake, not against Redis under partition. Killing workers under load
and measuring actual recovery time is the obvious next step. Until then the crash-recovery story is a
design argument backed by 223 tests, which is how I present it.

---

### JusticeQueue — AI legal triage pipeline

**Problem.** Legal aid intake queues are triaged by hand, and urgency is not the same thing as arrival
order.

**Design and why.** A 13-step pipeline in which Gemini Flash makes 8 decisions per run about tool
selection and resource allocation, with MongoDB Atlas Vector Search retrieving comparable prior cases
to inform prioritization. Retrieval matters here specifically because a case's urgency is best judged
relative to cases that resemble it.

**Evidence.** Audited on 60 live cases: 32 improved (53%), average priority score up 6 points, 4 cases
upgraded into the critical tier, all attributable to vector-search retrieval.

**Scope, stated honestly.** This is model-directed execution inside a predefined graph, not autonomous
planning from scratch. The model picks paths through a structure I wrote; it does not invent the
structure. The `/judge` page is static mock data and the README says so. I would rather say this first
than have someone find it.

**Where it breaks.** The 60-case audit is small, and I graded it. It shows the retrieval step helps;
it is not evidence of production-grade triage accuracy, and a real evaluation needs a held-out set
scored by someone who is not me.

---

### Receipts — agent claim verification

**Problem.** A coding agent reports that it finished. Sometimes it did not. Checking means reading the
diff and rerunning things by hand, which is exactly the work the agent was supposed to remove.

**Design and why.** The pipeline takes an agent's completion claim and tests it against the live repo:
extract the claims, run the commands they imply, inspect the git diff, and emit a MERGE / FIX /
ESCALATE verdict. Built at OpenAI Build Week with React, Node.js, the Codex CLI, and GPT-5.6.

**Evidence.** 15 passing pipeline tests via `node --test server/pipeline/pipeline.test.mjs`. A
`lied-test-run` fixture reproduces a false agent claim on demand, so the failure case is a fixture
rather than a story. Transcripts are frozen in `proofs/`. Stage timings were captured on 17 Jul 2026:
Codex claim extraction 9,876ms, command verification 214ms, git-diff inspection 61ms, receipt export
1ms, 10,152ms end-to-end.

**Tradeoff and honest scope.** The README is explicit that this does not reinvent CI. CI tells you
whether the tests pass; this tells you whether what the agent *said* it did matches what it did. Those
overlap but are not the same question.

**Where it breaks.** 97% of the end-to-end time is the Codex claim-extraction call — the verification
work itself is under 300ms. The system is bounded almost entirely by one LLM round trip, so any
optimization that is not aimed at that call is wasted effort.

---

### PRBeliefs — GitHub App for AI code review

**Problem.** Small PRs sit waiting for a reviewer who is busy, and the feedback that eventually
arrives is often mechanical enough to have been automated.

**Design and why.** A real, installable GitHub App. Webhook ingestion is decoupled behind a Redis
queue so a burst of PR events cannot block or drop on the webhook handler — GitHub expects a fast
response, and doing review work inline would fail that. Review agents run in parallel via
`asyncio.gather` against Groq-hosted inference, because the agents are independent and the latency is
dominated by inference round trips. ~2,226 lines of Python, deployed with Docker Compose.

**Evidence.** 30 passing tests via `python3 -m pytest --asyncio-mode=auto`.

**What I do not claim.** The README mentions sub-second review latency and the site used to present
that as a metric. There is no benchmark artifact behind it, so it is now stated as a design target.
The architecture is built for low latency; I have not measured the end-to-end number and will not
quote one until I have.

---

### Disaster Relief Response Gap Tracker

**Problem.** Federal disaster aid is slower to reach some counties than others, and the raw federal
data does not make that comparison for you.

**Design and why.** A Celery-scheduled ETL pulling OpenFEMA and Census APIs with pagination and
exponential backoff, joined on FIPS codes, batch-upserted across 3,200+ US counties. The analysis
deliberately reduces to one auditable metric — response gap days, declaration date to obligation date —
because a composite index would be more impressive and far less defensible. Counties are compared only
against peers: same rural/urban class, population within ±25%, median income within ±25%. Quintiles are
precomputed so API reads are O(1) off cache instead of aggregating per request. Infrastructure is
Terraform-managed AWS.

**Honest caveats.** Without a `CENSUS_API_KEY` the pipeline falls back to a hardcoded 20-county demo
sample, so a casual cloner is not seeing the full dataset. The "810K+ records" figure that used to be
on the site had no support in the repository and has been removed.

**Where it breaks.** Obligation date is a proxy for aid arriving, not the same thing — money obligated
is not money spent. The metric is defensible as a measure of administrative response speed and should
not be oversold as a measure of relief actually delivered.

---

## 3. Anticipated questions

### UnderWrite

**"Isn't this just an LLM wrapper?"**
No, and the architecture is arranged specifically to make that answer verifiable. The authorization
decision is deterministic graph traversal over column-level lineage. The LLM is invoked only after a
block has already been decided, to explain the leakage path and suggest a fix. There is no code path
by which the model produces an approval. If you delete the LLM, the gate still works and still blocks
correctly; you just lose the remediation text.

**"Your DataHub PR isn't merged."**
Correct — all three submissions are open. The sequence was: file the proposal, implement it, and in
implementing it hit a Core API gap where fetching schemaField aspects one at a time makes lineage
walks too slow for a deploy gate, so file that as a separate issue against DataHub core. Getting a
skill accepted into a project like DataHub is not on my schedule. What I can defend is that the work
is real, it is public under my name on the official org, and you can read the code and the review
discussion yourself.

**"What if DataHub is down?"**
The deploy is blocked. That is intentional and it is the whole design. I would rather explain a blocked
deploy during an outage than explain a leaked model that shipped because the gate silently gave up.

**"How do you know it catches real leakage?"**
It catches leakage that appears in DataHub's lineage. It cannot see what lineage does not capture, and
I do not have a measured false-negative rate against a real deployment history. That is the honest
limit of the current evidence.

### RedisLite

**"75K ops/sec — real Redis does far more. Why is yours slower?"**
Three reasons, all of which I can point to in the code. One global `RWMutex` serializes every write,
so writes do not scale with cores. There is no pipelining, so each command costs a full round trip.
There is no sharding. Redis also has years of hand-tuned C, an event loop instead of goroutine-per-
connection, and optimized data structures. I was not trying to beat Redis; I was trying to understand
it, and the point of the exercise is that I can tell you exactly which of those gaps costs what.

**"What would you fix first?"**
Sharding the store into an array of maps with per-shard locks. Write contention is the binding
constraint, so it is the only change that raises the ceiling rather than shaving the constant.

**"Your benchmark numbers differ by 2.5x between machines."**
Yes — 74,498 ops/sec on my machine, 185,917 on a cloud VM, same command. That is why the site frames
the number as measured-on-specific-hardware and publishes the command. A throughput number without
hardware and a reproduction command is not a claim, it is decoration.

**"Is it actually Redis-compatible?"**
It speaks RESP, which I implemented from the spec, so a RESP client can talk to it for the command
subset I implemented. It is not a drop-in replacement and I do not claim command coverage parity.

### Aura

**"How do you know your job queue doesn't lose jobs?"**
The structural argument: Postgres is the durable source of truth, so a job that was accepted is
recorded durably before Redis ever sees it, and the Reconciler rebuilds Redis from Postgres after a
flush or eviction. Leases are deadlines, so a job claimed by a worker that dies is re-enqueued by the
Reaper once the deadline passes. But I want to be precise — that is a design argument supported by
code, not a chaos-tested proof. I have not killed workers under load and measured recovery. Until I
do, "does not lose jobs" is what the design intends, not something I have demonstrated.

**"At-least-once or exactly-once?"**
At-least-once. Exactly-once across a queue and a worker's external side effects is not achievable
without distributed transactions across both. So jobs can run twice — a slow worker gets reaped and
its job re-enqueued — and the answer is idempotency fences so that a second execution is safe rather
than pretending duplicates cannot occur.

**"Two schedulers start at once. What happens?"**
One wins `SET NX EX` on `aura:scheduler:lock` and the other backs off. The 15s TTL means a leader that
dies holding the lock releases it by expiry rather than deadlocking. The real risk is the classic one:
a leader that stalls past the TTL without dying can still believe it is the leader while another has
taken over. Redis-based leader election is not a consensus protocol, and if I needed a real guarantee
I would use one — etcd or Raft — rather than pretend a TTL is equivalent.

**"You said 20,000 concurrent tasks."**
I no longer do. The load test pushes 20,000 jobs through the API; that is a configuration I ran, not a
measured concurrency ceiling, and I corrected the site to say so. The claim about crash recovery
restoring 6,000 tasks in under two seconds was removed outright because there is no measurement behind
it anywhere in the repo.

### JusticeQueue

**"Is this an autonomous agent?"**
No. It is model-directed execution within a predefined graph — the model chooses among paths I
defined, it does not plan from scratch. The README says this and so do I.

**"Your audit is 60 cases and you graded it."**
Correct on both counts. It is evidence that retrieval improved prioritization on this sample, not a
production accuracy claim. A real evaluation needs a larger held-out set graded by someone with domain
expertise who is not the author.

**"Does the whole demo work?"**
Most of it. The `/judge` page is static mock data and is labeled as such in the repo. I would rather
tell you that up front than have you click it.

### Receipts

**"How is this different from CI?"**
CI answers whether the tests pass. This answers whether the agent's description of what it did matches
what actually changed in the repo. An agent can produce a green build and still have not done the
thing it claimed. The README is explicit that this does not replace CI.

**"How do you know it catches a lying agent?"**
There is a `lied-test-run` fixture that reproduces a false claim on demand, and the transcripts are
frozen in `proofs/`. So it is a rerunnable case, not an anecdote.

**"Ten seconds end-to-end is slow."**
It is, and I know exactly where it goes: 9,876ms of the 10,152ms is the Codex claim-extraction call.
The verification stages total under 300ms. Any real speedup has to come from that one call — a smaller
model for extraction, or caching — and optimizing anything else would be pointless.

### PRBeliefs

**"You claimed sub-second reviews."**
The README describes sub-second review latency and the site presented it as a measurement. It was not
one — there is no benchmark artifact — so I changed it to a design target. What I can defend is the
architecture behind the intent: parallel agents via `asyncio.gather`, and webhook ingestion decoupled
behind Redis so bursts do not block the handler. What I can measure is the test suite: 30 passing.

**"Why queue the webhooks instead of reviewing inline?"**
GitHub expects a fast webhook response, and LLM review is slow. Doing it inline means timing out on
GitHub's side and dropping events under burst. The queue converts a burst into a backlog, which is
the failure mode I want.

### General

**"Which of these would you rewrite?"**
RedisLite, and I would start with the lock. Everything else about it I would keep, including
goroutine-per-connection, because the readability is worth more than the throughput at this scale.

**"What's the hardest bug you hit?"**
The Core API gap in UnderWrite is the most instructive one, because the bug was not in my code. Lineage
traversal was too slow for a deploy gate, and the cause was needing one API call per schemaField
aspect. Fixing it on my side would have meant a workaround; the actual fix belongs in DataHub's API,
which is why it became an upstream issue rather than a local hack.

**"What did you get wrong on this site?"**
Several numbers. The next section lists them.

---

## 4. Honesty ledger — what I removed

These claims were on the portfolio and are not any more, because I could not substantiate them:

- **"Automated crash recovery restoring 6,000+ tasks in <2 seconds" (Aura)** — no recorded measurement
  exists anywhere in the repository. Removed entirely rather than softened.
- **"810K+ records analyzed" (DRRGT)** — no evidence in the repo. Removed. The verified 3,200+ counties
  stayed.
- **"19/19 passing tests" (Receipts)** — the actual count is 15, from the repository's single test file.
  Corrected downward.
- **"20,000+ concurrent task orchestrator" (Aura)** — 20,000 is the load-test job count, not a measured
  concurrency ceiling. Reframed as "load-tested at 20,000 jobs".
- **"<1s automated AI code reviews" (PRBeliefs)** — no benchmark artifact. Demoted from metric to design
  target.
- **"Upstreamed into DataHub's own skills repo"** — the submissions are real but open, not merged.
  "Upstreamed" implied acceptance it has not received. Changed to "proposed upstream", with all three
  links and their open state visible on the card.

Nothing was added to compensate. What replaced these numbers is design detail that is already in the
repositories and can be checked by reading them.

Every remaining number on the site has a command behind it in section 1. That is the point of the
exercise: the claims got smaller, and all of them now survive being checked.
