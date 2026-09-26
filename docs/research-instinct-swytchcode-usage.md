# Instinct — Making Best Use of Swytchcode for Beadle (policy, execution, demo)

> Source: Instinct bridge post, 2026-09-26 ("Beadle / Swytchcode T3 — policy, execution, demo"), reply to our Swytchcode REQ; identical content also arrived as email id 68007. Distilled by `deepseek-research-1`. Companion: `docs/research-omp-swytchcode-policy-and-wiring.md` (O49, local verification). Reconciliations noted inline.

## Bottom line
- Use Swytchcode for **real, traceable cross-provider execution** — but keep Beadle's **DENY/review gate in the application on the free plan**.
- Instinct **could not verify a public Track 3 rubric** requiring "three APIs" to mean three distinct providers. **Three distinct providers is the safer interpretation, not a confirmed rule** — ask the organizer.

## Policies and demo risks
- Pipeline: resolve enabled tool (`tooling.json`) → input schema check → evaluate policies (`policies.json`) → resolve auth → execution rules → provider call.
- **Free-plan entitlement:** Developer ($0) **excludes custom policies**; Pro ($29/mo) lists allow/deny controls; human approval is listed on Business. **Do not advertise a Swytchcode-enforced custom DENY policy on free.**
  - *Reconciliation with O49:* local `swy policy add/list/remove/validate` commands do run on this machine, but per pricing the *custom policy entitlement* is Pro. Safe line: **DENY/UNKNOWN is Beadle's own gate before `swy exec`** — log the decision, show that **no provider call was attempted**.
- **Exit-code conflict in Swytchcode docs:** the public exec page labels exit 4 as policy-blocked; the agent guidance page labels it network failure. **Never substantiate a policy-block claim from a bare exit code** — use the structured error category + the actual audit record.
- Terms: no bypassing policy/rate-limit controls; **no public RPS cap found — don't invent one**; keep concurrency low, back off only on retryable throttling/network errors, make writes idempotent. **Dry-run does not prove provider delivery.**

## Free-tier wiring facts
- **Developer plan: 10,000 executions/month**, managed OAuth, all public integrations, **7-day logs**, community support, no credit card. Schema checks, policy checks and audit logging carry no separate charge.
- Each `swy exec` is an execution. **Save real run IDs / provider response IDs**; inspect local audit stats/network before the demo.
- Modes to label plainly on stage: `--explain` (non-executing preview) · `--dry-run` (validation, no send) · `demo` (simulated output — say so).

## Three-call chain (Instinct's recommendation)
- **Discord message (via swy, real send) → Notion ledger page (via swy, citing the Discord message ID/link) → Resend digest (via swy, citing the Notion page ID/link).** Three distinct providers; each real output feeds the next call.
- Verify each exact canonical method, enabled tool, auth, schema and destination, and complete **a successful live run locally before claiming the chain**.
- If Discord has only passed dry-run, **the live three-provider chain is unproven** — say "validated in dry-run" until the real send.
- `Notion → Discord → Notion` = three calls but **two providers** — avoid betting the demo on that interpretation.
- Telegram via direct Bot API **does not count** as Swytchcode-mediated.
- *Reconciliation with O49:* O49's chain is `notion.page.create → discord.message.create → resend.email.create` (also 3 providers, dry-run green). Both satisfy the provider reading; pick the order during Phase 2 and live-verify the final one. O49's dry-run proofs stand as **validation**, not delivery.

## Honest demo lines
- Show the **actual gate decision**, the permitted execution chain, and **output IDs / audit traces**.
- Show DENY as **Beadle-side prevention**, not a vendor policy block.
- "Discord validated in dry-run" until a successful live response exists; simulated/demo output is not a real send.
- Two resolved examples illustrate a workflow — **not** learned accuracy, generalization, or safe unsupervised autonomy.
- Never imply Telegram's direct API is Swytchcode execution; **wired methods ≠ tested live calls**.

## Confirmed
- The one-shot **13:50 IST deliverables reminder is confirmed scheduled**: one email + one bridge POST.

## Open question for the user
- Ask the organizer (Commudle event page) whether "three APIs" in the Track 3 rubric means **three distinct providers**. No public source settles it.

## Sources (as posted)
swytchcode.com/pricing · swytchcode.com/terms · docs.swytchcode.com/policies/overview · docs.swytchcode.com/configuration/policy-json · docs.swytchcode.com/policies/production-guardrails · docs.swytchcode.com/guides/execution-pipeline · docs.swytchcode.com/cli/exec · docs.swytchcode.com/cli/agents · commudle.com (Knotic event page)
