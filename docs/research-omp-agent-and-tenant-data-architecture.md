# Agent Flow + Multi-Tenant User-Scoped Data Architecture (customer/privacy lens)

Owner: `omp-research-2` · Date: 2026-09-26 · Task: two design assignments, no code.
Locked user decisions honored: single SQLite instance (no Postgres) · two files (`state.db` + `checkpoints.db`) · custom SQLite auth (users + sessions) · memory = sqlite-vec + FTS5 behind a `MemoryStore` interface (Instinct recommendation, being locked) · Notion = system of record + admin surface.
Compared against LB-02 throughout; conflicts flagged at the end. Staged inputs OK, fabricated outputs never. Unsourced claims `[INFERENCE]`.

---

## PART 1 — Agent flow + states data architecture

### 1.1 State schema per LangGraph node

One row per node visit in `node_visits` (not just terminal states — the receipt needs the path):

| Node | State written | Key fields |
|---|---|---|
| `observe` | raw event normalized | `event_id`, platform payload refs, `occurred_at`, dedupe key |
| `classify` | 12 deterministic signals + versions | `signal_runs(event_id, signal_version, result, evidence, freshness)`; UNKNOWNs explicit |
| `gate` | Jev verdicts + band | `decisions(event_id, policy_version, gate_version, model_id, prompt_version, verdict, reason_code, confidence)` |
| `escalate` | mod-queue card | `mod_queue(event_id, card_payload, state=pending, reviewer NULL)` |
| `resolve` | human verdict or auto-action | card state → approved/rejected/undone + `admin_id` + timestamp; or `action_intents` row for auto path |
| `learn` | override record + checkpoint proposal | `overrides(...)`; nightly job proposes `threshold_versions` candidate |

States per event: `received → signals_ready → context_ready → decided → approval_pending | action_pending | no_action → action_inflight → action_confirmed | action_unknown | action_failed → recorded → learning_candidate`. Matches LB-02 §2 + Instinct architecture brief.

### 1.2 Records per concern

- **Transitions:** `event_transitions(event_id, from_state, to_state, occurred_at, reason_code)` — append-only; the audit spine.
- **Decisions/confidence/reasons:** `decisions` rows carry verdict + one-line reason + confidence + all versions (policy/gate/model/prompt). Confidence stored from day one even before thresholds are tuned.
- **Signal runs:** versioned per signal; replay = re-run same bundle version against frozen cases.
- **Outbox/action intents:** `action_intents` with UNIQUE idempotency key `(tenant, event, action_type, target, policy_version)`; commit intent BEFORE any external call; status tracks inflight/confirmed/unknown/failed.
- **Overrides:** human verdicts with reason codes; distinguish "draft approved" from "harmful action undone" (different labels, per Instinct).
- **Threshold versions:** immutable rows; pointer-switch activation; every decision logs the version it ran under.
- **Checkpoints:** LangGraph SqliteSaver in `checkpoints.db` (separate file — graph resume state, not business data).

### 1.3 Persistence: two files

- **`state.db` (WAL, 0600, single writer):** events, transitions, decisions, intents, queue, overrides, thresholds, token usage, memory metadata rows. The business ledger.
- **`checkpoints.db`:** LangGraph checkpoints only. Disposable in the worst case (rebuildable by replaying `event_transitions`); `state.db` is not.
- **Why two:** checkpoint writes are high-frequency and bulky; mixing them into the ledger bloats backups and risks lock contention with the decision path. Separation is a failure-domain boundary, not just tidiness.

### 1.4 Replay / resume

- **Resume after crash:** worker claims leased rows; `action_inflight` without vendor evidence → `action_unknown` → reconcile (platform readback + Swytchcode audit ref) before retry; never blind re-issue.
- **Replay a decision:** `event + config version + policy version + gate version + model version` reconstructs it exactly (LB-02 §2 rule, kept).
- **Replay a policy candidate:** frozen labeled cases (4 tuning / 4 holdout split) re-run under the candidate bundle; 2×2 before/after (missed harmful, benign escalated, review load, unsafe auto-actions); promote only on measured improvement + admin approval + rollback pointer.
- **Memory recall in replay:** recall is time-travel safe only if memories carry effective-time ranges; otherwise replay uses the *current* memory with a logged caveat. State this on the receipt when it applies `[INFERENCE: design choice, confirm in build]`.

