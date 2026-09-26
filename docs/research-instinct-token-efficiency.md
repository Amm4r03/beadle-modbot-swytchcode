# Beadle Token-Efficiency Playbook (Instinct)

Date: 2026-09-26 · Source: email 67977. Engineering targets, not observed provider usage. Verify account-specific quotas before treating any provider as primary.

## Decision

Keep routing, scam-rule matches, dedup, rate/health counters, policy selection, and send/deny/escalate **deterministic**. LLM only for: a bounded draft, a synthesis that needs language, or a *proposed* policy change. The model never causes a side effect on its own. Groq's public 30 RPM / 1,000 RPD / 8K TPM / 200K TPD row is a **Developer-plan base table** — check the org Limits page; Gemini quotas are per project in AI Studio.

## Call / no-call map

| Stage | LLM? | Guard |
|---|---|---|
| Incoming event (idempotency, fingerprints, signals) | No | Persist evidence + signal version; near-dup must not suppress a changed claim |
| Policy/Jev (typed predicates, bands) | No (model may draft offline) | Versioned reason card; unsafe → review |
| Answer | Yes only if a new NL response is needed | Cite source IDs; deny unsupported claims; review against policy |
| Escalation | Optional single summary | Raw evidence links preserved even if summary fails |
| Digest/report | Optional one synthesis per batch | Numbers computed outside the model; validate prose against metrics |
| Policy proposal | Optional wording draft | Admin approval + replay + version/rollback; never auto-activate |

**Retrieval contract:** partition by community/source permissions; policies+FAQs separate from event history; top 3–5 cited chunks under a **400–600 input-token cap**; **150–250-token rolling summary** with last-seen event ID; raw refs kept for mismatch audit. Benchmark supermemory retrieval vs keyword/hybrid before trusting it for safety decisions.

## Token tactics (with tests)

1. **Fixed prefix first** (stable instructions + tiny JSON schema + policy version), mutable context last; Groq auto-caches prefixes (2h expiry; cached tokens usually don't count toward limits) — log actual `cached_tokens`.
2. **Zero-shot typed output first** against 30–50 adjudicated cases; add ≤1–2 counterexamples only if FP/FN metrics improve.
3. **Strict JSON schema** (`text`, `source_ids`, `uncertainty`, `escalate`, `additionalProperties:false`) — shape, not correctness; validate server-side per provider.
4. **Separate input/output ceilings**; cut oldest raw events first (never the current event, policy, safety evidence, citations); reject on unavoidable overflow rather than silent truncation.
5. **Cache only exact-safe renderable answers** keyed by policy/source versions + TTL; semantic matches = draft suggestions; invalidate on policy/source/community/fact changes; batch repeats after dedupe; never stream a draft into the public channel before validation.

## Budget (targets, per community)

Assumes 100 msgs/day → 15 answer drafts (850/220), 4 escalation summaries (1,000/280), 1 daily digest (1,500/400), 1 weekly report (2,000/600), 2 policy proposals/week (2,200/550) ≈ **24.2k tokens/day average** (~170k/week). Under the hypothetical 200k TPD: cap at **six such communities (~145k/day)** with 25% reserve; the **8k TPM** cap can be hit by ~7 concurrent drafts. Actual org caps may differ. Gemini capacity = per-project AI Studio numbers; RPD resets Pacific midnight; free-tier content is used to improve products (data-policy decision needed).

## Routing & fallback contract

Adapter: `generate({role, model_id, messages, schema, input_budget, output_budget, data_class, idempotency_key}) → {validated_output, input_tokens, output_tokens, finish_reason, provider, model, cache_tokens}`. Persist event, source IDs, policy/schema versions, model, idempotency key in our store. Priority: deterministic/template first → Groq `gpt-oss-20b` (low-risk) → `gpt-oss-120b` (harder drafts) → Gemini `gemini-2.5-flash-lite` (data-approved secondary) → Cloudflare Workers AI (neuron budget) / OpenRouter `:free` (unstable caps). **If no approved model has budget: queue the draft, show a human-review packet, leave unanswered — never send an untested model's guess.**

429 → parse `Retry-After`, token-bucket admission, jittered bounded retries; **never retry a side effect** (generation only). Timeout/malformed → one retry within deadline/budget, then approved fallback with fresh validation. 400/schema = config; 401/403 = stop + alert. Circuit breakers per model; defer weekly reports/policy proposals first.

## Acceptance & failures

Replay 7 days with token counters, cache-hit rate, p95 (daily + 1-min), 429s, duplicate events; count reasoning/schema overhead/retries/shared org traffic. Quality: unsupported facts, wrong community/citation, over-escalation, missed scams, malformed JSON on adjudicated cases — same cases across models. Privacy: redacted metadata by default; block cross-community retrieval and semantic-cache reuse; confirm provider training/retention per community policy. Overflow: keep raw refs; summary that omits a rule-triggering fact → human review. Outage: deterministic moderation + evidence packets continue; drafts queue then expire/hand off; test failover with a synthetic event + idempotency key.
