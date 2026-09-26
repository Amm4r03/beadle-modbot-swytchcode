# Beadle Signal Layer v0.1 — Deterministic Facts, Bounded Judgment (Instinct)

Date: 2026-09-26 · Source: email 67976. Design proposal, not observed production behavior. All thresholds are starter config, not measured optima.

## Decision

A **signal** = a versioned pure function of a message event + an immutable, time-stamped community snapshot → typed value (`TRUE|FALSE|UNKNOWN`, or an integer count/age) + evidence + input freshness. **Signals never declare a member a scammer** — they constrain what Jev may do, supply its questions/evidence, and make the policy band reproducible. Start with 12 cheap signals. Only **exact admin-supplied deny rules** may quarantine without Jev; resemblance/language/age are not proof. Missing input → `UNKNOWN`, never `FALSE`.

## Contract (TypeScript sketch)

```ts
type Tri = 'TRUE' | 'FALSE' | 'UNKNOWN';
type SignalResult = { id; version; value: Tri | number; unit?; evidence[]; input_status: 'COMPLETE'|'MISSING'|'STALE'|'ERROR'; evaluated_at; cost_ms };
type SignalDefinition = { id; version; scope: 'message'|'thread'|'member'|'community'; inputs[]; normalization; function_id; output: 'tri'|'integer'; threshold?; maximum_input_bytes; deadline_ms; effect: 'hard_quarantine'|'ask_jev'|'draft_context'|'dashboard_only'; unknown_effect; owner };
```

Snapshot: `event_id`, `community_id`, server event time, author ID/role/join time, normalized body (≤4,096 code points), URL tokens, roster/policy/FAQ revisions, time-window counts. Relative times computed from event timestamp (replay agrees). Duplicate event IDs produce no second action. Raw bodies are untrusted input, never instructions. Per-event evaluation budget: **30ms**; cache miss/deadline → `UNKNOWN`.

## The 12 signals (starter thresholds)

| ID / effect | Computation | Test vector |
|---|---|---|
| `member_new` / ask_jev | `event_at - joined_at < 24h` (context multiplier only) | 2h → T; 72h → F; unavailable → U |
| `staff_name_near` / ask_jev | NFKC + confusable skeleton vs admin roster; exact or Levenshtein ≤1 (len ≥5) | `Supp0rt` vs `Support` → T; verified staff → F; stale roster → U |
| `address_token` / ask_jev | token boundary + RE2 pattern for EVM `0x`+40 hex (syntax, not validity) | 40 hex → T; 39 → F |
| `link_risk` / ask_jev | registrable domain in admin shortener set OR IDN/confusable of admin-owned domain; no network deref | shortener → T; trusted → F; parse fail → U |
| `solicitation` / ask_jev | within 80 chars: one contact/DM phrase AND one wallet/verify/claim/airdrop/urgent term (versioned dictionaries) | "DM me to verify your wallet" → T; "DM me about lunch" → F |
| `first_link` / ask_jev | prior accepted posts == 0 AND ≥1 URL (counter complete) | 0 posts + URL → T; 7 posts → F; incomplete → U |
| `repeat_burst` / ask_jev | SHA-256 of normalized text; ≥3 events by same author in distinct channels within 10 min | 3 channels/8min → T; same channel → F |
| `question_shape` / draft_context | final `?` or interrogative first token (ignore code/quotes) | "How do I join" → T; "status update" → F |
| `faq_exact` / draft_context | normalized n-gram vs admin FAQ aliases; exact or ≥0.8 Jaccard (3-grams), top match separated by ≥0.15 | exact alias → T + FAQ-7; tie → U |
| `unanswered_age` / draft_context | minutes since root question with no qualifying human answer; T ≥60min | 90min → T; staff replied 12min → F |
| `new_member_silent` / dashboard_only | joined ≥24h and <7d, zero public posts (no inference of reading/DMs) | 48h/0 posts → T; 8d → F |
| `backlog_growth` / dashboard_only | unanswered >60min roots, trailing 24h minus prior 24h; T if Δ≥5 AND current ≥10 | 12 vs 6 → T; 8 vs 2 → F |

## Composition: facts → question → band → action

1. Validate origin/event ID; compute signals with pinned bundle. **Exact admin deny match → quarantine for review immediately** (Jev not asked to override).
2. Else build a small packet (fired signals + evidence, UNKNOWNs, matched FAQ + approved citation, policy version). Jev answers distinct binaries: `is_this_suspicious_solicitation?`, `can_answer_from_approved_source?`, `needs_human_review?`. **Do not sum booleans into a magic risk score**; Jev confidence is not calibrated probability by default.
3. **Policy is a deterministic reducer:** DENY/QUARANTINE if exact deny fires; DRAFT if any abuse signal + Jev suspicious, Jev requests review, any required signal UNKNOWN, or no approved answer source; **AUTO only** for low-impact FAQ reply when citation unique + Jev answerable/not suspicious + policy allows + idempotency passes. Jev unavailable/contradicts evidence → DRAFT, never AUTO. Health signals = dashboard only.
4. `FALSE` signals must not veto Jev's independent concern; Jev cannot overrule exact admin deny; admin `never_auto` wins over everything.

**Worked routing:** first post "DM me to verify your wallet at https://go.example/x" from 2h-old account → member_new/solicitation/first_link/link_risk all T → **DRAFT with reasons** (no auto-ban). Veteran asks "How do I connect my wallet?" + unique FAQ-7 → can AUTO-reply **only if policy permits FAQ auto**. Missing message-content permission → UNKNOWN → no auto-reply.

## Evolution, replay, receipts

- Proposal record (source: admin override / false positive / backlog audit; new predicate/threshold; owner; failure hypothesis; examples). No self-editing live predicates; human approves.
- **Freeze labeled replay cases before tuning**, split by author/thread/time (no near-duplicate leakage); include multilingual, obfuscated URLs, innocent lookalikes, benign wallet talk, missing inputs, edits, retries, out-of-order. Track FP/FN, abstentions, latency p95/p99, queue-size change; review every false hard-block. Shadow-run proposed bundle before activation.
- **Receipts:** immutable bundle hash + per-signal versions (incl. Unicode confusables, PSL, FAQ, roster), Jev prompt/model version, policy version, snapshot revision, all results + missingness, Jev verdicts with cited refs, reducer trace, band/action, human override, rollback ref. Redact message content/addresses/credentials in logs; minimal restricted evidence with admin-set retention.
- **Rollback** atomically to prior bundle/policy; queued cases keep the bundle that decided them; new release = new decision, never rewrites old receipts. UI "why?": exact facts fired, those missing, Jev Q/verdict/citation, policy clause, who approved, what changed.

## Failure guards

Adversarial wording/homoglyphs → bounded evidence + evasion sampling · false positives → reversible quarantine only for exact admin rules · stale thresholds/roster → expire snapshots → DRAFT · contradictory inputs → show conflict → DRAFT · expensive normalization → input caps + RE2 · missing coverage → explicit UNKNOWN + no auto. Alert on **fire-rate/unknown-rate/override/lag changes**, not just accuracy.

## Hackathon build order

Implement `SignalDefinition`/`SignalResult` + snapshot builder + reducer first; then `first_link`, `solicitation`, `question_shape`, `faq_exact`, `unanswered_age` + fixtures. Seed admin FAQ, staff roster, deny list. Demo: normal FAQ auto-reply → suspicious DM draft with receipt → admin override → replay into candidate v0.2. Dashboard metrics + confusables sophistication on the roadmap. **Do not claim measured precision, autonomous learning, or cross-platform coverage until tested.**
