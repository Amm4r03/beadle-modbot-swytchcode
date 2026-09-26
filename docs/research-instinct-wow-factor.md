# WOW Factor — Making the Gate's Learning Visible (Instinct research)

Date: 2026-09-26 · Source: email 68001. Product/UX research + demo design, not a claim these screens already exist.

## The core answer

The strongest proof is a **short causal chain**: *the gate was unsure → the admin made a decision and explained it → a later, genuinely distinct case was handled differently → the admin can open the exact decision, evidence, and override path.* One traceable case beats any "I learned 12 things" counter.

## The artifact to build: ONE "Because you taught me" case card

Shown on a real subsequent gate action, it contains:
- initial disposition + timestamp
- the admin's exact override and label
- the later case ID
- retrieved labeled example IDs
- Jev's transition reason (one line)
- stored **gate score** + the threshold and action it governed
- action taken or deferred
- one-click correction

Homes: **Notion** = audit/policy history; **Svelte** = links/visualization; **SQLite** = source of scoped event/example IDs; Telegram/Discord stay thin. Language: **"learning from decisions"** — never "retraining Jev" or "proven model improvement."

**Copy pair:** *"Earlier: I asked you about this type of post."* / *"Now: I used your decision on case #A and held case #B for the same policy reason."* If a narrow auto-action genuinely passed its threshold, replace "held" with the actual action. For conflicts: *"These examples conflict, so I asked again."* Never show a raw confidence percentage as calibrated probability — label it **"gate score"** with the threshold and the action it governed.

## Evidence patterns borrowed (sourced)
- **Linear Triage Intelligence** — prediction + reason + accept/decline at the point of action.
- **Intercom Fin** — unresolved case → proposed content fix → human approval; reports outcomes over time.
- **ChatGPT memory** — inspect/correct what is remembered; provenance with caveats.
- **Superhuman personalization** — editable preferences that shape output.
- **Discourse moderation experiment** — human-first, responder silent, staged trust; unfinished AI loses trust.

## 2.5-minute live demo (clocked plan)
1. **0:00–0:25 Cold case:** submit a new ambiguous post; show event ID/timestamp in Svelte, its path through observe/classify/gate/escalate, gate score, and the Notion quarantine card. It asks instead of pretending certainty.
2. **0:25–0:55 Teach once or twice:** admin resolves two *different* quarantine posts with explicit labels + short policy reasons; show the SQLite writeback IDs + linked Notion policy/history cards. Two labels = mechanism demo, not statistical evidence.
3. **0:55–1:30 New case:** a distinct analogous post; open its trace (retrieved examples, Jev reasons per hop, gate score, transitions, disposition). If still quarantined but citing the decisions, say "it recalled your examples and asked with context" — not autonomous improvement. Only show an auto-action if a predeclared narrow threshold was genuinely met.
4. **1:30–2:05 Negative control + correction:** a superficially similar exception that must NOT inherit the rule, or the admin overriding the third case; the override is logged. Trust proof, not hidden failure.
5. **2:05–2:30 Evidence view:** Svelte side-by-side before/after cards, linked event IDs/timestamps, the Notion resolution/policy card, the reason chain; say what changed (retrieved examples or rule version) and what did not (base model weights). Close: "The admin can check what it used and change it."

**Fallback:** if the chain breaks, keep the actual trace on screen and say where it broke; a recorded replay only with real run date/input IDs, labeled.

## First week: earned trust, not a prefilled curve
- **Day 1 — trainee:** quarantine-first; admin resolves first cases; ledger/trust views show IDs/decisions/labels; Svelte shows totals, not a predictive "learning %". Copy: *"I don't have enough examples yet. Your decision on #A is saved for the next similar case."*
- **Day 3 — context-aware assistant:** new event opens with retrieved prior labels + reason; admin sees whether a prior resolution changed the suggested disposition. Copy: *"I suggested quarantine because you resolved #A and #B this way; #C is different, so I asked."* If no comparable case: *"no comparison yet."*
- **Day 7 — limited colleague:** real counts with denominators (reviewed N, overturned X, eligible autonomous Y, erroneous Z, policy versions), each aggregate linked to event IDs. Promotion only for a narrow class after review + threshold + rollback.
- **First month:** only if real decisions accumulate; never promised in the demo.

## Implementation & defensibility checks
1. Persist community_id, event_id, timestamps, source, graph/run/policy version, stage, proposed/final disposition, decision maker, score + threshold at action time, Jev reason, retrieved example IDs, correction, resulting label. Scope every read by user_id at the single access path (SQLite is **not** DB-enforced RLS). Respect 7d/90d retention in display.
2. Keep writeback and later events causally separable: a replay of the same case is a **counterfactual**, labeled "replay"; a fresh third input is independent but two labels ≠ real-world accuracy. Distinguish retrieved examples, rule changes, base-model training.
3. Instrument override rate with numerator/denominator + category (including zero-volume states); pair with sampled error checks; a falling rate can reflect case mix.
4. Notion sync state must be honest — a failed write is not a completed resolution; Svelte links source IDs, never manufactures tidy summaries. Quarantine stays the safe default on conflict/sparse evidence.

**Open risk:** no external source validates Beadle's accuracy; the product examples show interface patterns, not causal proof. Real claims need instrumented test-community results and a documented error review.
