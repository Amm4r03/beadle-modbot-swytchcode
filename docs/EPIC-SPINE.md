# Beadle — Epic Spine & One-Day Build Plan (Instinct)

> Source: email 67995, 2026-09-26. Planning baseline; all architecture decisions settled; PRFAQ headline still open. This is the progress-tracking backbone and the anti-scope-creep guardrail.

> **REVISED PRIORITY (user, 2026-09-26): agent core first, integrations later.**
> Step 1: prove the **agent itself** works over **mock data** (fixtures): LangGraph state machine + Jev hops + signals + reducer + state management + transition log — no bots, no Notion, no external writes needed.
> Step 2: verify state management/underlying logic end-to-end on fixtures (deterministic replay, confidence stored, reasons logged).
> Step 3: integrations (E1 ingress bots, E3 Notion surface, E5 front) — the integration epic comes later.
> Revised order: **E4 data foundation (minimal) → E2 agent core on mock data → verify state/logic → E1 ingress → E3 admin surface → E5 web front → Discord adapter → demo.**
> Framework re-evaluation (all frameworks in the brief vs the new shape): `docs/research-framework-reevaluation.md` — **LangGraph stays locked**.

## Product frame
- **Customer (dual):** the community admin pays and decides; the member experience is the proof inside the story.
- **Working claim:** the community agent with a gate that learns. Final headline wording open.
- **Demo moment:** a genuine question answered confidently while a polished scam hits the visible policy block — same second, opposite outcomes, Jev confidence on screen.
- **Cross-cutting:** confidence stored from day one (hi/lo thresholds as config, tuned later); retention raw 7d + derived/audit 90d; planner keys via a custom fallback utility holding Groq + Gemini.

## Epic 1 — Ingress: thin Telegram + Discord bots (bots listen and act only)

| Stage | Success metric |
|---|---|
| 1. Telegram bot live in scripted group | 100% of test-group messages observed and forwarded as events within 2s |
| 2. Bot can act | Delete / flag / reply executes within 2s, visible in group |
| 3. Discord adapter | Same event shape from a Discord message with zero gate-engine changes |

**Failure signals:** missed/duplicated events; crash on media/stickers/links; action latency >5s; event-shape drift between platforms.
**Do-not-build:** no judgment/filtering/per-platform logic beyond format mapping; no additional platforms; no message storage in the bot layer.

## Epic 2 — Gate engine: LangGraph + Jev

One state machine: observe → classify → gate → escalate → resolve → learn. Jev is the brain inside each hop and writes a one-line reason per transition; LangGraph owns state; Jev fires only where judgment is needed.

| Stage | Success metric |
|---|---|
| 1. Graph skeleton | Every event traverses all states; full transition log written |
| 2. Jev hops wired | One-line reason on 100% of judged transitions; rules-only events never call Jev |
| 3. Confidence stored | Confidence on every decision record from day one; hi/lo thresholds from config |

**Failure signals:** Jev firing on every event; non-deterministic loops/dead ends; missing reasons; confidence absent from any decision row.
**Do-not-build:** no fine-tuning; no multi-model ensemble beyond the Groq/Gemini key fallback; no auto-learning beyond the quarantine writeback; no threshold auto-tuning.

## Epic 3 — Admin surface: Notion as system of record

Events ledger, quarantine queue, member trust history, 90-day pattern view. Quarantine = Jev flags low-confidence items; admin one-tap resolves; resolution written back as a labeled example.

| Stage | Success metric |
|---|---|
| 1. Events ledger | 100% of gate decisions land in the ledger within 5s |
| 2. Quarantine queue + resolve | One-tap resolve writes a labeled example back to the store, every time |
| 3. Trust + pattern views | Member trust row updates per event; 90-day pattern view renders from derived data |

**Failure signals:** ledger lag >5s or duplicates; a resolve that does not write back; Notion rate limiting under demo load; pattern view querying raw instead of derived.
**Do-not-build:** no custom admin UI beyond Notion; no analytics beyond the four views; no real-time push; no exports.

## Epic 4 — Identity + data security

Site auth links Telegram identity to a Beadle user. Local SQLite exposed via ngrok; a single access path enforces per-user scope; every row carries user_id; schema RLS-ready for a later Postgres swap. Demo line: "every read goes through one access path, and that path enforces per-user scope" — not DB-enforced RLS.

| Stage | Success metric |
|---|---|
| 1. Identity link | One user completes Telegram → Beadle link end-to-end via site auth |
| 2. Single access path | 100% of reads through the access module; cross-user read test returns denied/empty |
| 3. RLS-ready schema | user_id on every table; Postgres policy notes committed (under one page) |

**Failure signals:** any code path bypassing the access module; any row without user_id; identity spoofing in the link flow; scope leaking in dashboard queries.
**Do-not-build:** never claim DB-enforced RLS on SQLite; no org/role model beyond per-user scope; no encryption-at-rest work; no production deployment hardening.

## Epic 5 — Web front: minimal Svelte app

Auth surface + per-community telemetry dashboard.

| Stage | Success metric |
|---|---|
| 1. App + auth surface | Login and identity link work entirely through the Svelte front |
| 2. Telemetry dashboard | Per-community live counts: events observed, gated, quarantined, resolved |
| 3. Demo polish | Full 4-minute walkthrough runs without touching code or a terminal |

**Failure signals:** stale dashboard numbers; per-community scoping leaks; build breakage under ngrok; auth flow dead-ends.
**Do-not-build:** no design system; no mobile app; no chart library beyond minimal counters; no public marketing site.

## Dependencies

| Epic | Depends on | Why |
|---|---|---|
| E2 Gate engine | E1 (Telegram stage 1), E4 (schema) | needs events in + storage for decisions/confidence |
| E3 Admin surface | E2 | ledger/queue record gate decisions; writeback needs the store |
| E4 Identity + data | none | foundation; starts the day |
| E5 Web front | E4 (auth), E2/E3 (data) | auth surface needs identity; dashboard needs decision data |
| E1 Discord adapter | E1 Telegram event shape | adapter proof only after the event contract is fixed |

## Project-level metrics

| Metric | Target |
|---|---|
| Gate decisions with stored one-line reason | 100% |
| Judged events with confidence score | 100% |
| Quarantine resolves written back as labeled examples | 100% |
| Cross-user scope violations in testing | 0 |
| End-to-end latency observe → action | <5s |
| Platforms live in demo | 2 (Telegram + Discord) |
| Demo moment lands | yes |

## One-day build order (9:00–17:00 IST)

| Time | Work |
|---|---|
| 09:00–09:45 | Data foundation: SQLite schema (user_id everywhere), single access path module, ngrok up |
| 09:45–10:45 | Telegram bot: listen + act |
| 10:45–12:00 | LangGraph skeleton, rules-only pass-through end to end |
| 12:00–13:00 | Jev hops: per-transition reasons + confidence storage |
| 13:00–13:30 | Buffer / lunch |
| 13:30–14:15 | Notion: events ledger, quarantine queue, one-tap resolve writeback |
| 14:15–15:00 | Svelte auth + Telegram identity link |
| 15:00–15:45 | Telemetry dashboard per community |
| 15:45–16:30 | Discord adapter (adapter proof) |
| 16:30–17:00 | Demo script dry run + fixes |
