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

## Chain artifacts (from `docs/chain-run-proof.json` — fresh live run, committed)

- **Notion report page `3e781f99-c28c-8135-b097-f53607d9bd62`** — 200, created 2026-09-26T08:50Z, request `e8801678-…`; audit `nw_5311dd64e241`.
- **Slack ts `1790412619.377569`** (channel `C0C4JHM79AA`) — 200; audit `nw_44f67f184a00`.
- **Resend id `01a0dce8-82ca-73ca-a8f9-fffefd124515`** — 200; audit `nw_fa0705d353ec`.
- **Discord: ERROR (expected)** — exit 3, 401 auth (connection revoked); chain goes Notion → Slack → Resend for the 3-provider rubric. Discord excluded until reconnected.
- Provenance rule: cite the proof file, never hand-copied IDs. Re-run `swy audit network` for the 14:2x entries if the demo needs fresh timestamps.

## New features since the first runbook (verify live before stage)

- **Announcements** (`POST /api/announce`, api/server.py:236): broadcast text to Telegram (direct Bot API, needs `TELEGRAM_CHAT_ID` or a prior inbound message to discover it), Slack (Swytchcode post, needs channel), Discord (direct REST, needs token + channel). Per-platform results returned, failures as strings — rehearse which legs are green.
- **Knowledge ingest** (`POST /api/knowledge` + `GET /api/knowledge`): title+text → doc_id slug → `memory.remember`; 9 docs live (6 GDG + 3 plant). See `research-omp-knowledge-usage.md` for citation/hit-miss metrics.
- **Telegram ingress** (poller in `telegram-ingest` tab): live group → events. Confirm the poller is running + which group before promising live ingress on stage.
- **`/test` view** (api/server.py:283, `api/test.html`): rehearsal surface — confirm it loads + which actions it exercises before routing the demo through it.

## Click-by-click (2.5 min)

1. **0:00–0:20 Number:** "6-hour report → about a minute" + sourced pain. No fixture claims beyond MapleNest.
2. **0:20–0:50 Cold open:** Notion Beadle page + trust-ramp visual (IDs above, from the proof file).
3. **0:50–1:40 Split decision:** `tg-demo-msg-a` AUTO (0.93) → answer posts; `tg-demo-msg-b` DRAFT (0.98) → guardrail card. Same second, opposite outcomes.
4. **1:40–2:00 Guardrail:** policy trio (`policy list` → trip backstop → `audit policy` fresh row) OR the quarantine card — pick one for time.
5. **2:00–2:30 Close:** report lands, digest queued, override counter. Stop. Backup video covers failures.

## Pre-stage checklist

- [ ] Override row 1 writeback verified live (approve → labeled example queryable).
- [ ] Slack bot invited or Slack leg cut from the chain story.
- [ ] Discord reconnect decision (in scope or cut).
- [ ] Backup video recorded against these exact event IDs.
