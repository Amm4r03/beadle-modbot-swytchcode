# How the topic was chosen — the process that actually ran

> Reconstructed from the archived artifacts (2026-09-25 → 2026-09-26). This is the raw material for a future **`topic-decision` skill**: the exact pipeline, the artifacts each step produced, and the mechanics that made it work. Winner: **Track 3 → Community Health Operator (Beadle) with the Jev gate.**

## The pipeline (60 → 12 → 6 → 1)

```
1. Parallel idea generation        60 ideas  (30 per agent: deepseek + omp, per track)
2. Shortlist                       12 ideas  (2 per track)
3. External panel verdicts          6 ideas  (1 per track; Instinct, sourced + registry-verified)
4. Independent ratings              scores    (both agents rate /10 vs the judging criteria; averaged)
5. Customer-obsession research      evidence  (real pain threads, willingness-to-pay, quotes)
6. Taste/moat brief                 mechanics (the five 100x-vs-gimmick mechanics)
7. Developed designs               6 designs (one number · ruthless cuts · premium detail)
8. The bet + runner-up              decision  (with the banger moment and honest moat framing)
9. Lock + brief                     T3 locked (T3-PROJECT.md, decision register)
```

## What each stage actually did

**1 · Idea generation (all seats, in parallel).** Every seat produced 30 ideas across the six tracks (`docs/archive/research-deepseek-ideas.md`, `research-omp-ideas.md`). No filtering — volume first, diversity by lens (engineering vs customer).

**2 · Shortlist 2 per track** (`research-deepseek-shortlist.md`). Selection criteria were explicit: **customer-obsession impact, distinctiveness, scoring-criteria potential** (Swytchcode chaining 30% / technical 25% / innovation 20%). Overlapping variants were consolidated — one survives per concept. Engineering viability deliberately deferred.

**3 · External panel verdicts** (`research-deepseek-panel-verdicts.md`). Instinct picked **one per track** — every pick sourced to practitioner threads, every API-availability claim HTTP-verified against the live registry. This is where feasibility kills happened honestly (e.g., *Async Stand-in dropped — Google Meet's API cannot host a speaking bot*).

**4 · Independent ratings** (`research-deepseek-ratings.md` + `research-omp-ratings.md` → averaged in `research-final-evolution.md`). Both agents scored the six against the judging criteria **before seeing each other's scores**.

**5 · Customer-obsession research.** A dedicated pack (Instinct email 67964) on the surviving candidates: real pain quotes, budget-backed pain, willingness-to-pay.

**6 · Taste/moat mechanics** (`research-v2-final-candidates.md`). The five mechanics that separate 100x from gimmick:
1. Time-to-first-value on real-feeling data, in minutes
2. Speed you can feel (every beat <3s or narrated)
3. Removal, not addition
4. One number users repeat for you
5. Trust through visible control
Plus the **gimmick tells to avoid** (toy data, "imagine if", notification-as-payoff, falsifiable claims).

**7 · Developed designs.** Each of the six got: **one number** (e.g., "the 6-hour report, done in 60 seconds"), **ruthless cuts**, and a **premium detail** (for Beadle: escalate-with-context — question + attempted answer + why confidence fell short).

**8 · The bet.** Community Health Operator with the Jev gate — most budget-backed pain, cleanest 3+ API chain with a natural Jev + policy showcase, safest live demo (scripted community, no money/inboxes/calendars), and a number that lands. Runner-up: Order-to-Cash (flip only if sandbox credentials are ready). **The banger moment**: a genuine question answered and a polished scam blocked in the same second — *automation where it's safe, judgment where it matters*. Moat framing kept honest: data flywheel + switching costs, **never** "our LLM is better".

**9 · Lock.** The winner became `docs/T3-PROJECT.md` (locked brief), tracked thereafter in `docs/DECISION-REGISTER.md` (every WHAT-level decision: **user-locked / proposed / open**, nothing final without a user-locked row).

## The reusable recipe (for the `topic-decision` skill)

1. **Constraints inventory** — hard rules first (budget, timeline, demoability, honesty).
2. **Parallel idea generation** — volume across lenses; no filtering at birth.
3. **Shortlist with explicit criteria** — impact, distinctiveness, rubric alignment; consolidate duplicates.
4. **External panel verdicts** — sourced + registry/API-verified; kill infeasible ideas loudly.
5. **Independent ratings** — blind scores against the rubric, then average.
6. **Customer-obsession evidence** — real pain, real budgets, real quotes.
7. **Taste/moat mechanics** — one number, cuts, premium detail, gimmick tells.
8. **The bet** — one candidate + a runner-up + a banger moment + honest moat language.
9. **Lock + register** — a locked brief and a decision register with explicit statuses.

**Templates to ship with the skill:** decision register · research-pack format (sources + caveats + `[INFERENCE]` tags) · honesty-lines list · banger-moment test · the 60→12→6→1 pipeline table.
