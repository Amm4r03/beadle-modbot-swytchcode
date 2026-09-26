# LB-01 — Product & Delivery: what exactly are we building, and how does a manager use it?

> **Status: LIVING DOC — the running state of an open brainstorm. Stage 0. Last worked 2026-09-26.**
> Started from the user's instruction: think through what the product looks like, how a user actually uses it (CLI? extension?), the fastest way to build it so it just works, and how other communities integrate it. This note is **edited in place** as the discussion moves; it is the state of the thread, not a snapshot of one session. It is **not a spec, not a sprint plan, and not a decision.**
>
> **How to keep it:** every session appends a dated entry to *Discussion log*, moves settled items out of *Open questions* into the body with their **why**, and updates *Where this stands*. Every load-bearing number carries a date and a source.
>
> **Companions.** `docs/T3-PROJECT.md` (locked brief) · `docs/research-t3-edge-design.md` (edge design) · `docs/research-omp-supermemory.md` + `docs/research-deepseek-supermemory.md` (memory wiring) · `docs/research-omp-t3-demo-prep.md` (demo beats) · the deep customer-obsession pack (email 67964).

---

## 0. The question this answers

**The user's question:** "What is this product going to look like and how will a user actually make use of it? Is it a CLI, is it an extension? What exactly are we building, how are we scaffolding this? We need the fastest and best-fitting way to develop this so it just works — and a way that lets people integrate it into their systems for the benefit of their community."

> **Short answer so far:** the product is a **community operator that lives where the community already lives** — a hosted agent service with a chat-native presence (Telegram/Discord/Slack) plus a **minimal operator console** for the reasoning stream, report, and approvals. Managers never see a CLI; a CLI/npm package is a later power-user/self-host story, not the product surface. Fastest build: Python LangGraph service + FastAPI console + the already-verified Swytchcode actions (Telegram/Slack/Notion/Resend), single-tenant MVP.

---

## 0.5 Where this stands

| | |
|---|---|
| **Stage** | 0 — brainstorm |
| **Gate to stage 1 (PRFAQ)** | delivery form-factor confirmed; user journey confirmed; MVP surface confirmed; hosting approach confirmed |
| **Settled so far** | product definition (§1) · delivery comparison + recommendation (§3) · fastest scaffold (§5) |
| **Open so far** | 4 — see *Open questions* (delivery confirm, console scope, hosting, Discord/npm timing) |
| **Independent of the decision** | verified Swytchcode actions, fixtures, memory wiring design, demo beats — all usable under any delivery choice |
| **Blocked on** | the user's call on the four open questions |

---

## 1. What the product is

**One sentence:** a community operator that runs the weekly health loop — listen → answer → escalate → report → digest — with calibrated confidence gating (Jev) and governed execution (Swytchcode policy + audit), and a gate that learns from every admin override.

**Who the user is:** the community manager/admin (solo founder, CM team member, or agency running several communities) — the person from the research who leaves the modqueue to assemble context, answers the same question weekly, and reports with anecdotes instead of numbers.

**Job-to-be-done:** "Clear my queue the way I would, hand me the context I'd have gone looking for, and prove my impact upstairs — without becoming another platform I have to migrate to."

**What it does weekly (the product loop):** answer what it's sure of → escalate what it's not (with a pre-assembled packet) → publish the health report → email the digest (with 3 actionable trend cards) → learn from every approve/reject/edit.

---

## 2. Delivery options compared

| Option | What the user does | Build cost | Fit for managers | Demo strength | Verdict |
|---|---|---|---|---|---|
| **Chat-native operator** (bot lives in Telegram/Discord; Slack for escalations) | Adds the bot; approves via reactions | Low — no UI to build | High — where they already work | Medium — powerful but less visual | **Core of the product** |
| **Hosted web app / dashboard** | Signs up, connects tools, watches a dashboard | High — auth, hosting, full UI | Medium — yet another dashboard (their complaint) | High | Not the product; keep a minimal console only |
| **CLI (npm/pip)** | Installs and runs locally | Low | Low — managers don't live in terminals | Low | **Later story** (self-host/power users, publish on npm) |
| **Browser extension** | Installs into a browser | Medium | Poor — no natural host surface for community ops | Low | Reject |
| **Hybrid: chat-native + minimal console** | Bot in the community; console for reasoning/report/approvals | Medium-low — console is one page + SSE | High — product lives in chat, console only when needed | High — the console renders the reasoning stream judges must see | **Recommended** |

