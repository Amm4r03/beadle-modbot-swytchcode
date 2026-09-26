# T3 Trend Engine + Edge-of-Edge — Customer-Lens Critique

Owner: `omp-research-2` · Date: 2026-09-25 (evening) · Task: bridge request (trend/promotion engine + edge-of-edge + agent-proof).
Method: customer lens. Verified live tonight: trendsapi.ai free tier (100 req/mo, no card — site), HN Algolia public API (called it, JSON back, zero-auth). trend-pulse open-source + Google Trends RSS per email-seat brief, unverified by me — flagged below.

---

## 1. What managers actually act on: actionable vs generic

Managers act on suggestions that are **specific, low-effort, reversible, and pre-drafted**. They ignore everything else — a suggestion is a task in disguise, and tired managers don't accept tasks from bots.

**Generic (will be ignored):** "Trending: AI coding agents (88/100 on Reddit). Consider posting about it." No link to MapleNest, no draft, no reason this week. This is spam with a score attached.

**Actionable (gets approved):** "Blight threads got 3× median replies + monsoon plant-disease searches rising. Run a 48h 'show your spots' photo clinic Sunday? Here's the post draft + judging rubric + winner prize (moss-pole DIY kit, ₹120). Approve → I schedule + remind + compile entries Monday." One tap, effort priced, outcome visible.

**The rule:** every suggestion must carry (a) why-now evidence tied to *their* community, (b) the draft artifact, (c) effort + reversibility stated. Anything missing one of the three is a notification, and notifications are gimmicks (taste mechanics).

**Filtering is the whole product.** Raw trends are useless to a gardening group; the agent's job is trend × community-topic × member-history. "Cozy gaming setups trending" must never reach MapleNest. A suggestion that survives filtering proves the agent *knows* the community — which is itself a demo beat.

## 2. Does this strengthen T3? Yes — if it closes the loop

Today's operator is **listen → act → report** (past-facing). The trend engine makes it **listen → act → propose → run → report** (future-facing). The digest stops being a newspaper and becomes a Monday plan: "here's what happened, here's what I'd run next, approve with ✅."

It strengthens T3 on three judging axes: innovation (no other team shows trend→activity→execution chaining), real-world impact (blank-Monday is the manager's actual dread — "communities die from quiet attrition"), and demo density (a second proposal beat after the split-decision, same fixtures).

**Two conditions:** (a) quota discipline — weekly digest at ~4–8 trend calls/month fits the 100/mo free tier with headroom; cache aggressively, never call live on stage; (b) it must not bloat the 2.5 min — the trend beat is 20 seconds inside the digest moment ("and for next week, it proposes…"), not a second demo.

**Real hole:** relevance filtering is hand-waved. "Trend × community topic" sounds trivial and is actually the hardest judgment in the feature — a bad filter produces laughable suggestions on stage (gaming setups for gardeners). Mitigation: pre-compute the one suggestion on fixtures, show the *rejected* candidates list as the trust beat ("filtered out 6 trends irrelevant to gardening"). The rejects prove the filter works.

## 3. Edge-of-edge: onboarding in minutes + a system that evolves

**Onboarding (minutes, not hours):** connect Telegram group → set 3 thresholds (defaults pre-filled from gates) → point at existing pinned FAQs/threads as seed lorebook → first health report in 60 seconds. The demo *is* the onboarding: cold open on an empty dashboard, connect fixtures, report appears. Time-to-first-value in minutes (taste mechanic #1).

**Evolution (memory tiers / routing / escalation learning):**
- **Memory tiers:** hot lorebook (cited weekly) vs cold archive (auto-demoted, never deleted — auditability). The graph visibly prunes itself; show "promoted 3 facts, retired 11 stale ones this month."
- **Routing learning:** per-topic auto-answer success logged; topics with repeated mod corrections auto-drop into draft-only. Thresholds adapt per community, shown as a changelog, never silent.
- **Escalation learning:** every mod ✅/❌ on a card tunes the gate; the digest reports "I now answer rose questions solo — you approved 9/10."

Customer translation: "it arrives a trainee and becomes a colleague." That sentence is the pitch.

## 4. Proof it is an agent, not a router

Three tests a judge can apply, all demonstrable on stage:
1. **Judgment under uncertainty:** the split-decision — same second, opposite outcomes, scored live. A router has one path; this one chose.
2. **State across time:** the report references last week's unresolved item and follows up ("priya_grows posted again — activated cohort retained"). Routers are stateless.
3. **Learning from feedback:** a topic that was draft-only in wk-05 is auto-answered in wk-07 with the approval trail shown. Routers don't change.

If all three appear in 2.5 minutes, the "just a router" objection dies in the room.

## 5. The single unforgettable capability

**"Monday morning: the report is already written, next Sunday is already planned, and the only thing in your inbox is the two calls only you can make."**

One sentence, before/after, no jargon. The number attached: "6 hours → 60 seconds — and it proposes next week, too."

## 6. Source feasibility (free-tier, stage-safe)

| Source | Auth | Free tier | Stage use |
|---|---|---|---|
| trendsapi.ai | Bearer key | 100 req/mo, no card (verified tonight) | weekly batch, cached — never live |
| HN Algolia API | none | public, rate-generous (called tonight, 1ms) | tech-community flavor; cached |
| Google Trends RSS | none (unofficial) | free but brittle, breaks without warning | fallback only; never primary |
| trend-pulse (OSS) | none claimed | self-hosted, zero-auth claimed — **unverified, flag for smoke test** | verify or cut |

**Recommendation:** ship with trendsapi.ai (cached) + HN Algolia (cached); cut the rest if unverified by morning. Two working sources beat four flaky ones.
