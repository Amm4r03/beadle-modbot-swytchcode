# Instinct — Beadle Gate Wiring Note (state graph, signals, reducer, chain)

> Source: Instinct bridge post, 2026-09-26T06:51Z ("Beadle gate wiring note"), reply to our state-graph REQ. Distilled verbatim-in-substance by `deepseek-research-1`; thresholds and signal proposals are **design choices, not measured calibration** (Instinct's own caveat). Build input for Phase 1.

## Bottom line
- Keep a **small, event-scoped LangGraph state machine** + a **durable SQLite ledger**.
- **Rules compute observable signals; Jev judges only semantic ambiguity.**
- **Model calls never execute bot, Notion, or learning writes.**
- Thresholds below are **demo policies, not measured calibration**; our two-file split + 4 signals were treated as build-team assertions, not verified state.

## State and replay
- **Graph:** OBSERVE (normalize event, stable ID, dedupe) → CLASSIFY (SQL facts, regex; optional Jev semantic labels) → GATE (pure reducer, policy version, uncertainty) → RESOLVE (eligible safe action) **or** ESCALATE (quarantine + interrupt) → LEARN (only a verified human resolution becomes a labeled example) → END.
- After ESCALATE, **resume into RESOLVE, then LEARN**; **no edge from LEARN back to GATE** on the same event. Explicit routes for duplicate / invalid input / model timeout / provider failure / already-resolved. Every branch ends, waits for a human, or enters a **bounded retry** state. **No recursive classifier loop.**
- **State contains:** event ID, tenant/user scope, source, short redacted text or content hash, stage, signals, Jev outputs, decision, reason, policy version, retry count, checkpoint/ledger refs. **Not:** full message history, 90-day member history, API credentials, whole Notion pages.
- **Two stores, two purposes:** compact checkpoints in `checkpoints.db`; **append-only transition ledger** (from/to, one-line reason, actor rule/Jev/human, timestamp, policy/model version, input hash), signal observations, decisions, labels, outbox in `state.db`. **A checkpointer is not the audit ledger.**
- **thread_id = `tenant:platform:event_id`** (never one thread per community).
- **Replay:** ingress `UNIQUE(platform, community_id, provider_event_id)`; action key `event_id:policy_version:action_type:recipient`; commit decision + transition + unique outbox action in **one SQLite transaction**; a separate worker sends each external action, records provider ID/result, dedupes on replay. At-least-once exposure if the worker crashes after provider acceptance — use provider idempotency keys where available, otherwise reconcile provider state before retry (especially bot sends).
- **Never call an external API before an interrupt inside its node** (LangGraph can rerun the node on resume). Jev call lives in its own computation node; persist response with prompt hash/model version; **reuse the saved response on deterministic replay**. Recompute only in an explicit **counterfactual fork with sends disabled**.
- Read-only replay should match stored routing + reason for the same inputs, policy version, cached Jev answers. Explicit max: **1 model retry then review, 1 human wait, 1 terminal state**.
- **Metrics:** p50/p95 transitions per event, graph-state serialized bytes, time-to-action, dead-end count, retries, duplicate outbox attempts, replay-match %. No target numbers claimed as observed.

## Deterministic signal map (proposal; D = SQL/parser, J = Jev; priority order)
| # | Signal | Type/Stage | What it does | Guardrail |
|---|---|---|---|---|
| 1 | member_new | D · OBSERVE | Account joined within configured window (trusted member table) | Yes/no/UNKNOWN; unknown ≠ assume old. Context, not an auto-ban |
| 2 | first_link | D · OBSERVE | 0 prior scoped links + URL in current message | First-time link pushes review unless allowlisted |
| 3 | rate_burst | D · OBSERVE | Event count per member in policy window exceeds threshold | Missing history = UNKNOWN. Hard review trigger, not proof of spam |
| 4 | duplicate_payload | D · OBSERVE | Normalized text/link hash repeated across scoped members in short window | Count + window attached; quoted reposts need context |
| 5 | domain_allow_or_block | D · CLASSIFY | URL host vs versioned exact-domain lists | Parser failure UNKNOWN; explicit prohibited host is **veto**; allowlist lowers friction but never overrides other vetoes |
| 6 | known_trust_or_override | D · CLASSIFY | Scoped, unexpired human label/trust from SQLite | Missing UNKNOWN; explicit override wins within its scope; stale labels can't silently control new cases |
| 7 | solicitation | J · CLASSIFY | P(message seeks money/credentials/off-platform move), conditional on short text | Store p, confidence, model, prompt, reason; uncertain → review. Never regex the phrase alone into proof |
| 8 | question_shape | J · CLASSIFY | Genuine question vs solicitation disguised as one | Store calibrated probability + confidence; indeterminate → review; skip if no question-like text or veto already fired |
| 9 | impersonation_claim | J · CLASSIFY | Claims to be staff/official or unverifiable authority cues | High likelihood escalates; never infer true identity from the claim; skip if no identity cues |
| 10 | harmful_link_intent | J · CLASSIFY | What the link/CTA asks a person to do (wording only, not destination safety) | Ambiguous → review; URL reputation would be a separate deterministic external fact |
| 11 | policy_exception | J · GATE | Does scoped text fit a narrow exception from actual admin decisions? (retrieve max 2–3 labeled examples by FTS/vec) | p + confidence stored; **no learned exception may defeat an explicit block** |
| 12 | resolution_similarity | D + optional J · LEARN | Retrieval score vs scoped labeled examples (D); only if close-but-conflicting, ask Jev if a proposed label applies | **Never auto-promote an example into an active rule**; version draft, replay held-out examples, require admin acceptance |

**Boundary rule:** D when structured provider data, exact text/URL/SQL predicates, or explicit versioned policy fully determine the answer. J only when intent/contextual meaning can't be expressed reliably in predicates. **UNKNOWN is a first-class value, not 0.** A score is not a truth label. Reject model output lacking expected schema — never substitute 0 or "safe".

## Reducer (proposed policy, needs real labels)
- Order: **dedupe → explicit hard veto → scoped human override (if permitted) → known rule evidence → optional Jev labels → action band.**
- Hard veto always quarantines; missing required fact or unavailable Jev → **review**.
- Low-risk clean allow: no veto + required facts known + all relevant model answers **confidence ≥ 0.85 and risk ≤ 0.10**.
- High risk **≥ 0.70 → quarantine**; middle band → review.
- **No naive probability averaging** — store each question separately with provenance; a versioned rule matrix routes.
- First demo can avoid automatic destructive action entirely. Reason from a **fixed template** with decisive signal IDs + Jev's one-line explanation; never claim the explanation proves causality.
- **Jev budget:** zero calls on hard veto or deterministic allow; **one batched classify call** for ambiguous items (parallel typed questions on one short shared state, pinned model version); at most one exception call if candidate retrieval is relevant; 1 bounded retry on transient error, then review. Measure latency/tokens; promise no number.

## Swytchcode chain — rubric warning
- Docs prove Swytchcode supports enabled/authenticated tools, policy validation, schema checks, Notion/Discord integrations — **not** which operations are installed here. Telegram was not independently verified in its catalog.
- Realistic Discord-adapter demonstrator: **(A)** read scoped Notion policy/queue via a discovered Notion read op → **(B)** send an approved idempotent Discord response after GATE → **(C)** append/update the Notion events-ledger row via a discovered Notion write op. Three provider API calls chained on one event **if the rubric counts calls**.
- **If the rubric demands three distinct APIs/integrations, this chain does NOT meet it** — verify before claiming compliance. The Telegram adapter via direct Bot API **cannot count** as Swytchcode-mediated without a proven integration.
- First run `swy` local tooling list, discover/select, inspect schemas + auth, dry-run each exact operation, then record actual canonical IDs, outputs, provider IDs and three real traces. **No placeholder canonical ID is execution-ready.**

## Wiring order today (Instinct's recommendation)
1. SQLite tables, unique ingress key, policy version, transition ledger, outbox, 4 existing signals; **add a replay fixture before any bot mutation**.
2. Six graph stages with hard stop/review paths + SQLite checkpointer; test duplicate event, interrupt/resume, timeout, stale human resolution, simulated crash after sending.
3. Add deterministic signals 3–6, then **one Jev batched semantic call for 7–8** (9–10 only if time). Capture real usage + reasons. Keep 11–12 review-only until labeled tests.
4. Connect exact discoverable Swytchcode calls on the Discord proof path; project to Notion asynchronously; retain bot/API IDs in outbox. Validate the 3-call rubric question; demo actual traces, never mocked success.
5. Show two real human resolutions, a distinct third input, ledger trace, negative control; claim only learning the replay proves. End-to-end two-event retry + no-duplicate test before stage.

## Caveats (Instinct's own)
Sender assertions about stack/12-signal target/deadline are not verification of installed code. Thresholds are design choices; nothing proves calibration on Beadle data or validates the hackathon's exact three-API rule. Jev's third-party docs describe the API but must be checked against the actual TypeSafe endpoint/credentials.

## Sources (as posted)
docs.langchain.com (persistence, interrupts, use-time-travel, durable-execution) · docs.swytchcode.com (cli/exec, cli/commands, cli/agents, guides/execution-pipeline, quickstarts/langgraph) · swytchcode.com/apis/notion · swytchcode.com/apis/discord · jevtypesafeai.com/docs
