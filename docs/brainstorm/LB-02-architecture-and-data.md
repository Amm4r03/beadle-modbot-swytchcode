# LB-02 — App Architecture & Data Storage: how Beadle runs and where everything lives

> **Status: LIVING DOC — open brainstorm. Stage 0. Last worked 2026-09-26.**
> Started from the user's ask: plan vendor-specific data storage (simple now, encrypted later at scale) and a solid app architecture; all three seats research and note ideas. This note is **edited in place**; it is **not a spec, not a sprint plan, not a decision.**
>
> **Companions.** `docs/T3-PROJECT.md` · `docs/brainstorm/LB-01-product-and-delivery.md` · `docs/research-omp-supermemory.md` · `docs/research-deepseek-supermemory.md` · `docs/research-instinct-policy-competition-names.md` · `docs/research-instinct-learning-and-pitch.md`.

---

## 0. The question this answers

**How does Beadle run end-to-end, and where does every piece of data live — today (simple, free) and at scale (encrypted, multi-tenant)?**

> **Draft answer:** a single Python service (LangGraph orchestrator + deterministic signal engine + Jev decision layer + Swytchcode execution broker) with SQLite for operational state, supermemory for learned memory, Airtable for human-facing records, and Groq/Gemini for generation — all behind one console with SSE. Encrypted-at-rest, scoped keys, and secret management arrive when we go multi-tenant, not before.

---

## 0.5 Where this stands

| | |
|---|---|
| **Stage** | 0 — brainstorm |
| **Gate to stage 1** | architecture confirmed; storage homes locked; top decisions resolved |
| **Settled so far** | component sketch (§1), data flow (§2), vendor data table (§3), simple-vs-scaled storage (§4) |
| **Open so far** | 6 top decisions (§7) |
| **Independent of the decision** | Swytchcode action names, signals design, policy schema, token budgets |
| **Blocked on** | record-store choice (Airtable vs Notion), supermemory mode (cloud vs self-host), planner keys |

---

## 1. Component architecture (draft)

| Component | Responsibility | In-process now | Separate at scale |
|---|---|---|---|
| **Intake** | Normalize Telegram/Discord events into one `Event` shape (platform, community, channel, author, text, meta, ts) | yes (webhook/poll loop) | yes (queue) |
| **Orchestrator** | LangGraph nodes: load config → signals → retrieve → Jev → bands → act/escalate → record | yes | yes (per-community workers) |
| **Signal engine** | Pure deterministic functions (account age, handle similarity, URL/wallet regex, unanswered age…) | yes | yes |
| **Decision layer (Jev)** | Typed questions from policy statements → probabilities/confidence | API call | API call |
| **Execution broker (Swytchcode)** | `tooling.json` allowlist; `swy exec` writes; audit; idempotency; exit codes | CLI subprocess | same |
| **Memory (sqlite-vec + FTS5)** | Per-community rows: norms, FAQ, member facts, override outcomes | same `state.db` file, behind `MemoryStore` | same |
| **Record store (Airtable/Notion)** | Reports, escalation log, policy changelog, ledger (human-facing) | API | same |
| **Generation (Groq → Gemini)** | Drafts, digests, summaries; OpenAI-compatible base-URL swap; token-budgeted | API calls | same |
| **Operational DB (SQLite)** | Events, decisions, audit refs, queue, seen cursors, threshold versions, token usage | local file (WAL) | Postgres + encrypted volume |
| **Console (FastAPI + SSE)** | Reasoning stream, policy history, report archive, approvals, settings | same process | separate service |
| **Scheduler** | Nightly checkpoints, weekly digest, escalation cadences, token resets | APScheduler in-process | cron/queue |
| **Secrets** | Vendor tokens + API keys | `.env` (git-ignored) | OS keychain → KMS/secret manager; scoped per community |

**Failure domains:** intake (vendor outages), Jev (latency/errors → fail closed), Swytchcode (auth/policy), memory (latency → degrade to policy-only), generation (rate limits → provider fallback), SQLite (locks → single writer discipline), console (SSE drops → reconnect).

## 2. Data flow / state machine (per event)

`received → signals → retrieved → decided → executed | escalated → recorded → learned`
- **Durable at each step:** event row (idempotency key), signals fired + thresholds, retrieved refs, Jev question/answer/probability, band decision, exec audit ref, escalation ticket, override outcome.
- **Replay:** any decision reconstructable from `event + config version + policy version + gate version + model version`.
- **Sources of truth:** vendor platforms own their messages; **we own** decisions/audit/overrides; Airtable owns the human-readable report; Swytchcode owns execution audit.

## 3. Vendor data table (draft)

