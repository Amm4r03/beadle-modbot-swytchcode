# Decision Register — Beadle (T3)

> Every WHAT-level decision lives here with an explicit status. **User-locked** = the user said it. **Proposed** = drafted by an agent, awaiting the user's sign-off (do not treat as final). **Open** = no decision yet. Last updated 2026-09-26.

| # | Decision | Status | Source / notes |
|---|---|---|---|
| D1 | Track: T3 AI Community Agent → Beadle | **User-locked** | user + form submitted |
| D2 | Packaging: bot (Telegram/Discord) + console + email digest | **User-locked** | LB-01 session 3 |
| D3 | Policy path: free tier (no Swytchcode Pro; guardrail via our gate + blocked dry-run, labeled) | **User-locked** | session 3 |
| D4 | Framework: LangGraph | **Proposed — awaiting sign-off** | re-evaluation filed (`research-framework-reevaluation.md`); user asked to evaluate all frameworks |
| D5 | LangGraph SDK: **Python** (core); JS SDK not used (Svelte is UI only) | **Proposed — awaiting sign-off** | this register |
| D6 | Shape: thin bots over one shared LangGraph state machine; Jev inside hops, not state owner | **User-locked** | session 4 (via Instinct) |
| D7 | Record store: Notion (system of record + admin surface) | **User-locked** | session 4 |
| D8 | Quarantine flow: Jev action+confidence+reason → high acts / low queues → one-tap resolve → labeled writeback | **User-locked** | session 4 |
| D9 | Retention: raw 7d + derived/audit 90d | **User-locked** | session 4 |
| D10 | Data plane: **single SQLite instance (WAL), no Postgres** | **User-locked** | user, 2026-09-26 |
| D11 | Notion write path: notion-sdk-py for ledger + Swytchcode for one showcased write | **Proposed — awaiting sign-off** (grill: all writes via Swytchcode?) | omp stack doc |
| D12 | Auth: signed-cookie sessions (single admin) | **Proposed — awaiting sign-off** | omp stack doc |
| D13 | Memory layer: **sqlite-vec + FTS5** behind a `MemoryStore` interface — supermemory dropped (258MB server + LLM pipeline duplicates Jev); Neo4j rejected (JVM server, overkill); LanceDB/Neo4j are documented later swaps | **Proposed — awaiting sign-off** | `research-instinct-memory-layer.md` |
| D14 | Planner keys: Groq primary + Gemini fallback | **Proposed — awaiting sign-off** | user to add keys |
| D15 | Console scope: reasoning stream + report + policy history + quarantine queue | **Open** (gate 0→1 fork) | LB-01 |
| D16 | Deployment: laptop + ngrok only today; no cloud host/DB | **Proposed — awaiting sign-off** | TECH-STACK |
| D17 | Build priority: agent core on mock data first; integration epic later | **User-locked** | user, 2026-09-26 |
| D18 | PRFAQ headline: insight vs growth version | **Open** | with the user |
| D19 | WOW artifact: ONE "Because you taught me" case card (initial disposition → admin override+label → later distinct case → retrieved example IDs → Jev reason → gate score+threshold → one-click correction); language = "learning from decisions"; never show raw confidence as calibrated probability | **Proposed — awaiting sign-off** | `research-instinct-wow-factor.md` |
| D20 | Demo sequence: cold case → teach twice → new case trace → negative control + correction → evidence view (2.5 min, clocked) | **Proposed — awaiting sign-off** | same doc |

## Standing rule
No WHAT-level decision is treated as final without an entry here marked **User-locked**. Agents may propose; the register records the proposal and waits.
