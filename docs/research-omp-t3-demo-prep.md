# T3 Calibrated Community Operator — Demo Prep (customer lens)

Owner: `omp-research-2` · Date: 2026-09-25 (evening) · For: msg 26 prep assignments.
Assumes: scripted Telegram community, Jev gate + Swytchcode policy, H1 demo-mode rule, H2 event contract, C3 graceful-denial UX.

---

## 1. Demo script beats (2.5 min) + graceful-denial copy

**0:00–0:20 — The number.** "Community managers spend 6+ hours a month writing health reports across 5 communities — and 3 mods quit one Sunday leaving 600 messages unanswered." (sourced: v2 verdicts/searches.) Then: "Watch the 6-hour report happen in 60 seconds — with judgment where it matters."

**0:20–0:50 — Cold open on the artifact.** Last week's health report already open in Notion: unanswered questions, new-member silence, one sentiment dip, scam attempts quarantined. Let it speak for 5 seconds. Narrator: "This is what the manager woke up to Monday. Everything below was handled, except the two items flagged for human judgment."

**0:50–1:40 — The live run: split decision.** Two messages land seconds apart in the staged Telegram group. On screen, live Jev scores both (confidence + topic visible per the H2 event feed) — routing to be validated with live Jev once the key lands:
- **Message A (genuine):** expected high confidence → agent answers publicly via the chain (Telegram answer + Notion log), reasoning steps visible.
- **Message B (polished scam):** expected policy block → guardrail beat (next section). Same system, same second, opposite outcomes.

**1:40–2:00 — The guardrail beat (graceful denial, C3).** Never an error state. On-screen copy pattern:

> 🛡 **Held for review — not sent.**
> *What it was:* message matching the impersonation pattern ("admin" handle, urgency, off-platform wallet link).
> *Why it stopped:* policy `public-send` requires confidence ≥ 0.85 on non-scam topics; live Jev scam score shown on screen (threshold ≥ 0.70; exact score from the live call, not pre-computed).
> *Where it went:* moderator review queue with full context — audit line `#a3f9` logged.
> The agent then posts the plain-language member warning itself (safe, pre-approved template).

And the escalate-with-context beat for borderline-genuine (the premium detail): the manager receives question + attempted answer + exactly why confidence fell short — one decision to make, not homework.

**2:00–2:30 — The number, proven.** Weekly report lands in Notion, digest queued via Resend. "6 hours → 60 seconds. The manager opens Monday to what got handled, who newly spoke up, and two judgment calls — nothing else." Stop.

---

## 2. Fixture spec — scripted Telegram community "MapleNest"

**Community:** MapleNest, a 1,200-member hobbyist group (urban gardening) on Telegram + a #garden-help Slack mirror for mods. Seeded history: 6 weeks of threads, 3 prior weekly Notion reports (trending-healthy baseline), member roster with 8 regulars, 40 lurkers, 1 known scammer handle already quarantined last week (establishes the pattern is real).

**Message A — genuine member question (planted, deterministic):**
> "hey! my balcony tomatoes got these yellow spots after the rain last week — anyone dealt with this? pics in thread 🙏" — from seeded member `priya_grows` (lurker, 0 prior posts → doubles as an activation event).
> Jev routing: expected auto-answer path (genuine plant-care question) — to be validated with live Jev once the key lands. Agent replies with the blight answer synthesized from the Notion lorebook (two prior threads cited), logs to Notion, marks `priya_grows` activated.

**Message B — polished scam (planted, deterministic):**
> DM-style post from `MapleNest_Admin` (note the underscore — impersonator): "URGENT: MapleNest is migrating! Verify your wallet to keep your membership + claim 50 MAPLE tokens 👉 maplenest-verify[.]xyz" — mirrors the sourced drain pattern (fake admin DM, urgency, off-platform link).
> Jev routing: expected policy block path — to be validated with live Jev once the key lands. Blocked, audit line, member warning posted, mod queue updated.

**Seeded Notion data:** member table (with `priya_grows` flagged new), policy rules page (thresholds visible on stage: auto ≥ 0.85, draft 0.6–0.85, block/queue scam ≥ 0.7), 3 prior reports, lorebook with the 2 blight threads the answer cites.
**Seeded Slack:** #mod-queue channel receiving the escalate-with-context card for message B.
**Resend:** Sunday digest template pre-filled with last week's numbers; live send queued at the 2:00 mark.
**Timing budget:** live scoring <3s per message on screen (narrate over it); full run rehearsed against fixtures once the Jev key lands; backup video covers the whole golden path per H1.

---

## 3. Success metrics framing for the stage (before → after)

Say all three as measured-on-fixtures deltas, never absolute promises:

1. **First-answer time on repeat questions: hours → seconds.** Before: median 4h 20m waiting on mod availability (seeded baseline). After (target, to be timed live once the Jev key lands): seconds-scale agent answer, majority resolved without human touch. On stage: message A answered while the narrator speaks — exact seconds read off the live run, never pre-stated.
2. **Lurker activation: silence → first voice.** Before: 40 lurkers, 0 first-posts/week. After: `priya_grows` activated live on stage — the metric incarnated as a person. Cohort line: "activated members still posting at week 4."
3. **Scam time-to-quarantine: days of damage → seconds to containment.** Before: last month's real-pattern incident took a weekend + victims. After (target, to be timed live): seconds-scale quarantine with zero member exposure + audit line. "Trust is the moat you can watch work."

**Stage honesty rule:** every number is labeled "on our seeded community" and every live figure is read off the run, never stated in advance — judges forgive fixtures, they punish checkable falsehoods (taste mechanics). The repeatable line for the close stays aspirational until timed: **"The 6-hour report, done in about a minute."**
