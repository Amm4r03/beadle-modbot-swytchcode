# Supermemory — How It Works & T3 Wiring (engineering lens)

Owner: `deepseek-research-1` · Date: 2026-09-26 (~02:30 IST) · Sources: supermemory.ai docs (memory-vs-rag, search/recall, graph-memory, how-it-works), GitHub repo. Part of the three-way supermemory study (with `omp-research-2` + email seat).

## 1. How it works (the routing/retrieval model)

- **Two layers, one search:** **Documents** = raw, stateless content (RAG chunks). **Memories** = extracted, stateful facts tied to entities/users, with temporal validity. Routing query: `Query → entity recognition → graph traversal → temporal filtering → context assembly`.
- **Hybrid search is the default call:** `search(q, containerTag, searchMode="hybrid", limit, threshold, rerank?, rewriteQuery?, filters?, include?)`. Hybrid returns both `memory` (facts) and `chunk` (document) results with similarity scores; `threshold` 0.5 default, `rerank` +~100ms, `include.relatedMemories`/`forgottenMemories` for extra context. Example response timing ~92ms.
- **Graph semantics:** memories connect via **Updates** (new fact supersedes; `isLatest` keeps search current, history kept), **Extends** (enrich), **Derives** (inferred facts). Automatic forgetting (time-based, contradiction, noise).
- **Dreaming:** after indexing, the memory model builds the graph; `dynamic` (default, groups related docs, higher quality) vs `instant` (single doc, for demos).
- **Isolation:** **container tags** scope everything per user/project — our per-community boundary.
- **Profiles:** static + dynamic context summary in one call (~50ms) — per-member context if we need it.
- **Run modes:** cloud API (`api.supermemory.ai`) or **fully local/self-hosted** (OSS repo; plugins/MCP exist). Pricing/free tier needs one check before we depend on cloud.

## 2. What lives where (T3)

| Layer | Store | Why |
|---|---|---|
| Working memory | LangGraph run state (messages, Jev scores, decisions, audit refs) | the live run; rendered on screen |
| Short-term | Notion report pages (this week's window, escalations, actions) | durable, human-facing, already in the chain |
| Long-term | **supermemory, container per community** (`community_maple_nest`) | norms, FAQ lorebook, member history, override outcomes |
| Decisions/policy | Jev gates + Swytchcode policy | never in memory; memory informs, it does not authorize |

## 3. Retrieval wiring (per node)

- **Answer drafting:** hybrid search (lorebook docs + norms memories), `threshold 0.6`, `limit 5` → LLM drafts → Jev confidence gate → post.
- **Escalation context:** search scam/pattern history with `include.relatedMemories` → the escalate card shows precedent ("similar lure seen Sep 8").
- **Weekly report:** query unresolved questions + recurring topics; write answered Q&A back as documents (FAQ growth); report cites sources.
- **Trend suggestions:** query member interests/topic history → filter trend cards to what THIS community cares about (the trend × community filter).
- **Gate that learns:** every approve/reject/edit writes an **override memory** (`type=override, message_class, verdict, score`); nightly job recomputes act/escalate thresholds per class from override history; the override counter reads from here.

## 4. Continual-learning flow (why it's not a gimmick)

```
message → Jev score → gate → action (or escalation)
        → human verdict (approve/reject/edit) → override memory
        → nightly threshold recompute → updated gates → fewer escalations next week
        → answered Q&As → FAQ documents → better answers next week
        → contradictions → Updates edges → stale lore retired automatically
```
Every loop compounds: the community's norms become retrievable, the thresholds become calibrated to its tolerance, and the report proves the curve ("asked 20, overrode 6, next week 4 fewer").

## 5. Limits, risks, fallbacks

- **Not the source of truth** for policy/audit (Swytchcode + Notion are); memory informs decisions, never authorizes them.
- **Stage latency:** queries are fast (~100ms) but demo should pre-warm; fallback = fixture cache if memory is slow.
- **Failure mode:** if supermemory is unavailable, the loop degrades to Notion-only context (still works, less smart) — say so honestly if asked.
- **Cost/mode:** prefer **self-hosted OSS** for the hackathon (free, no key); cloud pricing to be verified before production claims.
- **Never** put secrets/credentials in memories; never let memory override Jev gates or policy.

## 6. Integration sketch

`LangGraph node: retrieve_context` (before answer/report/trend nodes) → `supermemory.search(container=community, ...)` → context into the LLM prompt; `node: record_learning` (after human verdict) → `supermemory.add(memory, metadata={type:"override"...})`; nightly `node: recalibrate` → read overrides → update `jev_gates.yaml` thresholds → log changelog to Notion.
