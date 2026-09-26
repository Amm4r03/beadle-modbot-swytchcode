# Competition + Local Testing + Policy Visibility (customer lens)

Owner: `omp-research-2` · Date: 2026-09-26 · Task: product-phase research, no code.
Constraints honored: policy path = FREE (no Pro), packaging = bot, free-tier APIs only, staged inputs OK / fabricated outputs never. Unsourced claims `[INFERENCE]`.

---

## 1. Competitive battle: why switch from MEE6/Dyno/Carl-bot?

### What the incumbents actually are (sourced 2026 reviews)

All three are **rule engines + utility bundles**, not judgment systems ([supervisor.gg comparison, Aug 2026](https://supervisor.gg/blog/mee6-vs-dyno-vs-supervisor); [peakbot.pro 30-day test, 2026](https://peakbot.pro/blog/mee6-vs-dyno-vs-carl-bot-2026)):

- **Dyno** — moderation king: 19 automod filters (caps, spam, invites, phishing links…), all free; per-server $5.99/mo. Weakness: no leveling, no reaction roles, automod warnings don't feed the manual warning system.
- **MEE6** — engagement king: leveling/XP, giveaways, social alerts, audit log; $11.95/mo, heaviest paywall, slowest innovation. Moderation is 8 basic checks.
- **Carl-bot** — reaction roles + embeds + logging; ~$7.99/mo; moderation basic, setup steep.
- **Shared ceiling (the key quote):** "Word lists only catch what you wrote down… Counters measure volume, never meaning… Neither classifies harm by category… Neither weighs conversation context. **Switching between MEE6 and Dyno does nothing about any of that.**"

### Why an admin switches to us

Not for more filters — for the three things rule engines structurally cannot do:

1. **Meaning over matching.** The single calm, correctly-spelled scam sentence that trips zero counters. Our Jev gate reads intent + impersonation pattern; theirs reads `fr33 n1tr0` variants admins must enumerate by hand.
2. **Judgment with receipts.** Their automod acts silently or not at all; ours routes through confidence tiers, shows *why* on the escalate card, and logs an audit line per action. The admin keeps control instead of maintaining word lists.
3. **A loop that compounds.** Their config is static until a human edits it; ours re-tunes thresholds from overrides, retires stale lore, and proves it on the trust-ramp curve. "It arrives a trainee and becomes a colleague."

### Objections they'll raise (honest answers)

- **"False positives will nuke my community."** Fair — the #1 automod complaint ([false-positive guides](https://peakbot.pro/blog/how-to-fix-discord-automod-false-positives)). Our answer: the scam gate is deliberately lower than the answer gate *because* quarantine is reversible and a wrong public answer is not; every block carries one-tap un-ban + apology path; reversal speed is a tracked metric. Never claim zero false positives.
- **"You're reading our messages — privacy?"** Fair. Our answer: per-community container isolation (no cross-community training on their data unless they opt in), PII minimization (handles are facts, wallet/DM contents quarantined, never memories), scoped keys, purge on request. Consent-first like the T2 flow.
- **"Another subscription?"** Fair — MEE6+Dyno+Carl-bot already stack to ~$25/mo. Our answer: free-tier stack (Telegram free, Slack/Notion/Resend free tiers, Jev pennies per the audit); paid lines named upfront (Swytchcode Pro only if they want custom policies; Resend past 100/day). No per-server multiplication for the judgment layer.
- **"Lock-in — what if we leave?"** Fair. Our answer: config is portable YAML, audit trail exports to Notion they own, lorebook lives in their docs. Leaving costs them the tuned thresholds, not their data. Say that plainly.

### The honest wedge

**Don't replace their bot on day one — sit beside it.** Wedge = the weekly report (read-only value, zero risk), then escalate-with-context cards (judgment they keep), then gated auto-actions after trust is earned. The trust ramp IS the sales motion: draft-only week one, auto-send unlocked by approvals. We win the messages their counters can't read; they keep the bot that counts.

### What we must never claim

No accuracy percentages without test sets; no "replaces MEE6/Dyno" (we complement rule engines — say the supervisor.gg line: three tools, three jobs); no cross-community learning; no "fully autonomous"; no cost claim beyond sourced free tiers + named paid lines; no staged figure presented as production data.

---

## 2. Local testing strategy: every story, staged servers, pass criteria

### Principle

Staged *inputs* (scripted messages, seeded history) are allowed; fabricated *outputs* (pre-computed scores presented as live) are not. So the harness drives **real code paths against staged inputs** — the gates actually score (live Jev once keyed, else the story is marked untestable and blocked, never faked).

### Mock-data harness per story

| Story | Staged inputs | What runs for real | PASS = |
|---|---|---|---|
| Answer genuine Q | MSG-A + lorebook | gate → draft/post → Notion log | answer posted with ≥2 citations, audit line written, `priya_grows` flagged activated |
| Escalate borderline | mid-confidence message (draft band) | gate → draft + mod card with reason | card contains question + attempted answer + why-short + precedent; nothing sent publicly |
| Scam ladder | MSG-B, MSG-R1, MSG-R2 (held back) | gate → quarantine + warning + card + audit | quarantined in seconds, 0 member exposure, warning posted, card actionable; reversals one-tap |
| Weekly report | wk-05/06/07 seeds | aggregation → Notion page | report renders answered/new-voices/incidents/escalations with correct counts off the seeds |
| Digest | report + templates | composition → Resend (test sender) | digest matches report numbers; links resolve; queued, not silently dropped |
| Learning loop | seeded override history | recompute → versioned gates + changelog | thresholds move only with ≥N samples; changelog row written; versions pinned per decision |

### Per-platform staged test servers

- **Telegram:** private staged group + bot (privacy off/admin) — plant the pair, watch the chain. Primary surface.
- **Discord:** staged server with the adapter stub (config diff proof) — read + post in a test channel; full chain only if adapter lands.
- **Slack:** test workspace #mod-queue — escalate cards land here; assert format, not just delivery.
- **Notion:** integration token + explicitly-shared test pages (or 404 — check sharing first).
- **Resend:** test sender to our own inboxes; assert content match, never spam real members.

### Transition: mock → private → real

1. **Mock (tonight):** fixtures only; every PASS above green; backup video recorded here.
2. **Private community (first real):** a small friends' group we control — report pipeline read-only first (no answering/moderation writes), side-by-side with staged report; writes enabled only after the read-only report proves sane.
3. **Real (post-hackathon):** trust ramp from draft-only; auto-send unlocks by approvals; weekly review of the changelog for the first month. Never skip stage 2 — the first live false quarantine must happen where forgiveness exists.

---

## 3. Policy visibility: what the admin sees (customer lens)

### What the admin actually wants (not what engineers want to show)

Admins don't want thresholds; they want **answers to three questions**: *what did you do? why? can I undo it?* Everything below serves those three.

### The three surfaces, in their language

1. **Per-action receipt (in the moment):** the guardrail card pattern — what it was / why it stopped (rule + score band, never raw model output) / where it went / one-tap undo. Language: "held," "answered," "drafted" — verbs, not gate names. Never "Noul 0.93" or "Updates edge."
2. **Weekly changelog (the trust-ramp page):** "what I learned" — promoted/retired facts with counts, threshold moves with the verdicts behind them ("rose questions: draft-only → auto, you approved 9/10"), reversals owned ("I was wrong twice on refunds — reverted to v3"). This page is the retention mechanic.
3. **"Why did it change its mind?" (on demand):** any threshold row expands to its cause — verdict count + dates + the two most recent examples. Two clicks from "it behaves differently" to "here's exactly why." No graph jargon anywhere: "learned," "changed my mind," "retired."

### Where each lives

Receipts in the mod-queue surface (Slack card); changelog in Notion (manager-owned, survives us); explanations inline-expandable from either. Memory internals (container tags, dreaming modes, edge types) never surface — they're engineering words for engineering docs.
