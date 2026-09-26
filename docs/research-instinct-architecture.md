# Beadle Architecture (Instinct) — Single-Community Design

Date: 2026-09-26 · Source: email 67978. Design proposal, not a claim that vendor APIs already provide these primitives.

## Recommendation

**One Python/FastAPI process + one local SQLite DB on the laptop for the demo.** One Telegram ingress path first; Discord as a separate adapter only if needed. LangGraph graph, signal calculations, provider clients, execution broker, worker, and a read-only SSE console are **modules in one repo, not services**. Webhook validates → commits a minimal event → ACKs fast → a leased worker advances it. **Do not make Airtable/Notion/supermemory/Swytchcode the canonical transaction log.**

**Ownership boundaries:** vendor owns actual message/moderation state; local DB owns *what Beadle received, intended, attempted, observed, learned*; Swytchcode owns its policy/audit result (copied by reference); supermemory = retrieval index, not ledger; Airtable/Notion = human projections (their outage must not undo a decision); provider text = evidence/draft, never authority. **Neither a Swytchcode success nor an HTTP 200 proves a platform mutation until vendor response/readback confirms it.**

At ~100 communities: split stateless ingress/API + durable queue/workers/scheduler; move events/outbox/checkpoints to managed Postgres; `tenant_id` in every key/query; per-tenant quotas. Discord Gateway is a long-running WebSocket (heartbeat/resume) → separate its worker at deployment time.

## Event state machine & recovery

Append-only `event_transitions` + materialized `events.state`:
`received → signals_ready → context_ready → decided → approval_pending | action_pending | no_action → action_inflight → action_confirmed | action_unknown | action_failed → recorded → learning_candidate`.
- No path from failed/unknown → confirmed without vendor evidence.
- `approval_pending` resumes only on same event/policy version with recorded reviewer; if source deleted or policy changed → re-evaluate.
- Explicit `needs_attention` for missing context/parser failure/exhausted retries.
- Learning is asynchronous; never a prerequisite for a response.

**Schema (illustrative):** `inbox_events` (PK id; tenant/platform/external_event_id unique; payload_hash; state; lease_until; attempt_count) · `normalized_events` · `signal_runs` (PK event_id+signal_version) · `decisions` (policy/model/prompt versions, context refs, verdict, reason) · `action_intents` (idempotency_key UNIQUE, swytchcode_ref, platform_ref, attempts, last_error) · `event_transitions` · `job_runs` (PK job_type+tenant+period_key).

