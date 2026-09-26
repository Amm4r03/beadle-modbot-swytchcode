# Tech Stack & Engineering Style — Beadle (T3)

> **LOCKED 2026-09-26** (user approved locking; per-stage pins from `docs/research-omp-stack-per-stage.md`). Nothing is implemented yet; this is the stack we build against once cascade stage 4 completes.

## Per-stage pins (from omp's stack research)

| Stage | Pick |
|---|---|
| Telegram listen | `python-telegram-bot` v21, polling (Updater handles retry; webhook swap later) |
| Telegram act | Swytchcode `sendmessage`/`deletemessage` actions (audit refs); direct Bot API fallback behind the adapter |
| Discord | `discord.py` 2.x, Message Content Intent enabled (portal checklist item) |
| Event shape | One pydantic `Event` enforced at the boundary (zero gate-engine changes for Discord) |
| Graph | LangGraph ≥0.2 + **`langgraph-checkpoint-sqlite` SqliteSaver** (separate DB from ops tables; `LANGGRAPH_STRICT_MSGPACK=true`) |
| Jev client | Raw `httpx` module (pinned model string logged per decision); typed via pydantic |
| Generation client | `openai` SDK with base-URL swap (Groq primary → Gemini fallback); errors normalized in the adapter |
| Transition logging | Checkpoints (resume) + `event_transitions` rows (render/receipts); row first, checkpoint second, one transaction |
| Notion writes | `notion-sdk-py` for ledger writes + Swytchcode Notion action for the showcased audit write; one page template for both paths |
| Notion schema | Single events DB + filtered views (ledger/queue/trust/patterns); resolve = status flip; batch writes, 2s flush ticker, `Retry-After` handling |
| Site auth | Signed-cookie sessions (`itsdangerous`) — single laptop/single admin |
| Access module | One `access.py`; all reads funnel through it; a grep test fails on raw `sqlite3.connect` outside it; explicit `user_id` param threading |
| RLS notes | **Not applicable — no Postgres planned.** One-page scoping note: `user_id` on every table + all reads via `access.py`; enforced by code, never claimed as DB-enforced |
| Front | Svelte 5 + Vite, **static build served from `dist/`** by demo time; `EventSource` + `Last-Event-ID` replay with backoff; hand-rolled counters only |
| Scheduler | APScheduler in-process, idempotent period keys |
| Testing | pytest, offline (no live keys in CI), fixture inputs → real code paths |
| Lint/types | ruff + pydantic everywhere; `ruff check` in the 16:30 dry run |
| Logging | Structured JSONL, redacted, correlation IDs; redaction tested (no keys/tokens/raw DMs) |
| Secrets | Untracked `.env` (names in `.env.example`); rotate the night before |

**Additions to `requirements.txt`:** `python-telegram-bot`, `discord.py`, `notion-sdk-py`, `openai`, `apscheduler`, `sqlite-vec`, `fastembed` (+ `langgraph-checkpoint-sqlite`).

## Stack

| Layer | Choice | Notes |
|---|---|---|
| Language | **Python 3.11** | matches pyenv present; LangGraph/FastAPI ecosystem |
| Agent framework | **LangGraph** (locked) | one shared state machine: `observe → classify → gate → escalate → resolve → learn`; thin bots over it |
| Decision layer | **Jev** (TypeSafe direct, `JEV_API_KEY`) | model pinned (`jev-1.13.0`); typed questions from policy statements; one-line reason per state switch; cannot plan, only judges |
| Generation | **Groq `gpt-oss-120b` primary → Gemini `flash-lite` fallback** | OpenAI-compatible client with base-URL swap; token budgets per the playbook; only for bounded drafts/synthesis/policy wording |
| Execution | **Swytchcode CLI** (`swy exec`, JSON stdin) behind a thin adapter | `tooling.json` allowlist; audit refs; exit codes; free tier (no Pro); blocked action shown via `--dry-run` exit 4, labeled honestly |
| Bots | **Telegram** (bot token, admin in group) + **Discord** (bot token, Message Content Intent) | thin adapters: normalize events in, post actions out |
| Memory | **sqlite-vec + SQLite FTS5** in `state.db`, behind a `MemoryStore` interface (remember/recall/forget; embeddings via local `fastembed`) | supermemory **dropped** (258MB server + LLM extraction duplicates Jev); Neo4j rejected (JVM server, overkill); LanceDB/Neo4j are the documented later swaps |
| Record store | **Notion** (locked) | system of record + admin surface: events ledger, quarantine queue, member trust history, 90-day pattern view; also the demo surface |
| Digest | **Resend** (free 100/day) | weekly digest + escalation summaries; test sender for demo |
| Trends | **trendsapi.ai** (free 100 req/mo) + **HN Algolia** (free) | cached weekly; never live on stage |
| Operational DB | **SQLite (WAL), single instance — no Postgres** | single writer; separate checkpoint file for LangGraph; `community_id`/`user_id` on every row; scoping enforced by the single access module (no DB-enforced RLS claims) |
| API / console | **FastAPI + SSE** backend, **Svelte** front | Svelte doubles as auth surface + per-community telemetry + quarantine queue view |
| Scheduler | in-process (APScheduler) | nightly checkpoint, weekly digest, escalation cadences; idempotent period keys |
| Testing | **pytest** | per-story harness (staged inputs → real code paths); frozen replay cases; isolation test; adversarial-handle test; duplicate/crash-after-send drills |
| Lint/format/types | **ruff** (+ format), type hints, pydantic schemas | typed SQL and pydantic models for every boundary |
| Logging | structured JSONL, redacted, correlation IDs | no tokens/raw prompts/PII in logs |
| Secrets | untracked `.env` now → KMS/secret manager later | never in repo/docs/mailboxes |
| Deployment | local + ngrok now; Cloud Run/Fly later; Vercel/Cloudflare for the console later | no SQLite on ephemeral filesystems |
| Repo | public GitHub (submission requirement) | README, architecture diagram, setup instructions, demo |

## Engineering style

1. **Cascade docs-first.** No implementation until stage 4 completes and the user explicitly starts the build.
2. **No fake work.** Staged inputs OK; fabricated outputs never. Blocked → ask the user. Demo honesty lines always available.
3. **Deterministic first.** Signals → Jev judgment → deterministic reducer → policy bands; the LLM only drafts/synthesizes. The agent decides; the model never causes a side effect alone.
4. **Outbox before external write.** Idempotency key `(tenant, event, action_type, target, policy_version)`; reconcile before retry; no HTTP 200 treated as proof of a platform mutation.
5. **Version everything.** Policy, signal bundle, gate thresholds, model, prompt — recorded on every decision receipt; rollback is atomic.
6. **Fail closed.** Jev unavailable → DRAFT, never AUTO; no silent fallbacks; key-loss matrix honored.
7. **Small modules, one repo, one process** at demo scale; split only when load demands.
8. **Observable acceptance criteria.** Every story names the state, input, and expected output; metrics are method+scope labeled.
9. **Privacy by construction.** Raw 7d / derived 90d; redaction before write; per-community isolation with a test; undo capability required for any auto-action.
10. **File ownership + comms** per `AGENTS.md` / `docs/agent-comms.md`.

## Open stack items (user)
- supermemory mode: self-host (recommended) vs cloud free tier.
- Groq key (+ optional Gemini key) to validate live.
- Console scope confirm (reasoning stream + report + policy history + quarantine queue).
