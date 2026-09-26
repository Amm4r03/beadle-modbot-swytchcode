# Instinct — Adjustable Gate Thresholds (post-hackathon, future scope)

> Source: Instinct bridge post, 2026-09-26 ("adjustable gate thresholds, post-hackathon research"). FUTURE scope. Distilled by `deepseek-research-1`. Instinct caveat: code not inspected; `threshold_versions` + fixtures treated as proposed integration points.

## Bottom line
**Keep today's demo thresholds frozen** and describe them as an **uncalibrated starting policy**. Never claim learned thresholds, calibrated confidence, or measured error reduction.

| Approach | Fit | Main risk |
|---|---|---|
| Frozen per-category policy | ✅ correct for today's demo | no adaptation |
| Admin-approved bounded proposals | first post-demo step | human review cost |
| Automatic per-community tuning | only with enough independent labels | sparse data, feedback loops, gaming |

## Proposal governance (when we get there)
- **One small per-community, per-category change at a time, admin-approved.** Never auto-learn a global threshold from a few overrides — an override is evidence an admin disagreed with a particular action under a particular policy version, not the ideal boundary (admins disagree; only reviewed items are labeled; auto-handled mistakes may be invisible).
- Retain: original prediction, score, action, override, final resolution, policy/model version, timestamp, community. **Separate reversals of incorrect auto-actions from routine manual review** (count both, don't confuse).
- **Eligibility (conservative trial gate):** rolling 30–60-day window, ≥100 independently labeled relevant cases, ≥20 on each side of the proposed boundary, plus a separate **chronological holdout**. Rare base rate or conflicting labels → gather more, don't move. Decay/cap old examples only in the proposal set; keep raw labels immutable. Never train on the same cases used to declare a win. Ask admins to label a random sample of **auto-handled** cases too (else evaluation is biased to quarantined cases).

## Hard guards (proposed)
UNKNOWN / missing provenance / conflicting policy / unsupported evidence → **review regardless of any threshold**. No candidate may bypass explicit DENY, remove manual override, or exceed community scope. **No more permissive auto-decision in safety-sensitive categories without explicit admin approval.** Even tightening costs false quarantines → admin-approved upper bound on review load. Max **one approved step of 0.02** in score space per category per week within a preapproved band; outside the band = separately reviewed policy release. **If model or prompt changes → pause threshold learning and rebaseline.** One-click return to the last approved version stays.

## Evaluation protocol
Replay old vs proposed policy on the **same held-out, timestamp-later labeled cases**, stratified by community/category/channel. Record confusion counts, incorrect auto-actions / independently reviewed auto-actions, review load / eligible actions, admin reversals / reviewed actions; plot error vs automation coverage; check borderline, new-member, adversarial cases separately. **Override rate is a health signal, not accuracy.** Compare at similar automation coverage + review burden, with uncertainty intervals and per-category denominators. Freeze the holdout before proposing; never tune on fixtures. Shadow-run → small opt-in rollout with explicit admin rollback trigger (confirmed safety regression or review-load budget breach). Sparse labels → present counts as observations, claim nothing.

## Audit event per proposal/approval/activation/rollback
event ID · UTC timestamp · actor/admin ID · community + category · old/new policy version + exact boundaries · direction + stated reason · label-window + holdout IDs with counts · model/prompt version · comparison metrics + uncertainty · guardrail/fixture results · approver · effective time · rollback parent version. **Append-only record of failed proposals too.** Each decision references the exact policy version + cited case IDs so explanations replay without rewriting history.

## Limits
Neither Jev's confidence number nor a handful of overrides is a calibrated probability. "100" and "0.02" are **starting governance knobs, not statistical proof**. Today's demo line: **"frozen thresholds; feedback captured for later evaluation"** — never "self-tuning".

## Sources (as posted)
ACL 2021 (label bias) · arXiv 2208.12084 · scikit-learn calibration · NIST AI RMF playbooks (Measure, Manage) · MLflow model registry (illustrative) · NIST 2026 monitoring report
