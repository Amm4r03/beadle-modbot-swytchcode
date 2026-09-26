# Build Plan — Today (2026-09-26, 12:15 → 17:00 IST)

> Plan of attack only — **no building until the user gives the go.** Order follows the user's P0: **prove the agent core on mock data first, integrations later.** Every phase has observable acceptance criteria (from `EPIC-SPINE.md`). No fake work: blocked → ask.

## Phase 0 — Clear the path (15 min, no code)
- [ ] **Jev key:** user re-copies from console.typesafe.ai/keys → re-paste `JEV_API_KEY` → verify with one live call (`jev.evaluate("test")`).
- [ ] **Fixture metadata:** add explicit `joined_at` per fixture author (remove the guess in `main.py`).
- [ ] **Confirm env:** `.env` keys present; `swy auth status` = 4 connected; `mode: production`.
- **Acceptance:** a live Jev call returns a real score; the smoke test shows genuine → answer path and scam → quarantine path with real probabilities.

## Phase 1 — Agent core on fixtures (60–75 min) *(P0)*
- [ ] Complete the 12 deterministic signals (currently 4) with UNKNOWN handling + versioning.
- [ ] `MemoryStore` (sqlite-vec + FTS5 in `state.db`): remember/recall/forget; seed FAQ + norms; local embeddings.
- [ ] Gate: memory retrieval → Jev questions → deterministic reducer (AUTO/DRAFT/DENY) with thresholds from config; reasons persisted.
- [ ] Learning hop: override rows + nightly-checkpoint stub (proposal + replay against frozen cases).
- **Acceptance (observable):** both fixture messages traverse all states; every judged transition has a one-line reason; confidence stored on every decision; replay of a decision reconstructs it from versions.

## Phase 2 — Execution path (30 min)
- [ ] `swytchcode.py` adapter: outbox intent before call → `swy exec` (Resend/Notion/Discord; Telegram direct) → reconcile → audit ref.
- [ ] Wire the quarantine card + answer post as the two demo actions; idempotency keys.
- **Acceptance:** one allowed action executes with an audit ref; one blocked/dry-run action shows exit 4; duplicate intent never re-executes.

## Phase 3 — Surfaces (60 min)
- [ ] Create **Events Ledger + Quarantine Queue** in Notion **through swy**; projection from SQLite; resolve → override writeback.
- [ ] Telegram ingress (direct Bot API polling) + Discord adapter (swy, `params.channel_id`); thin adapters only.
- **Acceptance:** a staged Telegram message appears in the ledger; a resolve writes a labeled override back; Discord produces the same event shape.

## Phase 4 — Console + demo (60 min)
- [ ] Svelte console: SSE reasoning stream + weekly report links + policy history (static build).
- [ ] Demo script rehearsal (cold case → teach → new case → negative control → evidence view), backup recording, freeze fixtures.
- **Acceptance:** full 2.5-min run without touching a terminal; fallback labeled honestly.

## Minimum credible path (if time runs short)
Phase 0 → 1 → 2 → (Notion queue only) → demo with the split decision + learning candidate. **Cut first:** Discord adapter, telemetry dashboard, trend cards, report polish. **Never cut:** reasons on transitions, confidence storage, the fail-closed gate, honesty lines.

## Dependencies
- Phase 1 needs the Jev key (Phase 0). Phase 2 needs `swy` auth (done) + Notion parent page (done). Phase 3 needs Phase 2's adapter. Phase 4 needs Phase 3's data.
- Parallelizable: Notion DB creation (swy) while signals/memory are being finished.

## Why this order (direction check)
The user's P0 is a working agent, not integrations. Mock-data-first proves state management and judgment before any platform plumbing; integrations then slot into an already-working core. Each phase maps to the epic spine's success metrics; nothing here claims unbuilt capability.
