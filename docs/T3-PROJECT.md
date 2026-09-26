# T3 PROJECT — Calibrated Community Operator (LOCKED)

> Track 3 — AI Community Agent · Locked 2026-09-26 · Form submitted by user · Buildathon: Sep 26, 09:00–17:00 IST.
> This is the canonical project brief. All other research is archived in `docs/archive/`.

## Product in one line

A community health operator that runs the weekly loop — **listen → answer → escalate → report → digest** — with **Jev as the decision layer** (calibrated confidence per action) and **Swytchcode as the tool broker** (policy block + audit trail). Thesis: *automation where it's safe, judgment where it matters.*

## Merged build (locked)

1. **Operator (product):** weekly loop over Telegram (+ Discord optional) → Jev scores → gates route → Swytchcode executes allowed writes → Notion report → Resend digest.
2. **Raid Rehearsal (stage peak):** a scam variant held back from the fixture corpus is posted live; Jev scores it on screen; policy quarantines in seconds while a genuine question is answered in the same beat.
3. **Trust ramp:** 10-second cold-open visual — wk-05 draft-only → 9/10 approvals → auto-send unlocked.
4. **The gate that learns (the edge):** every human approve/reject/edit tunes the Jev thresholds per community; the stage moment is the **override counter** — "asked 20 times, you overrode 6, next week 4 fewer."
5. **Trend digest (3 cards max):** trend + why-for-us + ready-to-post draft, from trendsapi.ai / trend-pulse / HN Algolia (cached; never live on stage).

## Live decisions (2026-09-26 morning, with the user)

- **Shape:** thin Telegram + Discord bots over **one shared LangGraph state machine** (`observe → classify → gate → escalate → resolve → learn`); bots thin, intelligence in the graph.
- **Jev:** the brain inside each state hop, **not the state owner** — LangGraph owns deterministic auditable transitions; Jev fires only where judgment is needed and writes a one-line reason per state switch.
- **Record store LOCKED: Notion** — system of record + admin surface (events ledger, quarantine queue, member trust history, 90-day pattern view) and the demo surface.
- **Quarantine flow:** Jev returns action + confidence + reason; high confidence acts immediately; low confidence → Notion quarantine queue; admin resolves with one tap; resolution written back as a labeled example; confidence stored from day one.
- **Data plane:** SQLite local over ngrok, single access path enforcing per-user scope, RLS-ready schema (Postgres later moves policies as-is); no Supabase. Retention: raw 7d + derived 90d.
- **Epic spine (5):** 1) Ingress: Telegram + Discord bots · 2) Gate engine: LangGraph states + Jev hops + confidence · 3) Admin surface: Notion ledger + quarantine · 4) Identity + data security (site auth links Telegram identity; single access path; RLS-ready) · 5) Svelte web front (auth surface + per-community telemetry dashboard).

## Demo (2.5 min)

Number+pain ("6-hour report → 60 seconds") → cold open (staged community + last week's report + trust-ramp visual) → live run (genuine question → Jev scores → answer posts) → guardrail beat (scam → Jev flags → policy block exit 4 → Slack escalate card) → close (report in Notion + digest via Resend, number proven). Optional: invite a judge to post a real question.

## Architecture

- **Planner:** LLM (drafts answers/digest) · **Decision layer:** Jev (typed scores + confidence; cannot plan) · **Tool broker:** Swytchcode (policy + exec + audit; "confidence is not proof of authorization").
- **Orchestration:** LangGraph (Python), nodes: ingest → jev_score (batched) → route → answer/policy_gate → escalate → aggregate → report → digest.
- **Event contract (reasoning-visible):** `thought` / `tool_selected` / `exec_started` / `exec_result` / `decision` / `action`.
- **Memory tiers:** run state (working) · Notion report pages (short-term) · supermemory graph (long-term, container per community).

## Integrations & verified actions

| Role | Provider | Action (verified) |
|---|---|---|
| Listen (primary) | Telegram | `telegram_v5_0.getupdate.create` |
| Answer | Telegram | `telegram_v5_0.sendmessage.create` |
| Quarantine | Telegram | `telegram_v5_0.deletemessage.create` |
| Escalate | Slack | `slack.chat.postmessage.create` |
| Report | Notion | `notion.page.create` / `notion.page.update` / `notion.block.update` |
| Digest | Resend | `resend.emails.send` |
| Optional second surface | Discord | `discord.message.create` / `discord.message.get` / `discord.message.delete` |

**Free-tier stack:** Telegram (free) + Slack free + Notion free + Resend free (100/day) + Discord free + Jev pennies (~₹4/M tokens). **Paid lines to state honestly:** Swytchcode Pro ~₹2,770/mo for custom policies (or honest fallback); Resend Pro past 100/day. **Excluded:** X (pay-per-use), WhatsApp (not in registry).

## Constraints (from the brief)

Agentic framework required (LangGraph chosen) · ≥3 Swytchcode APIs chained output-to-action · reasoning-visible interactive demo · policy guardrail · judging: Swytchcode 30 / technical 25 / innovation 20 / functionality 10 / impact 10 / UX 5 · submission: public repo, README, architecture diagram, setup instructions, demo, Commudle.

## Open decisions

- [ ] **PRFAQ headline wording (user):** insight version ("moderation, management and insight, in one entity") vs growth version.
- [ ] **Supermemory mode:** self-host (no key/cost) vs cloud free tier.
- [ ] **Planner keys:** Groq key (+ optional Gemini) to be created and validated.
- [ ] **`swy login` refresh** when we add methods.
- [ ] Demo surface detail: Svelte console scope (reasoning stream + report + policy history + quarantine queue).

## Doc map

- Rules & house rules: `hackathon-ground-rules.md` · Track definitions: `hackathon-tracks.md`
- Build plan: `build-plan-t3.md` · T3 build brief: `research-t3-build-brief.md` · Edge design: `research-t3-edge-design.md`
- Demo prep (omp): `research-omp-t3-demo-prep.md` · Customer evidence: `research-omp-v2-pains.md` · Edge critique (omp): `research-omp-edge-critique.md`
- Design/taste: `research-v2-final-candidates.md` · Free-tier audit: `research-free-tier-audit.md` · Framework: `research-deepseek-framework-matrix.md`
- Fixtures: `fixtures/maple_nest/`, `fixtures/jev_gates.yaml` · Core modules: `app/` · Bridge: `bridge/` · Comms CLI: `scripts/comms`
- Archived (v1 pipeline, other-track ideation): `docs/archive/`
