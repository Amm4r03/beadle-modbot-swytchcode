# Metrics + Self-Updating Config + Cross-Platform + Marketing (customer lens)

Owner: `omp-research-2` · Date: 2026-09-26 · Task: product-phase research, no code.
Rule: every figure below is a **target to be measured or a method to measure it** — never a pre-stated result (no-fake-work house rule). Anything publishable must be labeled with method + scope ("on our seeded community," "measured over N weeks on our own deployment").

---

## 1. Success metrics + publishability per differentiator

### 1a. The gate that learns (thresholds tuned by overrides)

- **What it is:** every approve/reject/edit writes an override record; a nightly job recomputes per-class thresholds; the override counter ("asked 20, overrode 6, next week 4 fewer") proves the curve.
- **Success:** escalation rate falls week-over-week while mod reversal rate stays flat or falls (fewer asks, same or better judgment). Method: count escalations + overrides per week from the audit log; plot the curve.
- **Failure:** escalation rate falls because the gate got reckless (reversals rise), or thresholds thrash week to week (learning rate too hot), or one admin's habits drag the whole community's gates.
- **Publishable?** Yes, with scope: "on our own deployment, escalations fell X→Y over N weeks with reversals flat" — publish the curve image, not a single number. Never "our AI is 95% accurate" without a defined test set, N, and date range. The trust-ramp visual (wk-05 draft-only → auto-send unlocked) is publishable as *our story*, not as a general claim.

### 1b. Decision-context packets (escalate-with-context card)

- **What it is:** every escalation carries question + attempted answer + exactly why confidence fell short + precedent ("similar lure quarantined Sep-08").
- **Success:** median mod time-to-decision falls (target: under 60 seconds per card, to be timed), and mods stop asking follow-up questions in-thread (the card was sufficient). Method: timestamp card-posted → mod-react; count clarification replies.
- **Failure:** cards get skimmed and mods ask "so what do I do?" anyway — meaning the packet is data, not a decision. Fix: end every card with one recommended action + one-tap approve.
- **Publishable?** Yes: "median decision time X seconds on N cards" with method. The card format itself is publishable as a design pattern (screenshot-safe, no PII).

### 1c. Trend engine (weekly "3 things to run")

