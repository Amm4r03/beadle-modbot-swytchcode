# Build Plan — Calibrated Community Operator (T3)

Owner: `deepseek-research-1` · Date: 2026-09-26 (01:00 IST) · Status: ready to build pending track confirmation + Swytchcode login.
Inputs: `docs/research-v2-final-candidates.md` (design), `docs/research-omp-t3-demo-prep.md` (beats), `fixtures/maple_nest/*` + `fixtures/jev_gates.yaml` (omp), smoke test findings (below).

## Merged design v2 (confirmed by both agents, 2026-09-26 — O19)

- **Product:** Calibrated Community Operator (weekly loop, as below).
- **Stage peak — Raid Rehearsal:** mid-demo, post a scam variant **held back from the fixture corpus**; Jev scores it on screen; policy quarantines in seconds while a genuine question is answered in the same beat. Pre-validate the variant offline; keep a second fallback variant; honest framing: "held back from the fixture corpus."
- **Trust ramp (10-second cold-open visual):** wk-05 draft-only → 9/10 approvals → auto-send unlocked; pays off when the split decision fires.
- **Trend engine (pending email-seat research):** digest gains a "next week" section — trend × community-topic × member-history → ONE drafted activity with why-now evidence, effort, reversibility; rejected trends shown as the filter-proof beat. Sources cached (trendsapi.ai free 100/mo + HN Algolia); never live on stage.
- **Alternate:** Refund Court (T6) only if PayPal+Gmail credentials exist before Hour 1.
- **Verified action names (Section 0 done):** Telegram `telegram_v5_0.getupdate.create` / `sendmessage.create` / `deletemessage.create`; Slack `slack.chat.postmessage.create`; Notion `notion.page.create` / `notion.page.update` / `notion.block.update`; Resend `resend.emails.send`; Discord `discord.message.create` / `discord.message.get` / `discord.message.delete`.

---

## Product in one line

A community health operator that runs the weekly loop — listen, answer, escalate, report, digest — with **Jev as the decision layer** (calibrated confidence per action) and **Swytchcode as the tool broker** (policy block + audit trail). Stage thesis: *automation where it's safe, judgment where it matters.*

## Demo beats → code mapping

| Beat (2.5-min script) | What runs | Modules |
|---|---|---|
| 0:00–0:20 Number + pain | Static slide: "6 hours → 60 seconds" | — |
| 0:20–0:50 Cold open on the artifact | Show wk-07 Notion health report already populated | `report.py` |
| 0:50–1:40 Live run: split decision | MSG-A genuine question → Jev scores (0.88) → auto-answer posted; MSG-B scam → Jev scam_p 0.93 → Swytchcode policy block → quarantine + warning + mod-queue card | `graph.py`, `jev_gate.py`, `swytchcode_tool.py` |
| 1:40–2:00 Guardrail beat | The blocked action rendered as a receipt: what/why/where + audit line | `events.py` (UI feed), `audit` output |
| 2:00–2:30 Number proven | Digest lands in Notion + Resend email | `report.py`, `swytchcode_tool.py` |

## Architecture

```
fixtures/maple_nest (demo feed)  ─┐
live Telegram/Slack (real mode)  ─┤
                                  ▼
                          LangGraph graph (Python)
   listen → score (Jev) → route (gates) → act (Swytchcode exec) → report → digest
                                  │
              ┌───────────────────┼────────────────────┐
              ▼                   ▼                    ▼
      Jev decision layer   Swytchcode tool broker   Event emitter
      (typed scores +      (tooling.json policy,    (SSE/JSONL feed for
       confidence; no       exec, audit trail;       the reasoning-visible
       text, no tools)      confidence ≠ auth)       UI: thought /
                                                     tool_selected /
                                                     exec_started /
                                                     exec_result /
                                                     decision / action)
```

