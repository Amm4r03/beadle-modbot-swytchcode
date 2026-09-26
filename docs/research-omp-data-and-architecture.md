# Vendor Data Storage + Architecture Dial-In (customer/privacy lens)

Owner: `omp-research-2` · Date: 2026-09-26 · Task: brainstorm-phase research, no code.
Inputs: LB-01 sessions 1–3 (packaging CONFIRMED: bot; policy path FREE; guardrail model NL-text + value bands via Jev; planner key from user; Jev live-verified jev-1.13.0/scam-0.96), AGENTS.md non-negotiables, my metrics/learning doc, supermemory UX doc, competition/testing doc (filed). LB-02 not yet on disk — §5 below is pre-LB-02 input, not a review of it.
Rule: staged inputs OK, fabricated outputs never. Unsourced claims `[INFERENCE]`.

---

## 1. Vendor-by-vendor data map

| Vendor | Data we hold | Where it lives | Sensitivity | Retention | Who reads it |
|---|---|---|---|---|---|
| Telegram | bot token; chat/message/author IDs; message text; timestamps | token: env/secret store only; messages: SQLite events + JSONL | **High** (token = full bot control; texts = member speech) | events 90d rolling; raw texts 30d, then aggregates only `[INFERENCE: proposal]` | agent worker; admin via console/report |
| Discord | guild/channel/message/author IDs; content; roles; audit entries | same as Telegram | **High** (same reasons + voice/stage metadata if ever touched — don't touch) | same as Telegram | same |
| Notion | integration token; page/block/record IDs; report + policy rows; changelog | token: secret store; IDs in SQLite (not copies of content); content lives in Notion | **Medium** (our own artifacts; no member PII beyond handles) | reports indefinite (they're the product); drafts 30d | admin (owns the pages); agent worker (read/write) |
| Resend | API key; sent metadata (to/message-id/status); templates | key: secret store; metadata: SQLite; templates in repo | **Medium** (email addresses = PII) | metadata 1yr (billing disputes) `[INFERENCE]`; bodies 30d | agent worker; admin via digest archive |
| Jev | API key; per-call logs (question text, answer, probability, model version, latency) | key: secret store; logs: SQLite (never in Notion_SUP — no member text in gate logs) | **Medium** (questions may quote message fragments — redact before logging) | 1yr (calibration evidence) | agent worker; admin via gate-history view |
| Trends | API key; cached snapshots (keyword, scores, timestamp) | key: secret store; snapshots: SQLite/JSON | **Low** (public data) | cache 30d, then re-fetch | agent worker |
| Supermemory | memories + docs per community containerTag; override records | supermemory (cloud or self-host); Notion mirrors changelog in human language | **High** (derived beliefs about members) | per policy: ephemeral facts auto-forget; overrides kept 1yr; purge on community exit | agent worker (scoped keys); admin (review queue) |
| Local SQLite | events, decisions, audit trail, mod queue, threshold versions, token-usage counters | encrypted volume (later) / local file (now, git-ignored) | **Highest** (the join of everything — IDs that tie stores together) | audit 1yr; events 90d; queue items until resolved +30d | agent worker; no direct admin access (only via console views) |

### Principles (binding)

1. **Single source of truth per fact:** message text lives in SQLite once; Notion/Supermemory hold IDs + derivations, never second copies of raw text.
2. **IDs, not copies:** cross-store references are `(community_id, message_id, policy_version)` tuples. If a store is purged, the others degrade to dangling IDs, not leaked copies.
3. **PII minimization:** handles where needed for function; wallet addresses, emails, DM contents never enter memories or logs — quarantine metadata only.
4. **No tokens in logs, ever:** secret values never appear in SQLite, JSONL, Notion, console output, or screenshots. Log `key_present: true/false`, never the key.
5. **No member text in gate logs:** Jev call logs record question *templates* + scores, with message fragments redacted. The full text lives once, in the event row.

## 2. Storage design: now vs later

### NOW (hackathon + first deployment)

- **SQLite** (single file, git-ignored, WAL mode): `events`, `decisions`, `audit`, `mod_queue`, `threshold_versions`, `token_usage`, `override_history`. Schema migrations as numbered SQL files in repo.
- **JSONL** append-only event log beside it (crash-safe intake; replay source).
- **Notion**: human-readable mirrors only (reports, changelog, policy history) — built from SQLite, never written first.
- **Supermemory**: long-term beliefs + lorebook, per-community containerTag, scoped keys.
- Secrets: env file, never committed; `.env.example` documents names only.

### LATER (post-hackathon hardening)

- **Encryption at rest:** SQLCipher (or encrypted volume) for the SQLite file — the whole file is the crown jewels.
- **Per-community scoped keys** for supermemory + per-tenant secret namespaces; KMS/secret-manager (Cloud Run Secret Manager / equivalent) instead of env files.
- **PII redaction pipeline** at intake: fingerprints + patterns scrubbed before storage, with a redaction log (what rule fired, not the value).
- **Retention jobs:** scheduled purges per the table above; "delete my data" = purge container + redact event rows for that member, logged as an audit event itself.
- **Export/delete:** one-click per-community export (config + changelog + reports) and full purge; leaving costs tuned thresholds, never data hostage (competition doc §1).
- **Backups:** encrypted nightly snapshot, tested restore; backup retention ≤ live retention (backups must forget too).

## 3. Cross-platform config (companion to metrics-doc §3)

Schema proposal already filed in metrics doc (thresholds, ladder, cadences, tone, policies, adapter section). Additions from this pass:

- **Secrets are NOT in config:** the YAML holds thresholds and behavior; tokens/keys live only in the secret store, referenced by name (`telegram_bot_token_ref: env:TELEGRAM_BOT_TOKEN`). A config export never leaks a credential.
- **Porting checklist (Telegram ⇄ Discord ⇄ Slack):** copy judgment layer verbatim → swap `platform_adapter` → re-seed community examples (lures differ per platform culture) → reset trust ramp to draft-only → run the staged-pair acceptance (the §4 harness below) before any live write.

## 4. Local testing strategy (mock → private → real)

- **Harness per story** (answer / escalate / scam / report / digest / learning): staged inputs drive real code paths; PASS criteria already defined in competition/testing doc §2. With Jev now live-verified, the gate stories run against the real scorer — no replay path needed for scoring (replay survives only as *expected-route assertions* on fixture inputs, labeled as such).
- **Staged test servers per platform:** private Telegram group + bot (primary); Discord staged server (adapter proof); Slack test workspace (#mod-queue format asserts); Notion shared test pages (check sharing first — 404s are the classic false failure); Resend test sender to our own inboxes.
- **Transition rule:** mock (tonight, fixtures, backup video) → private friends' group read-only report first, writes only after sane → real with trust ramp from draft-only. The first live false quarantine must happen where forgiveness exists.
- **What "pass" means:** defined per story in the testing doc; plus the global gate — no story passes on a fabricated output, only on a live call or an honestly-labeled expected-route assert.

## 5. Architecture dial-in: customer/privacy holes in the LB-01 direction (pre-LB-02 input)

LB-02 isn't on disk yet, so these are holes against the LB-01 session-3 settled direction + my own earlier docs, for the sketch to answer:

1. **Where does the PII boundary sit in the pipeline?** The sketch must show the redaction point *before* SQLite write, not after — otherwise every downstream store inherits raw text and §1's minimization is aspirational. Ask: which component owns redaction, and what happens to in-flight data on rule updates?
2. **Who can read the SQLite file?** It's the join of everything (§1: highest sensitivity). The sketch needs an access story: file perms, which processes mount it, and why the console reads through an API, never the file. A console with raw SQL access is a breach waiting for a screenshot.
3. **Per-community isolation below the app layer?** Container tags isolate memory, but SQLite rows and Notion pages need the same discipline: every table row carries `community_id`, every query filters by it, and there's a test that proves cross-community reads return empty. One missing WHERE clause defeats the container story.
4. **Override queue is the gate of record — where does it persist?** My metrics doc says our own queue, not supermemory's review API. The sketch must place it: SQLite table with state machine (pending → approved/rejected/undone), supermemory mirrors outcomes. If it lives only in memory, a restart loses the learning loop.
5. **Digest/report rendering must not leak quarantine details.** The member-facing digest and the mod-facing report are different documents with different redaction levels (member sees "1 scam stopped," mod sees the handle + pattern). The sketch should show two render paths from one event store, or someone will paste the wrong one.
6. **Undo path end-to-end (not just undo weight).** Metrics doc pins weights; the sketch must show the un-ban/un-send mechanics per platform (Telegram revoke vs Discord delete vs Slack delete + correction post) — an undo the platform can't execute is a broken promise.

---

## 6. Review of LB-02 §6.5 (folding my §5 in — O37 dispositions accepted)

Read LB-02 §6.5 against each of my 7 holes. Verdict: all 7 addressed; 4 carry follow-ups for the sketch owner. No rejections.

1. **PII boundary — ACCEPTED WITH FOLLOW-UP.** §6.5.1 places redaction at intake before the SQLite write, with versioned rules + re-scan job. Ambiguity to resolve: "raw text stored once in the event row with redaction metadata" — is the event row the redacted or the original text? If original is retained, state its retention + who can read it separately from the redacted copy; if redacted, say "redacted text stored once." Also: does the re-scan rewrite history (immutability vs forgetting)? Pin that.
2. **SQLite access — ACCEPTED WITH FOLLOW-UP.** 0600 + single-process writer/reader + console-via-API-only answers the hole. Add the backup/migration/test tooling to the access list — anything that opens the file is part of the story, including the nightly backup copy.
3. **Per-row isolation — ACCEPTED WITH FOLLOW-UP.** `community_id` on every row + filtered queries + empty-read test is exactly the ask. Clarify which tables (if any) are deliberately global (token usage? threshold versions?) and why; and carry the same discipline to the Notion side (page sharing per community), since containers alone don't cover it.
4. **Override queue — ACCEPTED.** SQLite state machine (`pending → approved/rejected/undone`), restart-safe, supermemory mirrors. No follow-up from my lens beyond what's already in my metrics doc (min-sample + quorum live here as gate config, not queue mechanics).
5. **Two render paths — ACCEPTED.** Member digest (no handles) vs mod report (handles + patterns), versioned templates, handle-absence test. Follow-up for the sketch: feed the test an adversarial handle (one that reads like an aggregate, e.g. "5 members") so the assertion proves structure, not luck.
6. **Undo mechanics — ACCEPTED, STRONGER THAN ASKED.** Per-platform undo table + "no undo capability = no auto-execute" closes the broken-promise hole completely. Remaining ask: undo SLA + the failed-undo path (auto-executed, undo API errors — what's the compensation?).
7. **Key-loss matrix — ACCEPTED WITH FOLLOW-UP.** Degradation per dependency with no silent fallbacks is the right shape and matches my hole. Define the alert channel (who gets the operator alert, where it lands) and tie the Groq→Gemini leg to the token-efficiency fallback contract so the two docs agree on paper, not just in spirit.

Net: §6.5 resolves the privacy/architecture round. My §5 is superseded by it — keep §5 as history, treat §6.5 as the build input. Open threads now live with the sketch owner (LB-02 discussion log), not with me.
