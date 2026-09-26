# Agentic Framework Re-Evaluation (post-shape-change)

Date: 2026-09-26 · Context: the product shape changed to **thin bots over one shared LangGraph state machine with Jev hops** (observe → classify → gate → escalate → resolve → learn), agent-core-first on mock data, integrations later. This re-checks the earlier framework matrix against that shape. Decision: **LangGraph (Python) stays locked**; reasoning below.

## Criteria (weighted to the locked shape)
1. **Owns a deterministic state machine** (explicit states/transitions, auditable, not prompt-flow).
2. **State persistence + checkpointer** (crash recovery, resumable interrupts).
3. **Conditional routing** (output of one hop decides the next; Jev verdicts drive edges).
4. **Jev hop integration** (call typed questions between nodes; one-line reasons on transitions).
5. **Observability** (transition logs, streaming for the demo reasoning view).
6. **Python-first** with mature tooling (FastAPI/SQLite ecosystem).
7. **Free, no framework lock-in**, works with Swytchcode's CLI/SDK and our free-tier providers.
8. **Ecosystem evidence** (production use, Swytchcode quickstart support).

## Comparison

| Framework | Deterministic state machine | Checkpointer/interrupts | Conditional routing | Jev hops | Observability | Verdict |
|---|---|---|---|---|---|---|
| **LangGraph** | **Best** — graphs, nodes, conditional edges; state is a first-class object | **Yes** — persistent checkpointer, interrupts; documented restart semantics | **Yes** — edges on state/Jev output | Natural: call Jev inside a node; write reason to state | Transition log = the state; LangSmith optional (free tier) | **LOCKED** |
| Pydantic AI | Typed flows, graph support, but less explicit state-machine ownership | Partial | Yes (graph API) | Good (typed) | Logfire integration | Runner-up; strongest types, younger graph/checkpoint story |
| CrewAI | Role/task-based; flows exist but rigid/opaque | Weak | Limited | Possible | "Basic" per practitioner reviews | No — shape mismatch |
| OpenAI Agents SDK | Handoffs/guardrails; flow lives in prompts more than structure | Partial | Via prompts | Possible | Free tracing | No — not a deterministic machine |
| Vercel AI SDK | Multi-step loops (`stopWhen`), branching is yours | Partial (TS) | Yours to build | Possible | Excellent UI streaming | No — TS-first; our core is Python; keep for the Svelte surface only |
| Anthropic SDK | None — you write the while-loop | No | Manual | Manual | DIY | No — it's an SDK, not a framework |
| Google ADK | Newer, agent-first; state/checkpointing less proven for our pattern | Partial | Yes | Possible | Emerging | No — maturity risk in a one-day build |

## Why LangGraph wins for THIS use case
- The user's requirement — "LangGraph owns state so transitions stay deterministic and auditable; Jev is the brain inside each hop" — **is LangGraph's exact model**: nodes mutate a typed state, edges route on it, the checkpointer persists it, interrupts pause for human review (our quarantine queue).
- Jev hops are just node functions; the one-line reason is written into state and logged.
- The demo's reasoning view renders the state/transition log — no extra instrumentation framework needed.
- Swytchcode lists LangGraph first-class (quickstarts + cookbook examples).
- Crash/replay requirements (outbox, reconcile, resumable approvals) map to the persistent checkpointer + interrupt semantics.

## What we do NOT adopt
- No multi-framework mixing in the core (no CrewAI roles, no prompt-flow SDKs).
- Vercel AI SDK only if we ever want its UI streaming for the Svelte surface — not required (SSE from FastAPI is enough).
- No LangSmith dependency for the demo (optional dev aid; free tier only if used).

## Lock
**LangGraph (Python), single shared state machine, persistent checkpointer, Jev inside hops, transitions logged.** Framework evaluation closed; revisit only if the shape changes again.