| Vendor | Data | Sensitivity | Home now | Retention |
|---|---|---|---|---|
| Telegram | bot token; chat/message/author IDs; text; ts | token = secret; text may contain PII | token `.env`; IDs+text in SQLite; decisions logged | events 30–90d; decisions/audit keep |
| Discord | bot token; guild/channel/message/author IDs; content; roles | same | same | same |
| Airtable (or Notion) | PAT; base/table/record IDs; report/policy rows | PAT = secret; rows admin-readable | PAT `.env`; rows in Airtable | keep (report archive) |
| Resend | API key; sent metadata (to/subject/id/status); templates | key = secret; recipient emails = PII | key `.env`; metadata in SQLite | metadata 90d |
| Jev | API key; question/answer/probability logs | key = secret; scores = decision data | key `.env`; logs SQLite | keep (audit) |
| Trends | API key; cached snapshots | low | key `.env`; cache files/SQLite | cache 7d |
| Memory store (sqlite-vec + FTS5) | memories/docs scoped by `community_id` | may contain member facts | same `state.db` | per policy; forget/delete via `MemoryStore.forget` |
| Local SQLite | events, decisions, audit refs, queue, thresholds, token usage | mixed | `data/state.db` | per table policy |

**Principles:** single source of truth per data type; store IDs/references not copies; PII minimized (handles are facts; DM contents quarantined, never ingested); tokens never logged; every table has a retention rule.

## 4. Storage: simple now → encrypted/scaled later

- **Now (hackathon):** **two SQLite files** — `state.db` (WAL: events, decisions, audit, queue, thresholds, token usage, memory vec tables) + `checkpoints.db` (LangGraph SqliteSaver only; disposable/rebuildable) + JSONL logs + Notion projection; secrets in `.env`; single writer; daily backup = online backup of both files. Auth = custom SQLite `users` + `sessions` (hashed tokens, rotation/revocation rows) linking Telegram identity.
- **Later (serious scale):** SQLCipher or encrypted volume for the DB; per-community scoped API keys; KMS/secret manager (no `.env` in prod); PII redaction pipeline; retention automation; export/delete endpoints; encrypted backups; multi-tenant isolation tests; audit export.
- **Explicitly deferred:** Postgres, queues, microservices, KMS, SSO — only when load or tenancy demands.

## 5. Deployment options

- **Now:** single local process (worker + console + scheduler) under `caffeinate`, tunnel via ngrok; SQLite local.
- **Next:** worker on a small always-on host (Cloud Run container / Fly / Render) + console on Vercel/Cloud Run + webhooks on the same host; SQLite → mounted volume or Postgres when multi-tenant.
- **Cloudflare:** Workers fit webhooks/console edge but not the long-running Python worker; Containers could host it later.
- **What changes at 100 communities:** per-community workers/queues, Postgres, scoped keys, KMS, rate-limit budgets per tenant.

## 6. Failure & scale guardrails

| Breaks first | Guardrail |
|---|---|
| Vendor rate limits | per-provider token buckets, backoff, provider fallback (Groq→Gemini) |
| SQLite locks | single-writer discipline, WAL, short transactions, queue table |
| SSE disconnects | auto-reconnect + poll fallback (bridge pattern proven) |
| Scheduler overlap | idempotent jobs + last-run markers |
| Token budget | per-workflow budgets + semantic cache + retrieval not stuffing |
| Memory latency | memory is enrichment; policy-only fallback path |
| Secret leakage | tokens only in `.env`/keychain; redaction in logs |

## 6.5 Privacy & architecture fixes (O37 dispositions — all accepted)

1. **PII boundary before write:** redaction happens at intake, *before* the SQLite write; raw text stored once in the event row with redaction metadata; redaction rules versioned; on rule updates a re-scan job runs with an audit note.
2. **SQLite access story:** file perms 0600, single process (worker) is sole writer/reader; **console reads through the API only** — no raw SQL/file access; encrypted volume later.
3. **Isolation below the app layer:** every table row carries `community_id`; every query filters by it; a test asserts cross-community reads return empty; console views scoped. One missing WHERE clause defeats container isolation.
4. **Override queue persistence:** SQLite `overrides` table with a state machine (`pending → approved/rejected/undone`), restart-safe; supermemory mirrors outcomes. The gate of record is ours, never in-memory only.
5. **Two render paths from one event store:** member-facing digest (aggregates, no handles) vs mod-facing report (handles + patterns); templates versioned; a test asserts the digest contains no handles.
6. **Undo mechanics per platform:** undo table per action type with adapters — Telegram delete/restrict, Discord delete + role restore, Slack delete + correction post. **If the platform cannot execute the undo, the action may not auto-execute.**
7. **Key-loss degradation matrix:** Jev key → gate fails closed (draft-only); bot token → intake/writes halt + operator alert; Groq → drafts queue; Gemini → approved fallback; record store (Notion) → records queue locally; memory store → policy-only fallback. **No silent fallbacks that look like intelligence.**

