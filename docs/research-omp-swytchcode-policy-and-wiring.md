# Swytchcode Policies + Wiring for Beadle (customer + build lens)

Owner: `omp-research-2` · Date: 2026-09-26 · Task: msg 50 (REQ #50). Companion to Instinct's parallel research (FYI #51) — do not duplicate; this doc is local verification + customer reading.
Rule: every canonical ID and trace below was run on this machine tonight; failures reported as failures. Unsourced claims `[INFERENCE]`.

---

## 1. How policies are defined (verified locally + docs)

**Three files, three jobs** ([policies overview](https://docs.swytchcode.com/policies/overview/)):
- `tooling.json` = "what CAN execute" (trusted methods; unlisted tools refuse immediately).
- `policies.json` = "SHOULD this request execute" (evaluated pre-execution, after input validation, before any network call).
- `manifest.json` = "HOW it executes" (endpoints, retries, timeouts, idempotency).

**A policy = id + target + when + action.** Verified shape from `swy policy add --help`:
- `target`: canonical IDs guarded (repeatable/comma-separated).
- `when`: `field` + `operator` (==, !=, >, in, exists, matches, …) + `value` (CSV for in/not_in, "start,end" for between).
- `action`: `POLICY_BLOCKED`, `REQUIRES_APPROVAL`, `AUTH_FAILED`, `QUOTA_EXCEEDED`, `RATE_LIMITED` + message.
- Nested all/any/not: hand-edit `policies.json`, then `swy policy validate`.

**Pipeline order** ([execution pipeline](https://docs.swytchcode.com/guides/execution-pipeline/)): resolve tool → validate inputs → evaluate policies → resolve endpoint → resolve credentials → apply execution policy (retries/timeouts/idempotency) → execute → normalize → return. Blocked = exit before any network call.

**Expressing a gate policy ("no destructive action without human approval"):** `target: [discord.message.delete, telegram_v5_0.deletemessage.create]` + `when: field=<risk marker> operator=<op> value=<threshold>` + `action: REQUIRES_APPROVAL` (held in Slack/Telegram per [human approval](https://docs.swytchcode.com/policies/overview/)) or `POLICY_BLOCKED`. **Caveat found live:** `swy policy add` warns when `field` is not a declared tool input ("this condition can never match") — gate fields must be real input paths; derived scores (Jev probabilities) are NOT tool inputs, so the Swytchcode policy can only gate on request fields, never on our gate verdict directly. The Jev→policy bridge lives in OUR reducer (we choose which tool to call / whether to call), not in `policies.json`.

**Free vs Pro:** `swy policy` commands run locally on the free tier (verified: add/list/remove/validate all work). The pricing-page Pro gate is on *managed/advanced* policy features; local `policies.json` guardrails work free. Our honest fallback stands regardless: a blocked `--dry-run` (exit 4) labeled as such if a Pro-only feature is ever needed.

## 2. What else `swy` offers that we should wire (verified surface)

- **Input shape discovery:** `swy info <canonical_id>` prints LOCATION (path/body), REQUIRED, TYPE, and body schema — mandatory before writing any exec call. Proved tonight: `channel_id` is a *path* arg, not body (my first dry-run failed validation for exactly this).
- **Three dryness levels:** `--explain` (what would execute, exit 0, no API call — verbose schema dump), `--dry-run` (request that would be sent, no HTTP), live (real call). `--explain` doubles as the demo's "show the trace" beat; `--dry-run` exit 4 is the honest policy-block demo.
- **Auth transparency:** dry-run output shows resolved method + URL + redacted headers (`Authorization: [REDACTED]`) — credential resolution (env → managed → project .env) without leaking secrets. Say this on stage if asked about key handling.
- **`swy audit` (separate surface):** `audit network` (outbound calls), `audit policy` (violation log), `audit stats` (history/success rate), `audit clear`. Policies are config; audit is the log — `policy list` shows rules, `audit policy` shows what they blocked. The digest's "blocked this week" line should read from `audit policy`.
- **Exit codes as UI:** validation fail = 1, schema-invalid policies = 6 (observed live tonight when my test policy broke the schema — every exec failed until removal), policy block = 4. Our wrapper must map these to event-contract states, not just pass through stderr.
- **Discovery:** `swy list` (local tools), `search`/`discover` (intent → capabilities), `plan` (workflow steps), `demo` (stripe/fintech only — NOT our T3 actions), `examples`, `sync`, `workflow`, `mcp` (MCP server commands — editor/agent integration path, out of demo scope).
- **Account:** `auth` (provider credentials), `login/logout/whoami/workspace`, `doctor` (diagnostics), `config`.

## 3. Beadle action-path map (dry-run verified tonight)

All three legs dry-run clean (exit 0, resolved URL + redacted auth shown). Canonical IDs are exact — never guessed:

| Beat | Swy method | Resolved endpoint (dry-run observed) | Input shape gotcha |
|---|---|---|---|
| Answer post (Discord proof path) | `discord.message.create` | `POST https://discord.com/api/v10/channels/{channel_id}/messages` | `channel_id` is a PATH arg via JSON-stdin `args`, NOT inside `body`; `body.content` holds text |
| Ledger write | `notion.page.create` | `POST https://api.notion.com/v1/pages` (+ `Notion-Version: 2025-09-03` header auto) | body schema per `swy info`; parent page must be shared with the integration or 404 at live time |
| Digest email | `resend.email.create` | `POST https://api.resend.com/emails` | `to`/`subject` in body; test sender for demo |
| Telegram answer/quarantine | direct Bot API (path B) | n/a (Swytchcode bundle is a placeholder per HANDOFF) | Telegram legs do NOT count as Swytchcode-mediated — say so if asked |

## 4. The 3-distinct-APIs rubric (proposed + verified)

**Chain (one event, three providers, output-to-action):** (A) `notion.page.create` — write the decision/ledger row; (B) `discord.message.create` — post the approved answer (its content cites the ledger row from A); (C) `resend.email.create` — digest/escalation summary referencing both. Each leg's output feeds the next (ledger ID → answer citation → digest content), satisfying "output influences next action."
**Status:** all three dry-run green tonight. Live proof needs real channel/page/recipient (first-30-min job). If the rubric counts *providers* rather than *calls*, this chain qualifies (Notion → Discord → Resend); if it counts *calls*, it qualifies three times over. Telegram-via-direct-API is our fourth leg but must NOT be presented as Swytchcode-mediated.

## 5. Customer-lens notes (what this means for the pitch)

- The pipeline diagram (resolve → validate → policy → endpoint → credentials → execute) IS the "confidence is not proof of authorization" story made concrete — show it once, then live it on every beat.
- The `field`-must-be-a-real-input caveat is a trust asset: we say "Swytchcode guards the request fields; our reducer guards the judgment — two layers, honestly separated" instead of implying one magic policy box.
- `audit policy` as the digest source closes the loop: blocked actions are counted from the same log the demo shows. No second bookkeeping system.