**Why hybrid:** the research says managers want to stay in their community, not adopt another dashboard ("tools that measure but never act" is the runner-up shameful gap). The console exists for two reasons only: the reasoning-visible demo requirement, and the weekly report/approval surface when a chat message isn't enough.

---

## 3. Recommended delivery (draft for confirmation)

**Packaging — what it is, concretely (settled direction):** it is **a bot app you install into your community + a web console + weekly emails.** Not a browser extension; not a CLI for managers.
- Telegram: a bot added to the group (made admin so it can read).
- Discord: a bot invite, like MEE6/Dyno/Carl-bot.
- Slack: an app installed to the workspace.
- Console: a web URL (reasoning stream, weekly report, gate history, settings).
- Email: weekly digest + escalation summaries (Resend).
- Under the hood: a hosted backend (agent worker + memory + policy) the manager never manages. Later: npm CLI for self-hosters, not the manager surface.

**The product:** a hosted agent service. You connect it to your community once; it works in the background all week; you interact through chat (approvals, questions) and one console page (reasoning stream, report, gate-learning history).

**First-run (target <10 minutes):** add bot as admin → connect Slack + Notion + Resend (one-time tokens) → set 2–3 thresholds (defaults pre-filled) → first health report appears, populated with your unanswered questions and silent new members. First action asked of the manager: approve/reject one draft — the learning loop starts in minute one.

**Integration story for other communities:** bot install + workspace connect + thresholds + first report. Multi-tenant hosting and a scoped key per community come after the hackathon; the memory design already isolates per `community:{id}`.

**Later story (explicitly deferred):** an npm CLI (`npx community-operator init/connect/status`) for self-hosters and power users — publishable, but not the manager surface.

---

## 4. User journey (weekly)

1. **Monday digest** lands (email + chat): what was handled, what needs you, who's drifting, 3 things to run.
2. **Approvals** happen in chat (reaction on the escalate card) — each one feeds the gate.
3. **Community-facing answers** post from the bot; escalations go to the mod channel with the packet.
4. **Console** shows the reasoning stream live during any run and the report history.
5. **Over time:** fewer escalations, better answers, and the override counter proves it ("asked 20, overrode 6, next week 4 fewer").

---

## 5. Fastest path to "just works" (scaffold)

- **Service:** Python + LangGraph (nodes per the build plan) — no framework UI work.
- **Console:** one FastAPI page + SSE reasoning stream (pattern already proven by the bridge) — not a full dashboard.
- **Chat surfaces:** Telegram bot (listen/answer/quarantine), Slack app (escalation cards + approvals), Discord optional second surface.
- **Data:** Notion (reports/ledger), Resend (digest), supermemory (long-term memory; cloud free tier for demo, self-host fallback).
- **Execution:** Swytchcode for every write (verified action names) — no bespoke API glue.
- **MVP tenancy:** single community, single tenant; architecture leaves room for per-community containers/keys later.
- **Demo deployment:** local service + ngrok; hosted-ready architecture but not hosted for the hackathon.

---

## 6. Open questions (to resolve before anything is scoped)

1. **Delivery confirm:** hybrid (chat-native + minimal console) — yes, or does the user want a fuller web app for the demo?
2. **Console scope:** reasoning stream + report + gate history only (recommended), or add a dashboard?
3. **Hosting:** local + ngrok for the demo (recommended), or deploy to a cloud host before the pitch?
4. **Discord + npm CLI timing:** Discord in for the demo (recommended); npm CLI deferred to post-hackathon — confirm.

---

## 7. What this is NOT

- Not a spec, not an architecture doc, not a decision — those come after this thread closes.
- Not a dashboard product; the dashboard is the thing the research says managers already ignore.
- Not a moderation replacement or the community's system of record.
- Not a CLI-first product for managers (CLI is a later self-host story).

---

## 8. Discussion log