**O46 conflict dispositions (accepted):**
- **C1 Memory engine:** LB-02 memory rows updated to sqlite-vec + FTS5 behind `MemoryStore` (supermemory dropped; containers → `community_id` filters; dreaming semantics → override rows + nightly recompute; forgetting → retention jobs).
- **C2 Two files:** `state.db` + `checkpoints.db` confirmed; backup/restore procedures cover both; checkpoints are disposable (rebuildable from `event_transitions`), `state.db` is not.
- **C3 Auth:** LB-02's "site auth links Telegram identity" = custom SQLite `users` + `sessions` tables (hashed tokens, rotation/revocation rows); no external SSO.
- **C4 Record store:** Notion = **human-facing system of record + admin surface (projection)**; the **transaction log is the SQLite outbox ledger**. The demo must never imply Notion is the transaction log.

**O39 follow-ups (accepted, specified):**

8. **PII event-row model:** event row stores the **redacted content + content_ref pointer**; raw content lives only in a short-lived encrypted blob (7-day TTL) when replay requires it. Redaction rules are versioned; a rule update re-scans only within the raw TTL window — historical rows stay immutable with their redaction-rule version recorded on the receipt. (Mutable raw blob, immutable redacted row, versioned rules.)
9. **Backup & migration tooling:** nightly SQLite **online backup API** to an encrypted volume (never a blind copy of a live WAL file); numbered SQL migrations with `PRAGMA user_version`; documented restore drill; backup TTL ≤ live retention; tombstones re-applied after restore; console never touches the file.
10. **Global-table carve-outs:** only versioned definition bundles (`policy_bundles`, `signal_bundles` — no member data) are global; every member-data table carries `tenant_id` and every query filters. Projections inherit the same discipline: one Notion database/workspace per community, integration scoped per community, and the isolation test covers projections too.
11. **Adversarial-handle test + undo SLA:** test that confusable/leet staff-name variants only ever produce DRAFT (never auto-block); undo SLA = attempt within 5 minutes of approval; failed undo → `action_unknown` + human alert; the alert channel is tied to the key-loss matrix (§6.5 item 7).

## 7. Open questions (top decisions to lock before building)

Consolidated with Instinct's architecture brief (`docs/research-instinct-architecture.md`):

1. **First ingress:** Telegram webhook only, or Discord Gateway only for the live path? (No both before first end-to-end; confirm bot permissions/events.)
2. **Allowed actions:** exact Swytchcode action names/params, dry-run vs real mutation, what may auto-execute, who approves the rest. Until verified → broker is draft-only.
3. **Source & retention:** what member content may be stored; who sees the console; the 7-day raw / 90-day derived windows; which facts may go to supermemory/projections. Owner-facing privacy decision before real member content.
4. **Durability & hosting:** laptop + encrypted on-disk SQLite + tested backup for the demo (recommended), or cloud with managed DB/queue. Never SQLite-ledger on Cloud Run's ephemeral FS.
5. **Failure promise:** fail-closed behavior + alert owner for `action_unknown`, missing events, provider exhaustion, stale digests; demo duplicate delivery + crash-after-send tests.
6. **Record store: LOCKED — Notion** (system of record + admin surface: events ledger, quarantine queue, member trust history, 90-day pattern view; also the demo surface). Airtable no longer needed.
7. **Memory layer (resolved direction):** **sqlite-vec + FTS5 in `state.db` behind a `MemoryStore` interface** (remember/recall/forget; local `fastembed` embeddings) — supermemory **dropped** (258MB server + LLM extraction duplicates Jev); Neo4j rejected (JVM server, overkill); LanceDB/Neo4j documented later swaps. Portable learned-config JSON per community (thresholds, label weights, admin overrides, pattern_hash refs, model/prompt versions). Full doc: `docs/research-instinct-memory-layer.md`.
8. **Planner keys:** Groq primary + Gemini fallback (user creates free keys; validated live before use).
9. **Console stack:** **Svelte web front** doubling as auth surface and per-community telemetry dashboard (per session-4 decision); FastAPI + SSE backend.
10. **Secrets path:** `.env` now → keychain/KMS later; no secrets in repo/docs/logs.
11. **Data plane (session 4, revised):** **single SQLite instance (WAL) — no Postgres** (user, 2026-09-26); single writer; separate LangGraph checkpoint file; scoping enforced by the single access module (`user_id`/`community_id` on every row, all reads through `access.py`); no Supabase; ngrok exposure.
12. **Retention (confirmed):** raw 7d + derived 90d.

## 8. What this is NOT

- Not the final architecture doc (that comes after stage 0 closes).
- Not a microservices plan; single process until load demands otherwise.
- Not a data-warehouse design; we store references, not copies.
- Not a security audit; encryption/KMS are explicitly later.

## 9. Discussion log

- **2026-09-26 — session 1.** Drafted from the user's ask; omp tasked with vendor-data storage + architecture dial-in; Instinct tasked with the architecture/storage/deployment brief. Component sketch, data flow, vendor table, simple-vs-scaled storage, deployment options, guardrails, six decisions.

## Sources

- User instruction (chat, 2026-09-26): storage simple now/encrypted later; architecture research from all three seats.
- Prior docs: LB-01, T3-PROJECT, supermemory studies, policy schema, token-efficiency brief (in flight).

## Revision log

- **2026-09-26** — Created.
