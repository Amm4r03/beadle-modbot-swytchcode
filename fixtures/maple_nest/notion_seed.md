# MapleNest — Notion Seed

> Import order: `members` → `policies` → `lorebook` → `reports/wk-**`. Demo week is wk-07 (2026-09-21 → 2026-09-27).

## members (table)

| handle | status | joined | posts | notes |
|---|---|---|---|---|
| arjun_plants | regular | 2026-06-02 | 48 | swap-meet organizer |
| meera_greens | regular | 2026-05-19 | 61 | pest/disease answers, cited twice in lorebook |
| kabir_soil | regular | 2026-05-19 | 74 | soil mixes; mod-adjacent, NOT a mod |
| sana_leafs | regular | 2026-07-11 | 22 | indiranagar; succulents |
| vikram_pots | regular | 2026-07-30 | 17 | roses |
| divya_fern | regular | 2026-08-04 | 12 | ferns, hard-water saga |
| rohan_cacti | regular | 2026-06-25 | 19 | moved flats 2026-09-23 |
| anaya_moss | regular | 2026-08-20 | 9 | DIY moss pole guide |
| mod_ash | moderator | 2026-05-19 | 30 | pinned the Sep-08 scam warning |
| priya_grows | **new (lurker)** | 2026-09-18 | 0 | whitefield; balcony tomatoes; activation target |
| MapleNest_Admin | **suspect** | 2026-09-23 | 0 | handle mimics mods; quarantine candidate |
| maplenest.support | **held-back raid** | 2026-09-26 | 0 | revealed live; dotted-handle impersonation style |
| Maple_Nest_Official | **held-back fallback** | 2026-09-25 | 0 | revealed only if R1 under-scores |
| MapleNestAdmin_bot | banned 2026-09-08 | 2026-09-07 | 0 | prior impersonator, precedent for the pattern |

## policies (page — visible on stage)

- `public-send`: auto-answer requires topic confidence ≥ **0.85** AND scam-likelihood < **0.20**.
- `draft-band`: confidence 0.60–0.85 → draft reply for mod approval, never auto-send.
- `scam-block`: scam-likelihood ≥ **0.70** → block, quarantine sender, post member warning (pre-approved template), file audit line, escalate card to #mod-queue.
- `external-meetings`: never touch (no external meetings in scope).
- Every automated action writes an audit line: `action · actor · policy-version · jev-confidence · timestamp`.

## lorebook (pages, cited by the agent's answer to MSG-A)

- **Tomato yellow spots after rain (Sep 2026):** meera_greens: "lower leaves + yellow halos after rain = early blight usual suspect; remove affected leaves, don't compost, mulch to stop soil splash, copper spray if spreading." + kabir_soil: "whitefield rain week — check drainage holes first, tomatoes hate wet feet."
- **Fungus gnat quarantine (Sep 2026):** kabir_soil's yearly rant, condensed.
- **Neem oil buying guide (Aug 2026):** sana_leafs/vikram_pots price thread, condensed.

## reports/wk-05 (2026-09-07 → 2026-09-13)

- Answered: 14 questions, median first-answer 3h 50m (all human).
- New voices: 1 (anaya_moss, moss pole thread).
- Incidents: 1 — MapleNestAdmin_bot impersonator, banned in ~2 days after meera_greens' flag. Lesson logged: "we were lucky she spoke up."

## reports/wk-06 (2026-09-14 → 2026-09-20)

- Answered: 11 questions, median first-answer 4h 20m.
- New voices: 0. Lurkers steady at 41.
- Incidents: 0. Sentiment: healthy, swap-meet planning dominates.

## trust-ramp (page — the earned-autonomy visual for the cold open)

| week | mode | auto-sent | drafts approved | notes |
|---|---|---|---|---|
| wk-05 | draft-only | 0 | 14/14 reviewed | agent proposes, mods dispose |
| wk-06 | assisted | 6 low-risk | 9/10 approved | rose-pruning + moss-pole answers cleared for auto |
| wk-07 | **auto-send unlocked** | thresholds live | mods keep veto | approvals earned the keys — 23/24 lifetime |

## reports/wk-07 (demo week, 2026-09-21 → 2026-09-27) — LIVE, fills during demo

- Answered: MSG-A → 8s, agent, citing lorebook ×2.
- New voices: priya_grows activated (first post → answered → welcomed).
- Incidents: MSG-B quarantined in 11s, 0 member exposure, audit `#a3f9`.
- Raid beat: MSG-R1 (held-back variant, never rehearsed) quarantined live, audit `#a3fa`; MSG-R2 fallback unused unless R1 under-scores.
- Escalations awaiting judgment: 0 after mod clears the card (or 1, if the presenter leaves it open as the "your turn" beat).