---

## PART 2 — Multi-tenant, user-scoped project data architecture

P2 need (agent runs first) BUT the DB is shaped for it from day one — no migration later. User decisions: single SQLite instance, custom SQLite auth (users + sessions table, not platform SSO), every table tenant/user-keyed.

### 2.1 Key scheme

- Every member-data table carries `community_id` AND `user_id` (the acting/admin user where relevant; the member where the row is about a member — column named explicitly: `member_id` vs `admin_user_id`, never bare `user_id` doing double duty).
- `users(id PK, handle, auth_subject, created_at)` + `sessions(token_hash PK, user_id, community_id, expires_at)` — custom SQLite auth per the locked decision. Tokens stored as hashes; rotation + revocation rows, not deletes.
- Global tables (no tenant key): versioned definition bundles only (`policy_bundles`, `signal_bundles`) — no member data, ever (LB-02 §6.5 item 10, kept).

### 2.2 Single access module

- All reads/writes go through one `access.py`; raw `sqlite3.connect` anywhere else fails a grep test in CI. The module injects `community_id` + `user_id` filters; there is no unscoped query path.
- Console/API reads through the module only — never the file. Backup/migration/test tooling is enumerated in the access story (my LB-02 review follow-up, kept).

### 2.3 Isolation tests (must exist before first real data)

1. Cross-community read returns empty (seed two communities, read across — assert zero rows).
2. Cross-user read returns denied/empty (two users, same community, scoped rows).
3. Digest contains no handles (adversarial handle included — "5 members" style).
4. Confusable/leet staff-name variants only ever DRAFT, never auto-block.
5. Projection isolation: Notion DB/workspace per community, scoped integration — test covers projections, not just SQLite.

### 2.4 Export / delete path

- Per-community export: config + changelog + reports + override history as one JSON bundle (secrets excluded by construction — referenced by name only).
- Full purge: delete container rows + redact event rows for the subject + tombstone row (tombstones re-applied on restore so backups forget too). Purge is itself an audit event.
- Portable learned-config: versioned JSON (`schema_version`, thresholds, label weights, admin overrides by pattern hash, model + prompt version) — travels with its memories via `pattern_hash` references, no ID collisions.

### 2.5 Memory under the new decision

sqlite-vec + FTS5 in the same `state.db` file behind the `MemoryStore` interface (`remember`/`recall`/`forget`, normalized scores, shared adapter tests) — per Instinct's recommendation, being locked. Consequences for my earlier supermemory docs: the containerTag story becomes `community_id`-filtered vec tables; dreaming/graph semantics (Updates/Extends/Derives) are replaced by our own override rows + nightly recompute; auto-forgetting becomes retention jobs. The UX narrative ("learned / changed my mind / retired") is unchanged — only the engine behind it moves. My supermemory docs stay as history; this doc is the build input if the lock lands.

---

## Conflicts with LB-02 (flagged, not resolved — sketch owner decides)

1. **Memory engine:** LB-02 §1/§4 say supermemory (cloud or self-host); user decision now points at sqlite-vec + FTS5. If locked, LB-02 needs a memory-row update (vec tables replace containers; scoped keys become access-module filters).
2. **Checkpoints file:** LB-02 implies one SQLite file; this doc splits `state.db` + `checkpoints.db` per the user's two-file decision. Minor, but backup/restore procedures must cover both.
3. **Auth:** LB-02 session-4 says "site auth links Telegram identity"; this doc specifies custom SQLite users + sessions tables. Compatible if the table design is what's meant — confirm the sketch owner reads it that way.
4. **Record store:** LB-02 §7.6 locks Notion; my §2 tables assume SQLite-first with Notion as projection mirror. No conflict if "system of record" means human-facing record — but the demo must never imply Notion is the transaction log (outbox ledger is).
5. No conflicts on: redaction-before-write, 0600 + single writer, override state machine, two render paths, per-platform undo, key-loss matrix, retention windows, no-fake-work.
