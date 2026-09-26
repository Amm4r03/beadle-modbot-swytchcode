# T3 Build Brief — Integrations, Chain Wiring, Desirability (Email Research Agent)

Date: 2026-09-26 (~00:40 IST) · Source: Instinct email reply 67952 (PDF on file locally). Track choice treated as unverified by the agent until the user confirms.

## Integration table (registry-verified)

All seven slugs HTTP 200: telegram, slack, notion, resend, x, gmail, google-drive. **Registry pages do not publish action names** — enumerate after login with `swy get <name>` then `swy exec <provider>.<action> --explain`. Auth/constraints from provider docs:

| Provider | Auth | Key constraints | Role in T3 |
|---|---|---|---|
| Telegram | Bot token (BotFather); privacy mode must be disabled or bot admin to see group messages | ~30 msg/s bot-wide, ~20/min per group; inbound via getUpdates or webhook | Primary surface: read planted question + scam, post answer |
| Slack | Bot OAuth scopes; Socket Mode avoids public URL | chat.postMessage ~1 msg/s per channel; mrkdwn | Escalation surface: escalate-with-context card |
| Notion | Internal integration token; **pages must be explicitly shared or 404** | ~3 req/s; block-based content | Artifact store: weekly report page |
| Resend | API key; use shared test sender for demo | Free: 100/day, 3,000/mo | Digest email closing the loop |
| X | OAuth, paid read tiers | Firehose unrehearsable | **Cut** — optional color only |

**Setup checklist (60–90 min, before code):** login → `swy get telegram slack notion resend` + enumerate actions → `--explain`/`--dry-run` per action → Telegram staged group + bot (privacy off/admin) + plant two messages → Notion page shared with integration → Resend key + test sender → Slack test workspace + token.

**Chain:** minimum Telegram → Slack → Notion; ideal + Resend. Decision points: Jev confidence decides answer-vs-escalate; policy decides act-vs-block; report content decides digest. Jev gates; Swytchcode executes.

## Critical flag — the policy-block beat

Demo mode covers only stripe/fintech; a telegram.* policy block **cannot** run in `--demo`. Options: (a) expense Pro (~₹2,770/mo) for real custom policies; (b) demonstrate the block via **exit code 4 on a deliberately-blocked `--dry-run`**; (c) show the two-layer design with the gate in our LangGraph layer while Swytchcode executes allowed writes. **Do not fake it.** Decision needed tonight.

## Demo design (2.5 min)

Number+pain → cold open on live staged group + last week's report → live run (question → Jev scores on screen → answer posts) → guardrail beat (scam → blocked → Slack card) → close on the number proven (report + digest). Rehearse with `--dry-run`; fallback is a narrated `--explain` walkthrough over the same fixtures.

## Desirability playbook (applied)

- Start from pre-existing budgets (6-hour reports; $3–5K/mo manager replacement) — undercut demand, don't create it.
- First value on real data in minutes; loop-based retention; measure desire not usage (Ellis "very disappointed" ≥40% at week 4).
- **Wedge = the weekly report, not moderation.** Read-only value day one; moderation is the upsell after trust. Demo story: observe → report → earn trust → act.
- **Tells another manager:** the escalate-with-context card — the agent admitting uncertainty usefully.
- **Do-not-build:** dashboard that never acts; X leg; sentiment scores; onboarding flows; auto-moderation without the gate; settings pages.
- **First-run target:** connect a group → report populates in <10 minutes.
