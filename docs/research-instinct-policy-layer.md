# Instinct — Swytchcode Policy Layer Deep-Dive (catalog, entitlements, demo wiring)

> Source: Instinct bridge post, 2026-09-26 ~12:55 IST ("BEADLE / T3 — Swytchcode policy layer deep-dive"), reply to our policy REQ; identical content also arrived as email id 68008. All claims verified against live docs pages (fetched ~12:55 IST; sources at end). Distilled by `deepseek-research-1`. Companion: `docs/research-omp-swytchcode-policy-and-wiring.md` (O49).

## 1. Verified / corrected / refuted

**Verified:** `swy policy add/list/remove/validate`; file at `.swytchcode/integrations/policies.json`; policies evaluated before every execution (blocked request never reaches the provider); nested `all/any/not` hand-edited + validated; `target` = canonical IDs; all six policy doc pages load.

**Corrected:** operator list is bigger — `==`, `!=`, `>`, `>=`, `<`, `<=` · `in`, `not_in` · `contains`, `not_contains` · `starts_with`, `ends_with`, `matches` (regex ≤512 chars) · `exists`, `not_exists`, `empty`, `not_empty` · `before`, `after` · `between`, `outside` (exactly two timestamps).

**Refuted:** `QUOTA_EXCEEDED` / `RATE_LIMITED` are **not** policy action types (reference lists only `POLICY_BLOCKED` and `AUTH_FAILED`; validate rejects others). `REQUIRES_APPROVAL` is **disputed inside Swytchcode's own docs** (human-approval page documents it; overview + best-practices say the engine only allows/blocks) and is **plan-gated anyway → treat as unavailable**.

## 2. Catalog — what the layer can express

- File defaults: `on_violation: "fail"`, `evaluation: "pre_execution"` (only supported values).
- Policy = `{ id, target: [canonical IDs], when: condition, action: { type, message } }` — all four required; duplicate id replaces.
- Leaf condition `{ field, operator, value? }` evaluates **resolved request arguments**; presence operators take no value. Groups nest.
- **Fail-closed + one gap:** missing file = no policies, execution continues (never delete the file); valid = evaluated; malformed = execution stops with a validation error.
- On `POLICY_BLOCKED`: request never sent; message returned to caller. Docs say exit 4 — verify once locally with a real block; if it differs, demo without quoting the number.
- **Cannot express:** no allow-with-logging mode; no quota/rate counting (no cross-request state); no current-time functions (time operators compare a timestamp *field in the request*); no approval action on our plan; no preset/template policies documented; doc examples cover GitHub/Stripe/Postgres only — adapt patterns.

## 3. Entitlements (pricing, fetched live)

| Plan | Execs/mo | Logs | Policy features |
|---|---|---|---|
| Developer $0 | 10,000 | 7-day | **"No custom policies"** (FAQ repeats it) |
| Pro $29 | 100,000 | 30-day | Allow / Deny |
| Business $149 | 1,000,000 | 90-day | Allow / Deny / **Human approval**; BYO OAuth; RBAC |
| Enterprise | custom | custom | Custom approvals, SSO, audit export |

**The tension to handle honestly:** CLI docs describe `policies.json` as a local, version-controlled file evaluated pre-execution with a local audit log ("works without Cloud Sync") — while pricing says custom policies are paid. Likely reading: local-file evaluation vs cloud-managed policies, never stated explicitly. **So: prove enforcement locally before the demo.** Configure one `POLICY_BLOCKED` rule, trigger it, capture the block + its `swy audit policy` entry. If it blocks: "policy evaluated locally, pre-execution; the request never left the machine." **Never claim a cloud or plan entitlement.**

## 4. Defensible free-tier policy set for Beadle

- **Layer 0 — tooling.json least privilege** (strongest, free, documented): don't enable destructive methods at all; an untrusted tool never reaches policy evaluation. Show `swy list tooling`.
- **Layer 1 — 3–5 `POLICY_BLOCKED` guards, each provable with a dry-run pair:**
  - destructive-op backstops on any enabled write method (`when: { field: "<field every request has>", operator: "exists" }`);
  - Resend: malformed recipient blocked (`not` group wrapping `matches` email regex ≤512 chars);
  - Discord: missing channel target blocked (`{ field: "<channel id arg>", operator: "not_exists" }`);
  - Notion: missing parent blocked (`not_exists`).
  - **Misfire warning:** a rule keyed on a field name that isn't exactly the tool's request argument silently never fires. For every rule: pull real arg names from the tool schema, then `--dry-run` twice (should-trip + should-pass) and keep both traces. **Prefer `not_exists` guards over `exists`-based allow logic** (optional fields make the latter fire wrong).
- **Layer 2 — Beadle's gate** (ours, honestly labeled): DENY/UNKNOWN routing, quarantine queue, thresholds, everything semantic. Split to present: *Swytchcode = deterministic pre-execution guards on canonical IDs + local audit trail; Beadle = judgment + the human queue.*

## 5. Demo wiring for the 30% (~40 seconds)

1. `swy policy list` — "Every request passes these guards before any network call."
2. `swy policy validate` — machine-checked config; malformed file stops execution instead of silently passing.
3. **Live block** → terminal shows our message, request never sent → `swy audit policy -n 5` shows the fresh violation entry. **Rule → blocked attempt → audit entry = the honest proof trace.**
4. Contrast run: the passing request executes (`--demo` if no account connected).

**Safe language (word for word):** "Policies are evaluated before every execution; a blocked request never reaches the provider API." · "This runs on the free Developer tier; cloud-managed policies and approval workflows are paid features we deliberately did not depend on." · "Judgment calls — the UNKNOWN cases — go to Beadle's own quarantine queue. That is our human-in-the-loop."
**Never say:** "Swytchcode enforces our policies in the cloud" · "the platform holds risky actions for approval" · or quote exit 4 / rate-limit enforcement not observed locally.

**Approval flow:** not usable on our plan (Business); and even on a paid plan it hurts a 2.5-min demo (a held command waits on a click in another app). **Our in-product quarantine queue is the better HITL story.**

## 6. Production guardrails worth showing cheaply

`swy list tooling` (least privilege) · `swy doctor` / `--network` (config + network hygiene) · `swy auth status` / `whoami` (managed OAuth, no hardcoded keys) · `swy audit stats` + `audit network -n 20` (observability) · `manifest.json` retries/timeouts/idempotency (only claim what we configured) · pinned versions (show the config) · concurrency (app-side setting).

## 7. Recommendation (Instinct's, marked as such)

Wire **3–5 policies max**: two destructive-op backstops, two field-validation guards on the real chain, one domain allowlist only if free text flows into a send. **Prove each with a dry-run pair today.** Stage weight on the **block-plus-audit pairing** and the honest entitlement line. *Judges reward a team that knows exactly where the vendor's layer ends and theirs begins.*

## Sources (fetched 2026-09-26 ~12:55 IST)
docs.swytchcode.com: policies/overview · policies/policy-rules · policies/human-approval · policies/production-guardrails · policies/best-practices · configuration/policy-json · swytchcode.com/pricing
