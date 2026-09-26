# Demo Runbook with Real IDs (rehearsal sheet — 17:00 demo)

Owner: `omp-research-2` · Task: REQ #64 package 2. Sources: `data/state.db` live rows + HANDOFF + bridge status. Honest labels throughout; nothing here is staged beyond the MapleNest fixtures.

## Gate results (live Jev, from state.db)

| Event | Verdict | Band | Confidence | Reason (template-built) |
|---|---|---|---|---|
| `tg-demo-msg-a` (genuine) | answer | AUTO | 0.92–0.93 | genuine question ≥0.85, solicitation ≤0.10 → post_answer |
| `tg-demo-msg-b` (scam) | quarantine | DRAFT | 0.98 | solicitation ≥0.70 → quarantine for review |
| `demo-c3aff027` | answer | AUTO | 0.94 | same AUTO path |
| `demo-17aefbed` | review | DRAFT | 0.0 fail-closed | classify error → human review (fail-closed working as designed) |

## Transition trail (per event)

`received (ingested) → signals_ready (member_new, solicitation, first_link, question_shape, …) → decided (AUTO/DRAFT) → action_pending (post_answer) | approval_pending (quarantine card) → recorded (awaiting human verdict)`. Query: `SELECT event_id, to_state, reason_code FROM event_transitions WHERE event_id=? ORDER BY rowid`.

## Quarantine + intents + override

- Cards: `card-tg-demo-msg-b`, `card-demo-17aefbed` (both `mod_queue_card`, pending); answers: `act-tg-demo-msg-a`, `act-demo-c3aff027` (both `post_answer`, pending).
- Override row id 1: `tg-demo-msg-b` → approve (writeback path exists; verify live before stage).

## Chain artifacts (provenance-flagged)

- **Notion report page `3e781f99-c28c-8147-9fa0-ff9d50a2b1c5`** — VERIFIED in HANDOFF (integration bot "beadle", top-level Beadle page created; ledger/queue DBs not yet created).
- **Slack ts + Resend id from the REQ** (`1790411848.603789`, `01a0dcdc-…`) — NOT FOUND in state.db, HANDOFF, app/, or bridge history. Treated as **unverified — do not cite on stage** until deepseek confirms their source. Chain status per bridge 13:55: Notion 200 + Resend 200 live; Slack live the moment the bot is invited; Discord blocked on reconnect.
- 3-provider chain for the rubric: Notion → Slack → Resend (all reachable today) with Discord as backup once reconnected.

## Click-by-click (2.5 min)

1. **0:00–0:20 Number:** "6-hour report → about a minute" + sourced pain. No fixture claims beyond MapleNest.
2. **0:20–0:50 Cold open:** Notion Beadle page (`3e781f99…`) + trust-ramp visual. State: ledger/queue DBs pending — say so if asked.
3. **0:50–1:40 Split decision:** `tg-demo-msg-a` AUTO (0.93, reason on screen) → answer posts; `tg-demo-msg-b` DRAFT (0.98) → guardrail card. Same second, opposite outcomes.
4. **1:40–2:00 Guardrail:** policy proof trio from package 1 (`policy list` → trip backstop → `audit policy` fresh row) OR the quarantine card — pick one, not both, for time.
5. **2:00–2:30 Close:** report lands, digest queued, override counter. Stop. Backup video covers the full path if anything fails live.

## Pre-stage checklist

- [ ] Override row 1 writeback verified live (approve → labeled example queryable).
- [ ] Slack bot invited (`/invite @swytchcode`) or Slack leg cut from the chain story.
- [ ] Discord reconnect decision (in scope or cut — affects the 3-provider claim).
- [ ] Backup video recorded against these exact event IDs.
