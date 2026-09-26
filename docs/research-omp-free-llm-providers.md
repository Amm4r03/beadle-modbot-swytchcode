# Free LLM Providers + Layered Fallback Utility (agent generation, not the gate)

Owner: `omp-research-2` · Date: 2026-09-26 · Task: msg 46 (REQ #46). Companion to O47 (gate insurance) — this doc is ONLY about the agent's own generation (answer drafts, reports, summaries/planner). No overlap: nothing here scores or authorizes.
Rule: staged inputs OK, fabricated outputs never. Proofs below are real responses observed tonight or labeled "needs key."

---

## 1. Live proof (tonight, this machine, sourced `.env` key)

- **Groq model list:** 11 models live, including `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `openai/gpt-oss-safeguard-20b`, `meta-llama/llama-prompt-guard-2-86m/22m` (prompt-guard models noted for signal-layer use, not generation).
- **Groq generation proof:** `gpt-oss-20b` chat completion returned 200 in **0.52s wall** (88 prompt / 80 completion tokens). Caveat observed: with `max_tokens: 80` the content landed in `reasoning`, `content` empty, `finish_reason: length` — truncation artifact of my small cap, not a model failure. Lesson for the client: set output ceilings with headroom for reasoning tokens.
- Keys present in `.env`: `GROQ_API_KEY` only. Everything else below is "needs key," stated honestly.

## 2. Provider table (free tier, doc-grounded where unkeyed)

| Provider | OpenAI-compatible? | Free tier (verify before relying) | Models for our jobs | Status tonight |
|---|---|---|---|---|
| **Groq** | yes (`api.groq.com/openai/v1`) | free tier per account limits; Developer-plan base table is NOT verified entitlement — check org Limits page | `gpt-oss-20b` (drafts), `gpt-oss-120b` (harder synthesis) | **PROVEN live** (list + generation) |
| **Gemini (AI Studio)** | yes (`generativelanguage.../v1beta/openai/`) | free tier exists; quotas per project; free-tier content may train models (data decision needed before member content) | `gemini-2.5-flash-lite` | needs key |
| **Cerebras** | yes (OpenAI-compatible) | free tier historically offered; limits unverified tonight (search throttled) | verify model list with key | needs key |
| **OpenRouter `:free`** | yes | free variants exist; numeric caps currently placeholder per token playbook | verify per-model availability | needs key (even free needs auth) |
| **Together / Mistral / GitHub Models / NVIDIA NIM / SambaNova / HF Inference** | mostly yes | all need keys; free tiers vary and churn | — | needs key; do not assume |
| **Cloudflare Workers AI** | yes (compat endpoint) | 10k neurons/day free; neuron costs are per-model, NOT tokens | verify per-model neuron math | needs account check |

## 3. Layered fallback design (one client, ordered chain)

```python
class GenerateRequest: role, messages, schema, input_budget, output_budget, data_class, idempotency_key
class GenerateResult: validated_output, input_tokens, output_tokens, finish_reason, provider, model, cache_tokens

CHAIN = [
  ("groq", "openai/gpt-oss-20b"),      # primary: proven, sub-second
  ("groq", "openai/gpt-oss-120b"),     # harder drafts, same key
  ("gemini", "gemini-2.5-flash-lite"), # secondary provider (after data approval + key)
]
```

- **Health/latency:** per-model circuit breaker (consecutive-failure count + p95 tracker); a model trips open after N failures, half-opens on a probe schedule. Swap-on-failure only (never round-robin — determinism for receipts).
- **Swap rule:** timeout/malformed → one retry within budget, then next provider with fresh validation. 400/schema = config error (stop, alert). 401/403 = stop + operator alert (not a quota incident). 429 → parse `Retry-After`, token-bucket admission, jittered bounded retries; generation only, never retry a side effect.
- **Audit:** every activation writes provider, model, versions, token counts, latency, reason for swap. Fallback running is a digest line ("drafts ran on fallback 14:02–14:19"), never silent — same circuit rule as O47.
- **Budgets:** per-call input/output ceilings (cut oldest raw events first; never policy, evidence, citations); reject on unavoidable overflow. Per token playbook: ~24.2k tokens/day/community target; cap ~6 communities on hypothetical quotas pending org verification.
- **Chain config location:** static order + model names in env (`LLM_PRIMARY`, `LLM_FALLBACKS`); learned per-community preferences (e.g., "120b drafts better for this community's tone") may live in `learned_config` LATER — never tonight. Chain membership is ops config, not learned state.
- **If no provider has budget:** queue the draft with a deadline, show the human-review packet, leave the message unanswered. Never send an untested model's guess.

## 4. Recommendation (two LLM jobs)

- **Answer drafting:** `gpt-oss-20b` → `gpt-oss-120b` (same key, harder fallback) → Gemini flash-lite (once keyed + data-approved). Strict JSON schema (`text`, `source_ids`, `uncertainty`, `escalate`), server-side validation every call.
- **Report/planner synthesis:** `gpt-oss-120b` first (longer synthesis deserves the bigger model) → `20b` → Gemini. Numbers computed outside the model; prose validated against metrics before publish.
- **What this is NOT:** none of these models score, gate, or authorize anything — O47 owns calibration. An LLM draft that fails validation becomes a human-review packet, never a send.