**Ingress:** insert payload hash + event row, then ACK; duplicate key → success without second action. Telegram `update_id` = duplicate/out-of-order key (undelivered updates held ≤24h upstream). Discord: stable message ID + event type + Gateway sequence/session for resume. Store minimum normalized input for replay (hash alone can't reconstruct a crashed job).

**Worker:** claim due row with short lease → versioned signals → context with timeout → decision → **commit outbox intent before any external call** → execute → reconcile. On restart: reconcile platform target + Swytchcode audit ref before retry; if no reliable idempotency/readback → human review (never promise exactly-once). Idempotency key = `(tenant, event, action_type, target, policy_version)`; **never a new key on retry**. LangGraph persistent checkpointer; interrupted nodes restart from their beginning → external writes live behind the outbox, never ahead of an interrupt.

**Scheduler:** nightly key `(tenant, date, job_kind)`; weekly `(tenant, ISO week, job_kind)`; scheduler enqueues, worker owns the lease; high-water mark + source coverage window so the digest marks gaps instead of faking a complete week. `learning_candidate` stores reviewer override + evidence pointers; human-approved policy changes are versioned → replayed → explicitly activated.

## Deployment

| Option | Fit / caveat |
|---|---|
| **Laptop + FastAPI + ngrok + disk SQLite** | Fastest live demo; tunnel URL + laptop uptime are failure domains; one writer; back up via SQLite online backup API, not a blind copy of a live WAL DB |
| **Cloud Run service + scheduled job** | Good later for stateless webhook/API + jobs; **container FS is ephemeral — local SQLite is not durable**; SSE needs `Last-Event-ID` replay from durable DB; don't run a forever-loop as a request service; external DB/queue needed |
| **Cloudflare Workers + Containers/Durable Objects** | Worker = thin ingress; Containers' disk is ephemeral, DO SQLite persists separately; not tonight |

Discord Gateway needs a separately supervised long-lived process. Telegram: webhook **or** polling, never both.

## Data homes & retention (proposed defaults — decide with community owners)

| Data class | Home now | Proposed retention / later |
|---|---|---|
| Telegram/Discord IDs + content | local DB: IDs, timestamps, hash + minimal encrypted content | raw 7d; derived event/audit 90d; purge on request (audit exception); per-tenant keys later |
| Bot tokens / webhook secrets | untracked env/OS secret store; never DB/git/console/mail/traces | rotate on exposure; cloud secret manager + workload identity later |
| Signals, Jev decisions, approvals | local versioned rows + reason codes + source refs; bounded evidence, not full transcript | 90d initially; access audit; per-tenant retention later |
| Model calls (Groq/Gemini) | minimal model/prompt/token/latency/redacted decision; task-relevant snippets only | discard full prompt/output after ~24h debugging window; assess provider terms first |
| Supermemory | approved scoped facts + tenant namespace + source pointer; no creds/raw dumps | 30–90d or source-linked; verify real delete/export API before claiming guarantees |
| Swytchcode | intent/result ID, request hash, outcome, vendor audit ref; no tokens | 90d local; vendor retention/idempotency needs live contract check |
| Airtable/Notion | projections only: aggregates + redacted reasons + local decision IDs | delete/update when source deleted; verify trash/backups + workspace access; Notion ~3 req/s + 429/529 |
| Console/SSE + telemetry | authenticated read-only console, ID cursor, redacted JSON, correlation IDs | 7–14d ops logs; no payloads in access logs; export/delete later |
| SQLite + backups | private path, OS full-disk encryption, restrictive perms; tested nightly online backup to encrypted volume | managed encrypted Postgres + per-tenant policy later; backups forget too |

**Delete flow:** subject aliases → pause queued actions → delete/minimize local content + derived memories/projections → request vendor deletion where supported → tombstone + outcome without reintroducing deleted content on replay/backups. Don't promise external deletion timing before vendor APIs are verified.

## Failure drills (must pass before claiming reliability)

Duplicate/reordered webhook → one row, one intent · crash after intent commit → retry same intent · crash after call before response → `action_unknown`, reconcile, never blindly re-issue · Swytchcode denied → no platform call; unavailable → approval queue, not silent bypass · retrieval/model slow → cached vetted context or draft-only escalation · SQLite busy → short transactions, `busy_timeout`, no network/model inside a transaction · SSE disconnect → reconnect with last committed event ID · scheduler overlap → one job per period_key, stuck lease reclaimed · tunnel/offline laptop → health check + backlog alarm (Telegram holds ≤24h) · privacy → no token/raw prompt in logs/Notion; subject delete across DB+memory+projection; restore backup + reapply tombstones.

## Five decisions to lock before coding

1. **First ingress:** Telegram webhook only, or Discord Gateway only for the live path? (Don't build both before the first end-to-end run; confirm actual bot permissions/events.)
2. **Allowed actions:** exact Swytchcode action names/parameters, dry-run vs real mutation, which may auto-execute and who approves others. Until verified → broker is draft-only.
3. **Source & retention:** what community content may be stored, who sees the console, the 7/90-day windows, and which facts may go to supermemory/Notion/Airtable — an owner-facing privacy decision before real member content flows.
4. **Durability & hosting:** laptop + encrypted on-disk SQLite + tested backup for the demo, or cloud with managed DB/queue? Never SQLite-ledger on Cloud Run's ephemeral FS.
5. **Failure promise:** fail-closed behavior + an alert owner for `action_unknown`, missing events, provider exhaustion, stale digests; demonstrate duplicate delivery + crash-after-send tests.

**Unverified edges (explicit checks, not mocked guarantees):** Swytchcode execution/idempotency/audit contract · Jev interface · supermemory deletion behavior · cloud quotas/costs · community consent/retention terms.