- **What it is:** trend × community-topic × member-history → one drafted activity with why-now evidence, effort, reversibility; rejected trends shown as filter proof.
- **Success:** the manager *runs* ≥1 suggested activity per month and reports it worked (reply, attendance, entries). Leading metric: suggestion accept rate (target: ≥1 in 3 accepted, to be measured). Lagging metric: activated/re-engaged members attributed to a suggested activity.
- **Failure:** suggestions get a polite "interesting!" and die — the digest becomes astrology. Kill signal: zero accepted in 4 weeks → the filter is wrong, not the manager.
- **Publishable?** Carefully: accept-rate on our own deployment with N stated. Never "managers love our suggestions" (sentiment isn't behavior). The *reject list* beat is publishable as a trust mechanic ("we filtered out 6 irrelevant trends — here's why").

### 1d. Scam ladder (detect → quarantine → warn → escalate, tiered)

- **What it is:** scam-likelihood tiers route to different responses (low: watch; mid: draft warning for mod; high: auto-quarantine + member warning + mod card), all audit-logged and reversible.
- **Success:** time-to-quarantine in seconds (to be timed live), zero member exposure on staged attacks, and every false positive reversed within the hour with an apology path. Track both: containment speed AND reversal speed.
- **Failure:** a false quarantine bans a real member with no recourse (trust destroyed faster than any scam), or the ladder is so cautious it only ever "watches."
- **Publishable?** Yes with staging labels: "quarantined in Ns on staged attacks, 0 exposure, N/N reversed" — always say "staged." The ladder *design* (tiers + reversibility rationale: false quarantine is reversible, a answered scam is not) is publishable as a principle.

### General publishability rules (the "ensure we can publish it" answer)

1. **Method + scope on every number:** what was measured, on what data, over what period, N=? "8s answer" → "8s on our seeded MapleNest fixtures, timed live on <date>."
2. **Curves beat points:** a falling escalation curve is honest; "95% accurate" is a lie waiting for a denominator.
3. **Behavior beats sentiment:** accept rate, reversal rate, decision time — not "managers loved it."
4. **Staged is fine, silent staging is fraud:** every demo/staged figure labeled; backup video labeled as recording.
5. **Never publish:** another community's data, member PII, scam victims' details, or any number we haven't actually timed.

---

## 2. Self-updating config: thresholds/policies that learn (and un-learn)

### What learns, what never does

- **Learns:** per-message-class auto/draft/block thresholds (within floors/ceilings), topic mastery flags (draft-only → auto after N approvals), lorebook promotions/retirements.
- **Never learns:** the `never_auto` list (payments, deletions, permission changes), floor/ceiling bounds themselves, isolation rules. These change only by human edit with a changelog entry — via an owner-only console config editor (versioned, every edit logged), where admins may *propose* but only the owner *approves* (E1). A system that can learn away its own guardrails is a liability, not a feature.

### Belief updates (supermemory lead)

- Each human verdict writes an override memory: `{type: override, message_class, jev_scores, verdict: approve/reject/edit, resulting_action, admin, timestamp}` in the community's `containerTag`.
- Corrections supersede via Updates edges (new fact wins for "what's true now," history kept for audit) — the graph's native mechanism, not custom code.
- **Undos are first-class, weighted signals:** undo weight lives in config per action type (default: undo = 3× a passive approval; `undo_weights: {unban: 3, answer_edit: 2, warning_revoke: 2, digest_reject: 1}` `[INFERENCE: defaults are tuning choices, validate in build]`). Precise semantics: an un-ban reverses the quarantine verdict only; an answer-edit replaces the drafted text but keeps the routing verdict; a warning-revoke retracts the member warning but keeps the audit trail. Flip-flop guard: alternating approve/reject on the same item more than twice freezes that item for human review instead of accumulating weight (E4).

### Deterministic learning checkpoints (no mid-run drift)

- Thresholds change **only** at nightly checkpoints, never mid-run: recompute job reads override history → proposes new thresholds → writes versioned `jev_gates.yaml` + changelog row to Notion → takes effect next run. **Demo honesty (E2):** an 8-hour event cannot grow a real curve — the demo seeds override history as staged inputs (allowed) and labels the curve "compressed timeline on seeded history"; any "next week N fewer" line is a labeled projection, never a result.
- Every decision logs gate-version + policy-version + model-version (the trace), so any past action is reproducible from its versions. Demo determinism falls out for free: pin the version, the behavior is fixed.
- Minimum-sample rule: no threshold moves on fewer than N overrides per class (N=5 default `[INFERENCE]`); below that, the checkpoint logs "insufficient signal" and holds.

### "Why did it change its mind?" (explainable retrieval)

- The UI answers from the changelog + override history, in plain language: "I now answer rose questions solo — you approved 9/10 since Sep-20 (gate v3→v4 on Sep-26)." Never graph jargon.
- Every threshold row links to the verdicts that moved it (count + dates, not raw member data). A judge or admin can audit the *cause* of any behavior change in two clicks.

### Anti-drift / anti-overfitting (one loud admin problem)

1. **Floors + ceilings:** no threshold may leave its band no matter the history.
2. **Multi-admin quorum:** a threshold change needs verdicts from ≥2 distinct admins OR ≥N samples; one admin's week alone can't drag the gates.
3. **Time decay:** overrides older than 30 days decay in weight — the community's *current* tolerance rules, not its founding admin's.
4. **Reversal circuit-breaker:** if the post-checkpoint week's reversal rate exceeds 2× the pre-checkpoint baseline (min 5 decisions in each window `[INFERENCE]`), the versioned gate store pointer-switches back to the prior version, writes a changelog entry ("v4→v3 auto-revert, reversal spike 12%→28%"), and flags for human review — the system distrusts its own learning (E5).
5. **Contradiction surfacing:** when new verdicts contradict settled thresholds, surface it ("you've rejected 3 auto-answers on refunds this week — tighten the band?") instead of silently averaging.

### Wiring (supermemory as lead)

- Store: community `containerTag`; override memories + lorebook docs + member/topic facts; Notion holds the human-readable changelog mirror.
- Write path: `record_learning` node (after human verdict) → `supermemory.add(override)` + audit line.
- Read path: `retrieve_context` node → hybrid search (memories + lorebook chunks) → prompt context; nightly `recalibrate` → read overrides → recompute → versioned gates + Notion changelog.
- Gate of record stays our own review queue (H4); supermemory stores outcomes, never authorizes.

---

## 3. Cross-platform config: one schema, many communities

### Platform-agnostic config schema (v1 proposal)

```yaml
config_version: 1
community: { name, platform, locale, timezone }
thresholds:  # per-action gates; same semantics everywhere
  public_answer: { auto_at: 0.85, draft_band: [0.60, 0.85] }
  scam_quarantine: { auto_block_at: 0.70 }
  member_nudge: { auto_at: 0.80 }
  digest_send: { auto_at: 0.90 }
never_auto: [payments, deletions, permission_changes, external_contact]
scam_ladder:  # tiers are platform-agnostic; actions map per platform below
  - { tier: watch, when: "scam_p in [0.40, 0.70)", action: log_only }
  - { tier: warn_draft, when: "scam_p in [0.70, 0.85)", action: draft_warning_for_mod }
  - { tier: quarantine, when: "scam_p >= 0.85", action: quarantine_sender + post_warning + mod_card }
escalation_cadence: { digest: weekly_sunday_09IST, nudges_max_per_week: 1, mod_reminder_after_hours: 24 }
tone: { voice: "warm, plain-language, no jargon", sign_off: "Stay green", emoji: light }
policies: { policy_version, source: tooling_json_ref }
platform_adapter:  # ONLY this section changes per platform
  platform: telegram  # | discord | slack
  read: { method, scopes }
  write: { answer_post, delete, warn_post }
  threads_model: flat_with_replies  # discord: true threads; slack: thread_ts
  rate_limits_note: "..."
```

### Porting rules (Telegram ⇄ Discord ⇄ Slack)

- **Ports cleanly:** thresholds, ladder tiers, cadences, tone, never_auto, audit format, digest structure — the entire judgment layer is platform-blind.
- **Needs adapter work:** message ops (Telegram `sendMessage/deleteMessage` vs Discord channel/message ops vs Slack `chat.postMessage` + `thread_ts`), thread models (Discord true threads vs Telegram reply-chains), permission models (bot-admin vs OAuth scopes), rate limits.
- **Needs re-tuning per community (not per platform):** scam-pattern examples (crypto-discord lures ≠ gardening-telegram lures), tone norms, nudge cadence. The schema carries *starter* values; the learning loop (§2) calibrates them per community. Porting = copy config, swap adapter, re-seed examples, run trust ramp from draft-only.
- **Demo implication:** portability is proven with a config diff + adapter stub on screen ("same brain, new home") — one platform live, the second shown as scoped work, never implied as done (E3). Still a scalability proof point for the 10% impact score, honestly framed.

---

## 4. Marketing notes (customer lens — to dial in with Instinct)

### Positioning lines (candidates, pick one voice and hold it)

1. "Monday morning: the report is already written, next Sunday is already planned, and the only thing in your inbox is the two calls only you can make."
2. "It arrives a trainee and becomes a colleague." (learning arc — best for the trust-ramp visual)
3. "Automation where it's safe, judgment where it matters." (thesis line — best for technical judges)
4. "The 6-hour report, done in about a minute." (number line — close only, after timing it live)

### Proof points (only what we've sourced or will have timed)

- Budget-backed pain: $2–5K/mo manager replacement pricing; 6-hour monthly reports (sourced: v2 verdicts/searches).
- Scam stakes: sourced drain corpus (r/solana, r/wallet_TG, r/CryptoScams); Sep-08 MapleNest precedent in fixtures.
- Live proof (to be timed, never pre-stated): split-decision on stage, quarantine seconds, override counter ticking.
- Honesty as positioning: "staged group, live writes; fixtures modeled on documented real scams" — candor is the differentiator in a room full of vapor.

### Demo sequence (marketing cut — mirrors the 2.5-min beats)

Number + sourced pain → cold open on the populated artifact (let it speak) → split decision (the gasp) → guardrail receipt (the trust) → override counter tick (it learns) → number proven (stop). One sentence per beat in the pitch; the product demo carries the rest.

### What NOT to claim (ever)

No accuracy percentages without test sets; no "AI moderates for you" (it proposes, the human disposes — until trust is earned, then say exactly that); no cross-community learning claims (isolation is the point); no "fully autonomous."

---

## 5. Autoresearch fold-in (Instinct 67967, customer-lens reading)

Instinct's draft (`docs/research-instinct-learning-and-pitch.md`) reframes the gate-that-learns (§1a/§2) as Karpathy-style experimental discipline: freeze evaluator + cases, one bounded candidate change, replay, keep only measured improvement, human-readable receipt. What I take from it, in customer terms:

- **"Checked policy updates" is a better stage sentence than "the gate learns."** Learning claims invite "prove it"; a receipt invites "show me." The demo beat stays the same (mod approves → counter ticks) but the narration changes: "her correction became a reviewable rule, replayed against the same cases, one click to revert."
- **Reason codes are the missing UX in my §2 design.** Approve/reject *plus a reason* ("wrong topic," "too risky," "right call, wrong wording") turns verdicts into routable signal — different reasons tune different knobs. Add a 3-option reason picker to the escalate card; cost is one row of buttons.
- **Holdout honesty strengthens the publishability rules (§1).** The 4-tuning/4-holdout split gives "untouched" a concrete meaning: publish tuning-set deltas freely, holdout deltas only with N stated, and say "controlled demo" when N=8. This slots straight into rule 1 (method + scope).
- **The 2-minute sequence is compatible with our 2.5-min beats** (demo-prep doc): admin decision first (0:00–0:15 ≈ our cold open), context packet (our split decision), reject-with-reason → candidate diff (our guardrail beat, extended by one screen), replay before/after (new, ~25s — steal from the digest beat, not the split decision), approve + Swytchcode allowed/denied pair (our close). Net change: the digest beat shrinks to make room for the replay table.
- **Positioning pick:** "The community agent with a gate that learns" wins on clarity + demonstrability; "AI moderation bot" concedes distinctiveness and "autonomous community manager" overpromises. Category: human-governed community operations.
- **Caveat I hold:** the draft's evidence is moderation-literature + winner self-reports, not conversion tests — treat the sequence as a recommended narrative, not a proven formula. And the autoresearch name-drop must always carry the disclaimer (bounded experiment loop, not model retraining) or a technical judge will eat us alive.
