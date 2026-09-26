# T3 Edge Design — The Gate That Learns (+ Trend Engine, Real Data, Agent-Proof)

Date: 2026-09-26 (~02:00 IST) · Source: email reply 67958 (`~/Downloads/T3-edge-research.pdf`). This is the edge-of-the-edge design for the merged T3 build.

## 1. The edge: THE GATE THAT LEARNS

**The idea:** the operator is visibly dumber on week 1 than week 4 — every approve/reject/edit a human makes on an escalation tunes that community's Jev thresholds. Week 1 it asks 20 times; week 4 it asks 4, and it can show the curve. No other team will demo a product that provably got smarter during the judging period.

**First-run flow (minutes):** add bot as admin → agent reads last 7 days → first health report in <10 min, populated with THEIR unanswered questions and silent new members → first screen is the report plus: "3 questions need you; I can approve-answer 2 next time if you approve my drafts" → first approve/reject starts the learning loop in minute one.

**Memory tiers (free-tier buildable):**
- Working: the LangGraph run state (messages, Jev results, decisions, audit refs).
- Short-term: this week's window + escalation decisions in the Notion report pages (double-duty, zero new infra).
- Long-term: supermemory graph of norms/FAQs/member history/override outcomes, container per community (multi-tenant story).

**Learning mechanics (honest 8-hour version):** store each escalation with Jev scores + human verdict; recompute act/escalate thresholds per message class from override history (running override-rate per bucket / logistic on (score, verdict)). Threshold learning, not fine-tuning — matches Jev's own gate guidance and the conformal help-gate literature.

**Stage moment:** the **override counter** — "this week I asked 20 times; you overrode me 6; next week I'll ask 4 fewer." Running against fixtures overnight makes the curve real by morning.

## 2. Trend engine — verified sources + exact digest format

**Sources verified tonight:** trendsapi.ai (free key, 100 req/mo, no card — fine for 4–8 calls/month); **trend-pulse** (OSS, zero auth — safer primary, no quota); HN Algolia (official, free, no auth). **Reddit unauthenticated .json is being deprecated — do not rely on it** (OAuth app only, skip tonight).

**Actionable = three parts, always:** (1) the trend + why it's rising (source link), (2) why it fits THIS community (tied to an observed gap in the report), (3) a ready-to-post draft. Without all three it's astrology.

**Exact digest format (one screen, max 3 cards):**
```
THIS WEEK — 3 things to run
1. [Trend] "AI agents in production" rising 3x on HN this week (link)
   Why for us: 4 members asked deployment questions this week, 1 unanswered
   Ready to post: "Shipping an agent to prod this year? What's your stack — drop
   your setup below, we'll compile the answers into a community wiki page."
```

**Scope call:** the 3-card section (~1 hour on top of the aggregate node) is a differentiator; trend analytics pages, content calendars, auto-posting = scope creep. The manager's accept/reject of suggestions is another override signal feeding §1.

## 3. Real data for MapleNest

- **Primary: synthesize from documented real patterns** — scam fixtures lifted from the sourced corpus (r/solana, r/wallet_TG, r/CryptoScams); genuine questions from real FAQ threads in-domain.
- **Legitimate public sources:** HN Algolia (free) for real question threads; public Telegram groups read-only (observing is within norms; never post outside the staged group); Reddit only via free OAuth app (skip tonight).
- **Smallest honest live test:** point the **report pipeline only** (no answering/moderation writes) at one real public community the team controls/is invited to (a small friends' Telegram group counts) → scan → report → digest; show side-by-side with the staged report. Read-only on real data + full chain on staged data = maximum credibility, zero platform risk.

## 4. Agent-proof checklist (stage-legible, in demo order)

1. Reasoning visible from minute one (graph state rendered live).
2. Uncertainty quantified on screen (Jev batched scores in ms).
3. Same input class, different outcomes (split decision — say "same pipeline, opposite verdicts, because it judged").
4. A decision the script didn't know: invite a judge to post a real question (opt-in).
5. Memory across runs (this week vs last week; recurring questions added to FAQ).
6. Adaptation: the override counter ("you rejected 2 of 8, I adjusted") — nightly threshold update is honest if time is short.
7. Real side effects with receipts (Swytchcode audit refs on every write; policy block exit 4 or honest dry-run).
8. Recovery: one idempotent retry shown live (optional).

**Honesty lines (unchanged):** staged group, live writes; Jev tiny paid meter; policy block Pro or dry-run; fixtures modeled on documented real scams.

## 5. Backlog

Keynote/pitch deck — flagged to the research agent's backlog for later; not worked tonight.
