# Submission Checklist — verified vs hackathon rules (no push)

Owner: `omp-research-2` · Date: 2026-09-26 · Task: REQ #69. Sources: ground rules §7, T3-PROJECT, repo state observed tonight. Do NOT push anything.

## Items

| Item | Required? | Status | Evidence / gap |
|---|---|---|---|
| Public GitHub repo | yes | **partial** | local git on `main` (3+ commits); **no remote configured** (`git remote -v` empty) — user must create repo + `git remote add` + push. Tracked-file safety: `.gitignore` excludes `.env`, `.swytchcode/`, `data/`, `bridge/`, internal docs; secret scan of docs/app/fixtures/api clean (only false-positive prose matches) |
| README | yes | **ready** | `README.md` present: product, loop, architecture table, demo moment. Verify setup/run section covers env + login before submit |
| Architecture diagram | yes | **partial** | ASCII diagram in README + mermaid state graph shared earlier; no standalone diagram file — export one (mermaid → PNG/SVG) before submit |
| Setup instructions | yes | **partial** | `.env.example` present; README covers partially. Gap: single copy-paste quickstart (install → login → seed → run → demo) not yet consolidated |
| Demo (live or recorded) | yes | **partial** | runbook + fixtures + backup-video plan exist; live chain proven (Notion/Slack/Resend 200 in proof file). Gap: backup video not yet recorded; `/test` view + announce paths need verify-live |
| Commudle entry | yes | **missing (user action)** | only the user can submit; needs repo URL + video link first |
| ≥3 Swytchcode APIs, output-to-action | yes (30%) | **ready** | Notion → Slack → Resend live 200 in `chain-run-proof.json`, output-feeds-next; Telegram direct-API honestly separated |
| Agentic framework | yes | **ready** | LangGraph 6-node state machine in `app/graph.py`, smoke green |
| Reasoning-visible demo | strongly recommended | **ready** | event contract + SSE console + trace views per admin stories |
| Policy guardrail | yes | **ready** | 3 local policies with dry-run pairs + audit rows (`research-omp-policy-proofs.md`) |

## Rubric alignment (what to point at per weight)

| Weight | Criterion | Evidence |
|---|---|---|
| 30% | Swytchcode integration | 3-provider live chain + policy proofs + audit pairing + honest entitlement line |
| 25% | Technical | LangGraph state machine, two-file ledger, reducer, replay/resume, isolation tests |
| 20% | Innovation | gate-that-learns (override counter, Because-you-taught-me card), split-decision + Raid Rehearsal |
| 10% | Functionality | weekly loop end-to-end on fixtures + live legs; quarantine resolve writeback |
| 10% | Impact | sourced admin pain ($2–5K/mo, 6-hour reports), sit-beside wedge vs MEE6/Dyno |
| 5% | UX/Presentation | 2.5-min beats, graceful-denial copy, console stories A1–E2, backup video (pending) |

## Honest gaps (must close or disclose)

1. No remote / nothing pushed — user action, do last after secret re-scan.
2. Backup video unrecorded — highest-risk open item.
3. Architecture diagram file missing (ASCII only).
4. Quickstart not consolidated in one place.
5. Commudle entry needs repo URL + video.
6. Slack invite + Discord reconnect decisions affect the 3-provider claim — lock before stage.
