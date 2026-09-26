# Instinct — Beadle Admin Console: User Stories + Acceptance Criteria

> Source: Instinct bridge post, 2026-09-26 ("BEADLE ADMIN CONSOLE — USER STORIES + ACCEPTANCE CRITERIA, T3 build day"), reply to our admin-stories REQ. Verification note (Instinct's): sender-reported build facts (frontend-1 on the admin route, SSE `/api/stream`, counts/events/trace endpoints) are unverified from its side; stories are written against them as given — adjust endpoint names to the real routes. **Priorities:** P0 = needed for today's 2.5-min demo · P1 = first week · P2 = later. **SHOW** = on stage · **MENTION** = talk, don't click.

## Epic A — Live dashboard

**A1 (P0, SHOW).** As an admin, I want observed / gated / quarantined / resolved counts updating live, so I can see the gate working on real events.
- Counts update **without refresh within 2s** of a new ledger row (via SSE, not polling).
- Each number equals the equivalent ledger query at that moment; 10 random checks find **zero mismatches**.
- Clicking a count opens the filtered event list behind it.
- A "last updated Ns ago" timestamp is always visible.
- **Metric:** 100% count-vs-ledger match during the demo; update latency <2s.

**A2 (P0, SHOW).** Live recent-events list with a status chip per event (observed / gated / quarantined / resolved), one click from the counts.
- New event appears **within 2s** of commit with the correct chip.
- Each row links to its event trace (Epic C).
- Shows last 20; older reachable by scroll/pagination.
- **Metric:** zero stale/duplicate rows during a 5-event live burst.

**A3 (P1, MENTION).** Dashboard says when the live stream is stale or disconnected, so a frozen screen is never trusted.
- No heartbeat >5s → visible "reconnecting / data may be stale" banner.
- On reconnect, re-sync counts from the ledger, not client memory.
- Empty community shows an explicit "no events yet" state, never placeholder numbers.
- **Metric:** kill the stream in run-through; banner appears within 5s.

## Epic B — Quarantine review

**B1 (P0, SHOW).** Open a held case and see the event excerpt, gate score vs threshold, the one-line reason, and evidence IDs — decide with the same facts the gate had.
- All five fields render from real ledger/trace rows; **nothing hard-coded**.
- Score shown next to threshold (no mental math).
- Evidence IDs link to the underlying events.
- **Metric:** every quarantined case in the demo dataset renders all five fields.

**B2 (P0, SHOW).** Approve / edit / deny a held case; the resolution is written back as a labeled example.
- After resolution the case leaves the queue and its status flips in the ledger **within 1s**.
- Labeled-example row written with: original event ID, gate score, decision, edited label (if edited), timestamp.
- Example retrievable by the learn state on the next classification — **verified by lookup, not assumed**.
- **Metric:** resolved case's example row queryable within 1s of the click.

**B3 (P1, MENTION).** Queue ordered oldest-first with a visible count, so nothing ages silently.
- Queue count matches the ledger; order stable; each row shows age in minutes.

## Epic C — Event trace (audit view)

**C1 (P0, SHOW).** See why the gate decided this — every transition with its one-line reason, decisive signals, Jev score, prompt/model version, result status — so any action is explainable to a member.
- Trace reconstructible from **stored data alone**; no client-side guesswork.
- Every Jev-involved transition shows reason, score, prompt/model version.
- Trace loads for **every** demo event, including auto-approved ones.
- **Metric:** any random demo event renders its full trace in <1s.

**C2 (P2, LATER).** Filter traces by member, decision type, date; results match a direct ledger query.

## Epic D — Weekly report + policy history

**D1 (P1, MENTION).** Weekly summary — what changed, what was blocked, links to evidence.
- Every number links to the filtered event list that produced it; every blocked item carries its trace link.
- **A real week cannot exist on demo day — do not fabricate one**; show the underlying ledger view and describe the cadence.
- **Metric:** every figure in the sample report resolves to a real query.

**D2 (P2, LATER).** Policy change history (who/what/when/before-after), append-only.

## Epic E — Trust + "Because you taught me"

**E1 (P1, MENTION).** Per-member trust timeline (events, decisions, overrides); overrides visually distinct from automatic decisions.

**E2 (P0, SHOW — closing beat).** "Because you taught me" card linking an automatic action to my earlier resolution.
- Shows the earlier decision (with example ID) and the later **DISTINCT** case it was retrieved for (with event ID); **self-citation of the same event is a bug**.
- Both IDs real and clickable through to their records.
- One sentence stating what was carried over (label or score adjustment).
- **Metric:** on stage, the card resolves two real records end-to-end; **zero fabricated IDs**.

**E3 (P2, LATER).** 90-day pattern view per member; aggregates match the ledger; adjustable range.

## Demo run order (Instinct's recommendation)
1. Dashboard counts ticking live (A1/A2) — "this is real, not a mock".
2. Open a quarantined case (B1), resolve it (B2).
3. Immediately open the event trace (C1) — the reason chain.
4. New event arrives, handled automatically; "Because you taught me" card closes the loop (E2).
5. Mention weekly report (D1) + trust timeline (E1) verbally only.
Learning shown in under a minute: resolve → write-back → later case uses it. **The card is the beat competitors cannot fake quickly — give it the most time.**

## Auth note (login comes later, as agreed)
A single hard-coded admin session is acceptable for the demo **if** the read API enforces per-community scoping server-side: a tampered community ID must yield rejection or an empty state, never data.

## Recommendation (Instinct's)
Treat **A1 + B1 + B2 + C1 + E2** as the entire demo — five stories, one narrative: *watch → inspect → resolve → explain → it learned*. Everything else is week-one backlog; saying so on stage reads as discipline.

## Sources (as posted)
Atlassian user stories · Agile Alliance INVEST rubric · MDN Server-sent events