**Roles (sourced Q&A line):** Planner = LLM (writes replies/digest prose) · Decision layer = Jev · Tool broker = Swytchcode policy + exec. *"Even when Jev returns high confidence, the tool broker re-checks — confidence is not proof of authorization."*

## Repo layout (target)

```
app/
  graph.py           # LangGraph nodes + conditional edges
  jev_gate.py        # loads fixtures/jev_gates.yaml; calls Jev (live) or replays fixture scores (fallback)
  swytchcode_tool.py # wraps `swytchcode exec <id> --json`; emits exec events; captures audit
  events.py          # event contract (thought/tool_selected/exec_started/exec_result/decision/action)
  report.py          # Notion report + Resend digest composition
  demo.py            # demo driver: plays the staged Telegram pair on cue
  server.py          # minimal SSE endpoint + prompt UI (if web demo)
fixtures/maple_nest/  # omp's seed data (done)
fixtures/jev_gates.yaml
docs/                # this plan + research trail
```

## Build order (hackathon hours)

1. **Hour 0 (first 30 min after login):** `swytchcode get telegram slack notion resend`; `swy info` / `swy exec <action> --explain` for each action the chain needs; `swy add method` the trusted set; write `policies.json` for the public-send and scam-quarantine gates; verify sandbox vs production mode.
2. **Hour 1:** `events.py` + `swytchcode_tool.py` (wrapper + JSON parsing + exit-code handling) + `jev_gate.py` (fixture replay first, live Jev second).
3. **Hour 2–3:** `graph.py` — the five nodes + conditional routing per gates; wire the staged pair.
4. **Hour 3–4:** `report.py` — Notion page + Resend digest from the fixture week.
5. **Hour 4–5:** `demo.py` + reasoning-visible feed; rehearse the full 2.5 minutes twice; record backup video.
6. **Hour 5–6:** polish, README, architecture diagram, setup instructions; submission checklist.
7. **Buffer:** judge Q&A prep (calibration caveats, confidence≠authorization, model pinning, what we cut).

## Setup requirements (user actions)

- `npm install -g swytchcode` + `swytchcode login --open` (blocker for `get`).
- Test accounts per participant note: Telegram bot token, Slack app/webhook, Notion integration token + page, Resend API key. All free tiers.
- Jev: TypeSafe API key (user has access); pin model version.
- Custom policies caveat: Pro tier or script the block via demo mode — decide after checking `swy policy` behavior on the free tier.

## Smoke-test findings (already validated)

- CLI v2.23.7 via `npx`; `.swytchcode/` auto-scaffolds; `mode: sandbox`.
- `exec stripe.create_payment --demo` → success, exit 0.
- **Demo coverage is narrow:** only `stripe.create_payment` + `fintech.compliance`. T3 APIs have no demo mode → use app-level fixture replay for stage safety; real test accounts for live mode.
- `get <provider>` requires login; `policy` commands exist locally; `doctor` passes with warnings (no providers declared, no permissions boundaries — we should add `permissions.network` and `SWYTCHCODE_TOKEN` for CI later).

## Risks & fallbacks

| Risk | Fallback |
|---|---|
| Telegram/Slack/Notion action IDs differ from expectations | Fixture replay drives the loop; Swytchcode exec is exercised on whatever verified actions exist; show `--explain` for the blocked call |
| No live Jev key at demo time | Fixture scores replay (labeled "recorded decision" honestly) |
| Custom policy blocked by tier | `--demo` scripted block + explain; say so if asked |
| Venue Wi-Fi | Pre-recorded backup video of the full run |
| Fixture parsing brittleness | omp's seeds are already normalized JSON/MD |

## Open decisions

- [ ] Track confirmation (recommendation: T3) + form submission by user.
- [ ] Swytchcode login + provider fetch (user).
- [ ] Jev API key + pinned model string (user has access).
- [ ] Demo surface: minimal SSE web UI vs terminal feed (recommend web UI for judges; terminal fallback).
