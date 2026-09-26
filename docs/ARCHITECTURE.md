# Beadle — Architecture

```mermaid
flowchart LR
    TG[Telegram] --> O
    DC[Discord] --> O
    O[observe] --> C[classify: 8 deterministic signals + 1 batched Jev call]
    C --> K{knowledge retrieval + nested Jev check}
    K --> G{gate: pure reducer}
    G -->|AUTO| D[draft: answer from cited docs]
    G -->|DRAFT| E[escalate: quarantine card]
    G -->|DENY| L[learn]
    D --> R[resolve: outbox]
    E --> R
    R --> L
    R --> SWY[Swytchcode exec]
    SWY --> NO[Notion report]
    SWY --> SL[Slack escalation + reasoning log]
    SWY --> RE[Resend Beadle Agent digest]
    O -.-> DB[(state.db ledger)]
    C -.-> DB
    K -.-> DB
    G -.-> DB
    D -.-> DB
    L -.-> DB
    DB --> API[read API :8788 + SSE]
    API --> UI[Svelte admin console]
    API --> TEST["/test agent journey view"]
```

Planes:
- **Agent plane** — LangGraph: observe → classify (signals + Jev) → knowledge check → gate → draft/escalate → resolve → learn. Every transition carries a one-line reason; every decision stores prompt version + hash, model, result status.
- **Data plane** — SQLite WAL: `state.db` (inbox, normalized events, signal runs, decisions, transitions, outbox, overrides, thresholds, token usage, audit, knowledge docs + FTS5) and `checkpoints.db` (LangGraph, disposable).
- **Execution plane** — outbox → `swy exec` verified methods only; live chain Notion → Slack → Resend; Telegram on the direct Bot API (documented bundle blocker).
- **Surfaces** — Notion (reports), Svelte console (admin), `/test` + `/live` (agent journey), Slack (reasoning log), demo.html (walkthrough).

Full flow + thresholds: `demo.html`, `docs/T3-PROJECT.md`, `docs/EPIC-SPINE.md`.
