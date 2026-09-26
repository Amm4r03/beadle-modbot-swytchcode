# Supermemory × T3 — Customer/UX Angle (omp-research-2)

Date: 2026-09-25 (evening) · Task: msg 28 follow-up (supermemory wiring, UX lens).
Grounded in primary docs read tonight: [how-it-works](https://supermemory.ai/docs/concepts/how-it-works) (pipeline + dreaming dynamic/instant), [graph-memory](https://supermemory.ai/docs/concepts/graph-memory) (Updates/Extends/Derives, forgetting), [memory-vs-rag](https://supermemory.ai/docs/concepts/memory-vs-rag) (memory = who-state over time, RAG = static knowledge), [container-tags](https://supermemory.ai/docs/concepts/container-tags) (hard namespace isolation + scoped keys), [quickstart](https://supermemory.ai/docs/quickstart) (conversation + document ingest, three retrieval modes). Rest `[INFERENCE]`.

---

## 1. What lives where: memory vs Notion vs run state

The rule, in customer terms: **Notion is what happened, memory is what it means, run state is what is happening now.**

| Store | Holds | Example (MapleNest) | Why there |
|---|---|---|---|
| **Run state (LangGraph)** | this week's live flow: messages, gate scores, pending approvals | MSG-A answered / MSG-B held (routing to be validated with live Jev once the key lands) | Ephemeral, per-run; judges watch it move |
| **Notion** | the auditable record: reports, ledger rows, policy versions | wk-07 report, trust-ramp table, audit `#a3f9` | Human-readable, manager-owned, survives us |
| **Supermemory** | evolving understanding: member patterns, topic mastery, gate history | "rose questions now auto-answerable (9/10 approved)"; "priya_grows: activated wk-07, whitefield, tomatoes" | Temporal + relational; RAG would return stale text, memory returns *current state* |
- One `containerTag` per community: `community:maplenest`. Isolation is enforced by container tags at the vector-namespace level (separate index per tag) — the stage line says exactly that, never "impossible." Enforcement depends on passing the tag, so all memory access goes through one hard wrapper (`search(container=...)` only, no raw calls) that asserts the tag every time.
The failure to avoid: duplicating Notion into memory (two sources of truth) or querying memory for static facts (use the lorebook/RAG path). Memory answers **"what do we know about X *now*?"** — nothing else.
**Self-host vs cloud (H2):** until self-hosted parity for dreaming modes + review APIs is verified in the smoke test, assume NO parity — derive-approval folds into our own override/review queue (which we're building for the learning gate anyway). Cloud remains a fallback only if a key + cost line clears before Hour 1.

## 2. Per-community scoping (non-negotiable)

One `containerTag` per community: `community:maplenest`. Isolation is at the vector-namespace level (no shared index), so cross-community leakage is architecturally impossible, not policy-promised — say that sentence on stage if asked.

- Scoped API keys per community (read/write per tag) for any multi-community future; 403s enforced at the data layer.
- Hierarchical tags (`org:acme:community:maplenest`) reserved for the agency/multi-client story — mention as one line, don't build.
- PII rule: member handles are facts, wallet addresses/DM contents are quarantined metadata — never ingested as memories `[INFERENCE: policy choice]`.

## 3. When the agent queries memory (four call sites)

1. **Answer drafting:** before replying, hybrid search — lorebook chunks (RAG: what do docs say) + member/topic memories (who is asking, what worked before). The answer cites both.
2. **Escalation context:** the #mod-queue card includes memory — "similar to Sep-08 incident; this handle pattern quarantined before; 9/10 rose answers approved." The mod decides in seconds.
3. **Weekly report:** profile + memory traversal generates "what changed" (promotions, retirements, newly-mastered topics) — the report writes its own delta section.
4. **Trend suggestions:** trend candidates filtered against community-topic memories ("gardening relevance 0.9; gaming 0.02 — rejected 6"). The reject list is the trust beat.

Latency note: `dreaming:"instant"` for demo paths (graph now, +1 op cost), `dynamic` in production. Never query memory synchronously on the 3-second stage beat — pre-warm; memory enriches, fixtures decide `[INFERENCE: perf call]`.

## 4. Stage-embarrassment failure modes (pre-empt each)

1. **Stale memory contradicts the live demo** ("roses are draft-only" but wk-06 approved them) → pre-demo memory audit: query every claim the script makes; re-ingest corrections with `instant`.
2. **Cross-fixture bleed** (test community's facts in MapleNest answers) → single container tag in demo env; assert tag in every search call.
3. **Overconfident derive cited as fact** ("Alex likely works on payments" stated flatly) → low-confidence derives gated through memory-review (approve/decline API exists); script only cites approved memories.
4. **Empty-memory cold start** (fresh container, nothing to retrieve) → seed + dream fixtures the night before; onboarding beat *shows* the first memory forming (that's the delight, not the risk).
5. **Latency stall on a live query** → memory calls are enrichment, never on the critical path; every stage beat has a fixture fallback per H1.

Latency note: `dreaming:"instant"` for demo paths (graph now, +1 op cost), `dynamic` in production. Memory enriches, fixtures decide — EXCEPT one live moment (H3): when the mod approves the escalated card on stage, the override memory writes live and the override counter ticks on screen. That single live write is the "it learns" proof; everything else pre-warmed.
- Low-confidence derives never cite directly: our own override/review queue is the gate of record (H4 — no dependency on unverified review endpoints); supermemory stores outcomes as `type=override` metadata.

Ship memory as **visible evolution, not infrastructure**: the trust-ramp page gains a "what I learned" section (promoted/retired facts with counts), the digest gets one line ("I now answer rose questions solo — you approved 9/10"), and onboarding ends with the first memory forming live. The manager *feels* the trainee-become-colleague arc. Never expose graph jargon (Updates/Extends/Derives) in UI — those are engineering words; the UI says "learned," "changed my mind," "retired."
