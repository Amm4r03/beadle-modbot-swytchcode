# Gateway Alternatives to Jev — Free-Tier Insurance (customer + build lens)

Owner: `omp-research-2` · Date: 2026-09-26 · Task: msg 45 (REQ #45), ASAP before Phase 1 gate wiring.
Context: Jev (`jev-1.13.0`) recovered after a 25-min 403 flake; this doc is insurance, NOT replacement.
Rule: staged inputs OK; no fabricated outputs. Curl proofs below are real responses observed tonight; failures reported as failures. Unsourced claims `[INFERENCE]`.

---

## What the gate actually needs (so alternatives are judged fairly)

Jev returns **calibrated 0–1 probabilities for custom natural-language questions** (scam? answerable? needs review?). A fallback must do the same job: custom questions + numeric scores + deterministic thresholds. Anything fixed-taxonomy-only is signal-layer material, not gate-capable — labeled as such below.

## Curl proofs (tonight, this machine)

| Candidate | Probe | Observed result |
|---|---|---|
| OpenAI omni-moderation | POST `api.openai.com/v1/moderations` (no key) | `invalid_request_error: Missing bearer or basic authentication` — endpoint live, needs key; free status unverified without one |
| HF Inference classic (`api-inference.huggingface.co/bart-large-mnli`) | POST zero-shot payload | connection failed (HTTP 000) — classic endpoint unreachable from here |
| HF router (`router.huggingface.co/hf-inference/...`) | POST zero-shot payload | returned an HTML login page, not JSON — router needs a Bearer token |
| Perspective (`commentanalyzer...?key=TEST`) | POST TOXICITY | 404 page (wrong path shape for v1alpha1 without key; endpoint family exists) |
| Groq `/openai/v1/models` (no key set) | GET with dummy key | `invalid_api_key` — expected; proves reachability, nothing about model list |

Honest summary: **no keyless JSON proof was obtainable tonight** for any candidate — every calibrated endpoint needs a credential this machine doesn't hold (except the Groq key, which lives with the build env, not here). The verdicts below are therefore doc-grounded, not curl-proven, and labeled accordingly.

## Candidate verdicts (doc-grounded, free-tier only)

| Candidate | Custom questions? | Scores? | Free tier | Verdict |
|---|---|---|---|---|
| **Groq structured-output judge** (we hold a Groq key) | ✅ yes (any prompt) | ⚠️ JSON yes, calibrated no | free tier per account limits | **RECOMMENDED PRIMARY FALLBACK.** Same provider, same key, zero new accounts. Honest gap: outputs are uncalibrated text/JSON — treat as ordinal signal with wider bands + mandatory human review on first week, never as drop-in calibrated probabilities |
| **Google Perspective API** | ❌ fixed attributes (TOXICITY, SPAM, etc.) | ✅ 0–1 scores, free API ([codelab](https://developers.google.com/codelabs/setup-perspective-api)) | free, but needs GCP project + access-form approval (up to 1h) | Signal-layer only (no custom scam question). Worth the form for SPAM/toxicity signals; not a gate |
| **HF zero-shot (BART-MNLI) via router** | ✅ yes (candidate labels) | ✅ entailment scores | free with HF token (rate-limited) | Viable second fallback for custom questions; needs token + latency test (BART-large is slowish, ~1-2s `[INFERENCE]`). Router token required — HTML without it (proven above) |
| **OpenAI omni-moderation** | ❌ fixed taxonomy | ✅ scores | free *with* API key (account needed); unverified keyless | Signal-layer only. Useful if an OpenAI key already exists; do not open a new account for it tonight |
| **Llama Guard / ShieldGemma / Granite Guardian on Groq** | ❌ fixed safety taxonomy | ✅ yes/no + categories | free under Groq key *if* the model is listed | Check model list with the real key; if present, best *safety* second opinion — but still not custom-question calibrated. Signal layer |
| **Gemini free tier as judge** | ✅ yes | ⚠️ structured output yes, probabilities unclear | free tier exists; data-use terms need a decision before member content flows | Possible third fallback; blocked on the data-use decision, not tech |
| **OpenCode Zen `jev-1.13-free`** | ✅ (same API) | ❌ errors server-side | n/a | Documented limitation: client-visible but server-erroring — do not wire it; note as known-bad |
| **Cohere trial / Azure Content Safety free / Lakera** | mixed | mixed | trial or card-gated | Excluded: trial-expiry risk mid-demo, or card required. Revisit post-hackathon |

## Recommended fallback wiring (insurance, behind one interface)

1. **Primary: Jev stays.** No change.
2. **Fallback 1 (same key): Groq structured-output judge** with widened bands (auto ≥0.92, draft 0.70–0.92, deny below) + `uncertain` default on malformed JSON + first-week human review on all auto-actions taken under fallback. The wider bands ARE the calibration honesty.
3. **Fallback 2 (needs HF token): BART-MNLI zero-shot** for custom questions if Groq is down too; latency-qualify first (must clear <2s p95 or it becomes draft-only).
4. **Signals regardless:** Perspective SPAM/TOXICITY (after access form) + deterministic signal bundle feed the reducer with or without any judge.
5. **Circuit rule:** any fallback activation is itself an audit event + digest line ("gate ran on fallback Groq-judge 14:02–14:19, bands widened, N auto-actions held for review"). The fallback must be visible, never silent.

## What NOT to use and why

- **OpenCode Zen `jev-1.13-free`:** server-side errors — known-bad, do not wire.
- **Fixed-taxonomy APIs as gate:** omni-moderation, Perspective, Llama Guard answer *their* questions, not ours ("is this impersonating MapleNest_Admin?"). Presenting them as gate-capable is fake work.
- **Trial/card-gated APIs:** a trial expiring mid-demo is worse than no fallback.
- **Heavy self-host / JVM / 258MB binaries:** violates the brief's API-first constraint; the laptop has enough processes.
- **Replacing Jev:** explicitly out of scope — it works (5/5 200s, scam 0.91–0.93 live). This doc is insurance only.
