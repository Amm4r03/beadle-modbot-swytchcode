# Free-tier API Audit — Swytchcode Platform + T3/T6 Chains

Date: 2026-09-26 (~01:00 IST) · Source: email reply 67955; PDF `~/Downloads/Free-tier-API-audit.pdf`. Every claim cited to provider pricing/docs.

## The conceptual point (evidence)

Swytchcode = **execution layer, not an API provider.** Registry pages state you provide your own credentials once and Swytchcode stores/refreshes them ([/apis/telegram](https://www.swytchcode.com/apis/telegram)). It adds: manifests/schema, auth handling, input validation, idempotency-keyed retries, policy enforcement with signed audit, version pinning, `--demo`/`--dry-run`/`--explain`, MCP exposure, typed exit codes (4 = policy blocked). It does NOT provide the provider account, rate limits, or usage costs. **"Swytchcode lists it" says nothing about cost — the provider's pricing page is the only cost truth.**

Directory-wide per-provider audit of all ~325 integrations was **not feasible overnight** (JS-rendered listing); the audit covers both candidate chains + Jev fully, and sets the rule: verify provider pricing before designing.

## Cost-model categories

- **Truly free/open:** Telegram Bot API.
- **Free tier sufficient for hackathon + early product:** Slack, Notion, Jira, Gmail/Drive, Resend (caps noted).
- **Sandbox/test-mode free:** PayPal sandbox, Stripe test mode.
- **Pay-per-use, no free tier:** X/Twitter (free tier closed to new signups Feb 2026), Jev (fractions of a rupee/call).
- **Swytchcode itself:** free 10k execs/mo; custom policies Pro-only $29/mo (~₹2,770).

## T3 chain

| Provider | Cost model | Free limits | Auth | Call |
|---|---|---|---|---|
| Telegram | Truly free | ~30 msg/s bot-wide, ~20/min per group | Bot token; privacy off or admin to read groups | **usable-free** |
| Slack | Free forever | 90-day history; ~1 msg/s/channel | Bot OAuth | **usable-free** |
| Notion | Free plan | ~3 req/s; share pages with integration or 404 | Integration token | **usable-free** |
| Resend | Free tier | 100 emails/day, 3,000/mo | API key; test sender | **usable-free-for-demo** (Pro $20/mo past cap) |
| X | Pay-per-use | None (closed to new signups) | OAuth | **avoid** |
| Gmail/Drive | Free | 250 quota units/s/user | OAuth | usable-free (not needed for T3) |
| Jev | Tiny paid meter | $0.042/1M input tokens, output free | API key | **usable, ~₹4/M tokens** — say "fractions of a rupee," not "free" |

**T3 all-free stack:** Swytchcode free + Telegram + Slack free + Notion free + Resend free (+ Jev pennies). Honest paid lines: Swytchcode Pro for custom policies (the guardrail feature), Resend Pro past 100/day.

## T6 chain

| Provider | Cost model | Free limits | Call |
|---|---|---|---|
| PayPal | Sandbox free; production per-transaction 3.49% + fixed | Sandbox test accounts | **usable-free (sandbox)**; fees-on-revenue in prod |
| Gmail | Free | 250 units/s; consumer daily send caps | **usable-free** |
| Slack | Free forever | as above | **usable-free** |
| Jira | Free forever ≤10 users | 100 automation runs/mo, 2 GB | **usable-free** |
| Notion | Free plan | as above | **usable-free** |

**T6 all-free stack:** Swytchcode free + Gmail + Slack free + Jira free + Notion free + PayPal **sandbox**. Production cost = PayPal per-transaction fee out of revenue.

## Shared caveats

- **Policy block is Pro-tier.** Both demo designs anchor on it: expense ~₹2,770/mo or run the honestly-labeled two-layer beat (Jev gate + exit-code-4 `--dry-run` block).
- **`--demo` doesn't cover T3/T6 write actions** (documented only for stripe/fintech-compliance) → live-but-staged fixtures, not demo-mode simulations.
