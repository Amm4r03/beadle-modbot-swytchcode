# Best-Fitting Tech Stack Per Stage (customer + build lens)

Owner: `omp-research-2` · Date: 2026-09-26 · Task: stack-per-stage vs EPIC-SPINE.md, compared against TECH-STACK.md.
Constraints: free tier only, no paid deps, boring reliable picks, one-day build. Web search throttled mid-write (first 3 queries sourced, rest from TECH-STACK + prior verified docs); choices below reuse already-locked stack where set, new picks tagged `[NEW]`.
Rule: staged inputs OK, fabricated outputs never.

---

## E1 — Ingress: thin Telegram + Discord bots

| Stage | Options | Pick | Why | Risk |
|---|---|---|---|---|
| Telegram listen | (a) `python-telegram-bot` v21 polling, (b) raw Bot API `getUpdates` loop, (c) Swytchcode-only ingress | **(a) `python-telegram-bot` v21, polling** | Asyncio-native since v20 ([docs](https://docs.python-telegram-bot.org/en/v21.9/telegram.ext.updater.html)); Updater handles polling/queue/retry so the 2s metric is free; Swytchcode stays the *execution* path (answer/delete via verified actions), not the listen path | Webhook would be "purer" but polling removes ngrok-webhook debugging from the critical path; switch port later |
| Telegram act | (a) Swytchcode `sendmessage`/`deletemessage` actions, (b) direct Bot API calls | **(a) Swytchcode actions** | Verified action names on disk; audit refs + exit codes feed the receipt story; keeps the 30% integration weight honest | If an action ID drifts, fallback is direct Bot API with the same event shape — adapter boundary isolates the swap |
| Discord listen/act | (a) `discord.py` 2.x with Message Content Intent, (b) raw gateway websocket | **(a) `discord.py` 2.x** | Intent-gated content access is documented and standard (`message_content=True` + portal toggle — [SO](https://stackoverflow.com/questions/71967975/discord-py-on-message-no-content)); sane rate-limit handling built in | Intent must be enabled in the dev portal or content arrives empty — first-5-min checklist item, not a code risk |
| Event normalization | (a) per-platform dicts, (b) one pydantic `Event` | **(b) one pydantic `Event`** | Zero gate-engine changes for Discord (spine requirement) only holds if the shape is enforced at the boundary; pydantic rejects drift loudly | Schema churn mid-day breaks both adapters — freeze the shape at 10:45, version it |

## E2 — Gate engine: LangGraph + Jev

| Stage | Options | Pick | Why | Risk |
|---|---|---|---|---|
| Graph | (a) LangGraph ≥0.2, (b) hand-rolled state machine | **(a) LangGraph** (locked in TECH-STACK) | Judging expects an agentic framework; conditional edges make output-influences-next-action explicit (framework matrix conclusion) | Graph boilerplate costs ~30 min — pay it once at 10:45, not per node |
| Checkpointer | (a) `langgraph-checkpoint-sqlite` SqliteSaver, (b) in-memory | **(a) SqliteSaver** ([PyPI](https://pypi.org/project/langgraph-checkpoint-sqlite/), [docs](https://docs.langchain.com/oss/python/langgraph/persistence)) | Crash-after-send reconciliation + deterministic replay need durable checkpoints; same SQLite file as ops DB keeps one durability story | Set `LANGGRAPH_STRICT_MSGPACK=true` per the security note; keep checkpoint DB separate from ops tables to avoid lock contention |
| Jev client | (a) typesafe SDK if exists, (b) raw `httpx` POST | **(b) raw `httpx` POST** | No verified typesafe Python SDK on disk; `httpx` is already in requirements; typed request/response via pydantic at our boundary | Hand-rolled client must pin model version string + log it per decision — make it a 20-line module, not inline calls |
| Groq/Gemini client | (a) `openai` SDK with base-URL swap, (b) per-provider SDKs | **(a) `openai` SDK base-URL swap** | Both Groq (`api.groq.com/openai/v1`) and Gemini document OpenAI-compatible endpoints — one client, provider = config; matches token playbook's adapter contract | Base-URL swap hides provider quirks (429 shapes differ) — normalize errors at the adapter, never leak provider exceptions upstream |
| Transition logging | (a) JSONL transitions table mirror, (b) LangGraph checkpoints only | **(a) both: checkpoints + `event_transitions` rows** | Checkpoints resume; rows render (receipts, trust ramp, replay need queryable history, not checkpoint blobs) | Double-write must be in one transaction or receipts can disagree with state — write row first, checkpoint second |

## E3 — Admin surface: Notion as system of record

| Stage | Options | Pick | Why | Risk |
|---|---|---|---|---|
| Notion writes | (a) `notion-sdk-py`, (b) Swytchcode notion actions only | **(a) `notion-sdk-py` for writes, Swytchcode actions where they add audit** | Direct SDK = predictable latency for the 5s ledger metric; Swytchcode path kept for the demo's audit-receipt beat (one showcased write, not every write) | Two write paths must produce identical page shapes — define the page template once, both paths render it |
| Ledger schema | (a) one DB per view, (b) single events DB + filtered views | **(b) single events DB + filtered views** | One write, four views (ledger/queue/trust/patterns); quarantine resolve = status flip on the same row, writeback guaranteed structurally | Notion API ~3 req/s — batch ledger writes, never one call per event field; queue + flush on a 2s ticker |
| Rate limits | (a) naive retry, (b) token bucket + `Retry-After` | **(b) bucket + Retry-After** | Demo load (split decision + report) can burst past 3 req/s; naive retry 429-spirals on stage | Pre-create pages (ledger DB, queue DB) the night before — zero schema calls during the demo window |

## E4 — Identity + data security

| Stage | Options | Pick | Why | Risk |
|---|---|---|---|---|
| Site auth | (a) signed-cookie sessions (`itsdangerous`), (b) JWT | **(a) sessions** `[NEW]` | Single laptop, single admin, no multi-service audience — sessions are a cookie + server secret, no key rotation/token-revocation story to build in 45 min | Sessions don't port to multi-service later — acceptable; the swap is documented as a later decision, not today's work |
| Access module | (a) one `access.py` all reads funnel through, (b) per-module queries | **(a) one module** | The demo line ("every read goes through one access path") must be structurally true, not a convention — a single module makes the cross-user test meaningful | Every new query must import it — add a lint rule (grep test) that fails on raw `sqlite3.connect` outside the module |
| `user_id` propagation | (a) explicit param threading, (b) contextvar | **(a) explicit param** | Boring, greppable, reviewable in a one-day build; contextvars hide flow exactly where the audit needs it visible | Verbose signatures — accept it; the explicitness IS the audit story |
| RLS-ready notes | (a) Postgres policy file, (b) one-page notes doc | **(b) one-page notes** | Spine asks for notes "under one page" — a policy file for a DB we don't run is fake work | Notes must name the exact tables + policies, not "we'll add RLS later" hand-waving |
| ngrok exposure | (a) ngrok tunnel to FastAPI, (b) Tailscale/peer VPN | **(a) ngrok** | Already proven by the bridge (200 local + public verified); auth on every route, token-gated SSE | Tunnel URL + laptop uptime are failure domains — state both in the README; backup video covers tunnel death |

## E5 — Web front: minimal Svelte

| Stage | Options | Pick | Why | Risk |
|---|---|---|---|---|
| Framework | (a) Svelte 5 + Vite, (b) plain HTML/SSE | **(a) Svelte 5 + Vite** | Locked direction in LB-01 session 3 ("small Svelte site"); component-per-view (auth, counters, quarantine) beats string-built HTML by 15:00 | Vite dev port + ngrok = two moving parts — build static (`vite build`, serve `dist/`) by 16:00, never demo off the dev server |
| SSE client | (a) native `EventSource` + `Last-Event-ID`, (b) polling | **(a) `EventSource`** | Bridge already proves the pattern (live.js + reconnect); `Last-Event-ID` replay from the durable cursor is the disconnect story | Reconnect storms on flaky venue wifi — exponential backoff + a manual refresh button, always |
| Counters | (a) hand-rolled numbers, (b) chart lib | **(a) hand-rolled** | Spine bans chart libs; four live counts + trust-ramp line as plain numbers carry the demo | Numbers must come from derived views, never raw queries — stale-number failure signal is a data bug, not a UI bug |

## Cross-cutting

| Area | Pick | Why | Risk |
|---|---|---|---|
| Scheduler | **APScheduler in-process** (locked) | Nightly checkpoint + weekly digest + cadences with idempotent period keys; zero infra | In-process dies with the laptop — acceptable for demo; cron/queue later |
| Testing | **pytest** (locked) | Per-story harness, frozen replay cases, isolation + adversarial-handle + duplicate/crash drills | Tests must run offline (no live keys in CI) — fixture inputs, real code paths, honestly-labeled asserts |
| Lint/format/types | **ruff + pydantic everywhere** (locked) | Typed boundaries catch event-shape drift before stage does | Run `ruff check` in the 16:30 dry run — a red lint at 16:55 is a choice, not a surprise |
| Logging | **structured JSONL, redacted, correlation IDs** (locked) | Receipts + debugging without PII/token leakage | Redaction must be tested (assert no `sk-`, no token, no raw DM in a sample log) |
| Secrets | **untracked `.env`** (locked) | Names in `.env.example`, values never in repo/docs/mail | Rotate everything the night before; verify `git status` clean of `.env` |

---

## Locked stack summary (one page)

Python 3.11 · LangGraph (SqliteSaver checkpoints) · Jev via `httpx` (pinned model, logged) · Groq→Gemini via `openai`-SDK base-URL swap · Swytchcode CLI for writes that need audit · `python-telegram-bot` v21 polling + `discord.py` 2.x (Message Content Intent) → one pydantic `Event` · FastAPI + SSE console · Svelte 5 static build · SQLite WAL (0600, single writer, `community_id`/`user_id` everywhere) + JSONL · `notion-sdk-py` (single events DB + views) · Resend test sender · supermemory (self-host first) · trendsapi.ai + HN Algolia cached · APScheduler · pytest · ruff + pydantic · JSONL redacted logs · `.env` secrets · local + ngrok.

## Conflicts with TECH-STACK.md

**None material.** This doc pins versions/choices where TECH-STACK is silent (PTB polling over webhook, `httpx` over SDK, sessions over JWT, Svelte static over dev server, single events DB) — all compatible, no contradictions. Two additions proposed for TECH-STACK: (1) `python-telegram-bot`, `discord.py`, `notion-sdk-py`, `openai`, `apscheduler` to requirements (currently only langgraph/fastapi/uvicorn/httpx/yaml/dotenv); (2) the `LANGGRAPH_STRICT_MSGPACK=true` env note. Notion-vs-Airtable is settled here as Notion (matches TECH-STACK's "locked" line).