- **2026-09-26 — session 1 (product & delivery brainstorm).** Drafted from the user's instruction + the deep customer-obsession research. Product definition, five delivery options compared, hybrid recommended, user journey, fastest scaffold, integration story. Open: the four forks above.
- **2026-09-26 — session 2 (packaging + learning + enforcement).** Packaging settled: bot app + console + email digest. Added directions: self-updating config learning from decisions **and undos** (research dispatched: omp + Instinct/Karpathy), explainable retrieval of past decisions, spam ladder (warn→rate-limit→mute→ban) with size-based safe defaults, escalation cadences (immediate/daily/weekly), macro-narrative reports, cross-platform config schema + porting. Hosting: aim Vercel for console/webhooks; ngrok fallback; worker needs persistent compute. Resend rationale: durable forwardable digest + escalation email. Instinct tasked with Karpathy autoresearch + marketing; omp with metrics/publishability + learning design + cross-platform config.
- **2026-09-26 — session 3 (user decisions).** **Packaging CONFIRMED: bot** (Telegram/Discord/Slack) + console + emails. **Policy path locked: FREE** — our own gate blocks; Swytchcode policy layer shown via blocked `--dry-run` (exit 4), stated honestly; no Pro purchase. **Deployment:** ngrok now; Google Cloud Run / Cloudflare later as needed. **Dashboard:** deferred; later a small Svelte + local SQLite site on ngrok, deployable if time. **Policy visibility (new feature):** admins must see how policies changed over time — versioned NL-text+value diffs, why linked to overrides, one-click revert, digest line, Notion changelog. **Guardrail model confirmed:** NL policy text + value bands, evaluated by Jev (`instructions`/`criteria` → probabilities vs bands); Instinct designing schema + evolution. **Planner LLM:** user will supply an API key (opencode/muse spark suggested) to replace later. **Credentials:** list agreed (Telegram/Discord/Slack/Notion/Resend/trendsapi + planner key; Jev done & live-verified: jev-1.13.0, scam 0.96). **User departure:** only after epics + all stories are documented, so agents keep working on action items. Research in flight: Instinct (policy schema/evolution, competition battle, product names) · omp (competition, local testing, policy visibility).
- **2026-09-26 — session 4 (live decisions with the user, via Instinct).** **Architecture shape settled:** thin Telegram + Discord bots over **one shared LangGraph state machine** (`observe → classify → gate → escalate → resolve → learn`); bots stay thin, all intelligence in the graph. **Jev = the brain inside each state hop, not the state owner** — LangGraph owns deterministic auditable transitions; Jev fires only where judgment is needed and writes a one-line reason per state switch (judge-facing explainability). **Record store LOCKED: Notion** — system of record + admin surface (events ledger, quarantine queue, member trust history, 90-day pattern view) and the demo surface. **Quarantine flow:** Jev returns action + confidence + reason; high confidence acts immediately; low confidence lands in the Notion quarantine queue; admin resolves with one tap and the resolution is written back as a labeled example; confidence stored from day one (hi/lo thresholds encoded later). **Retention confirmed:** raw 7d + derived 90d. **Data plane:** SQLite local, exposed over ngrok, single access path enforcing per-user scope, RLS-ready schema so a Postgres swap later moves policies as-is; no Supabase. **Epic spine (5):** 1) Ingress: Telegram + Discord bots · 2) Gate engine: LangGraph states + Jev hops + confidence · 3) Admin surface: Notion ledger + quarantine · 4) Identity + data security: site auth links Telegram identity, single access path enforces per-user scope (RLS-ready) · 5) Svelte web front doubling as auth surface and per-community telemetry dashboard. **Open item:** PRFAQ headline wording is with the user — insight version ("moderation, management and insight, in one entity") vs growth version; awaiting his call. **Deck prep:** on track to start 14:00 IST; draft goes to the user for review.

---

## Sources — how this was produced

- User instruction, 2026-09-26 (bridge + chat): form factor, fastest build, integration, npm-later story.
- Deep customer-obsession research pack (email 67964, 2026-09-25): admin needs, time sinks, shameful gap, "sit on top of where the community already lives."
- `docs/T3-PROJECT.md` (locked build) · `docs/research-t3-edge-design.md` · `docs/research-omp-supermemory.md`.

---

## Revision log

- **2026-09-26** — Created. Supersedes nothing; first product/delivery thread.
