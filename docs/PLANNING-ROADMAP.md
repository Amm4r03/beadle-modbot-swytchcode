# Planning Roadmap (Cascade) — Beadle / T3

> Referenced by AGENTS.md. Cascade flow: **[0 brainstorm] → 1 PRFAQ → 2 Feature Doc → 3 User Stories → 4 Delivery ⟂ STOP**. No stage skipped, none back-filled; one stage per turn; nothing is implemented before stage 4 is complete and the user explicitly starts the build. Last updated 2026-09-26.

## Current status

| Stage | Artifact(s) | Status |
|---|---|---|
| 0 — Brainstorm | `docs/brainstorm/LB-01-product-and-delivery.md`, `docs/brainstorm/LB-02-architecture-and-data.md` | **OPEN — awaiting user review** |
| 1 — PRFAQ | `docs/prfaq/PRFAQ-Beadle.md` (to be generated) | not started (gated on 0→1) |
| 2 — Feature Doc | `docs/features/FEATURE-Beadle.md` (to be generated; 13 required sections) | not started |
| 3 — User Stories | `docs/stories/` (epics + stories, P0/P1, observable acceptance criteria) | not started |
| 4 — Delivery | aven board `SH-*` (already used for research; build tasks tracked here) | not started |

## Gate 0→1 — brainstorm → PRFAQ (falsifiable)

| Check | Passes when | Current state |
|---|---|---|
| Forks closed | Every open question that changes **what** gets built is answered **in the note**, with reasoning. Questions that only change **how** may stay open (engineering choices) | Mostly closed; remaining forks: console scope (what the demo surface shows) — user call; supermemory mode is a *how* choice |
| Claims grounded | Every load-bearing number has a date + source | Yes — all research docs carry sources |
| Someone owns it | Named owner + why now | Owner: the user. Why now: buildathon 2026-09-26; T3 locked; form submitted |

**One action to close 0→1:** the user reviews LB-01 + LB-02 and confirms the console scope (what the Svelte surface shows) — then the PRFAQ is written (WHY: problem, what must never happen, success/failure feelings — no implementation detail).

## Gate 1→2 — PRFAQ → Feature Doc
PRFAQ exists at the resolved path; it answers WHY, not HOW.

## Gate 2→3 — Feature Doc → User Stories
All 13 required sections present; non-goals populated (not a heading); open questions answered or explicitly deferred with an owner.

## Gate 3→4 — User Stories → Delivery
A review returns **Engineering-Ready** (critical findings are stop-the-line, never auto-fixed); every story carries P0/P1; acceptance criteria are observable (name the state, input, expected output).

## The stop
Cascade ends at stage 4. It never writes code, runs migrations, or opens PRs. Starting the build is a separate, explicit user decision.

## Notes on tooling
The cascade skill's status script and generators are bound to the Football Paradise project and are not present here. We follow the skill's **principles and gate definitions** (this file records them), and each artifact will state which structure guide it was written against.

## Review package for the user (stage 0)
1. `LB-01-product-and-delivery.md` — product, packaging, admin experience, session-4 live decisions (thin bots + shared LangGraph, Jev per hop, Notion locked, quarantine flow, epic spine).
2. `LB-02-architecture-and-data.md` — components, event lifecycle, schemas, storage/retention/PII, privacy fixes, consolidated decisions.
3. This roadmap — the path from here to stories, with gates.
