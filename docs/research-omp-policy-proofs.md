# D22 Policy Proofs — Free-Tier `policies.json` Set (proven live 2026-09-26)

Owner: `omp-research-2` · Task: REQ #64 package 1. All commands run on this machine; traces observed, failures reported as failures. Policies LEFT IN PLACE as the demo set.

## Rule 1 — Destructive-op backstop: `beadle-backstop-discord-delete`

- Config: `target: [discord.message.delete]`, `when: {field: channel_id, operator: exists}`, `action: POLICY_BLOCKED` ("Beadle guard: destructive delete blocked in demo").
- TRIP (should block) → `swy exec discord.message.delete --dry-run` with channel_id+message_id → **blocked**: `category: policy_denied`, `blocked by policy "beadle-backstop-discord-delete"`, no provider call. ✅
- PASS (untargeted method) → `discord.message.create` same args shape → resolved URL `POST https://discord.com/api/v10/channels/123/messages`, auth redacted. ✅
- Audit: `pol_1b51273d79 | discord.message.delete | beadle-backstop-discord-delete | blocked`. ✅

## Rule 2 — Resend subject guard: `beadle-resend-requires-subject`

- Config: `target: [resend.email.create]`, `when: {field: subject, operator: not_exists}`, `action: POLICY_BLOCKED`.
- ⚠️ CLI warning at add time: `field "subject" is not an input of the target tool(s)` — because `subject` lives inside `body`, not top-level args. **Yet the block FIRED anyway** (see below). `swy policy validate` repeats the warning but reports "valid (3 policies)". Field-path semantics vs evaluation semantics differ — evaluation evidently resolves nested paths even though the add-time checker doesn't. Flagged, not hidden.
- TRIP (no subject) → **blocked**: `category: policy_denied`, `blocked by policy "beadle-resend-requires-subject"`. ✅
- PASS (with subject) → resolved URL `POST https://api.resend.com/emails`. ✅
- Audit: `pol_f143d6fa25 | resend.email.create | beadle-resend-requires-subject | blocked`. ✅

## Rule 3 — Discord channel guard: `beadle-discord-requires-channel`

- Config: `target: [discord.message.create]`, `when: {field: channel_id, operator: not_exists}`, `action: POLICY_BLOCKED`.
- TRIP (no channel_id) → **input validation fires FIRST** (`missing required field "channel_id"`, category `validation`), policy never evaluated. No audit row. This is correct layering (validate → policy), but means the rule is **defense-in-depth only** — it can never trip before validation does. Stated plainly: the rule is harmless but unprovable via dry-run pair; its value is documentation + protection if the schema ever loosens. Kept in place, labeled as such.
- PASS (with channel_id) → resolved URL, green. ✅

## Audit surface

`swy audit policy` shows both blocks with IDs, timestamps, tool, policy, status. `swy policy list` shows all 3 rules; `swy policy validate` = valid (with the subject-field warning noted above). File lives at `.swytchcode/integrations/policies.json` — present, never deleted.

## Demo line (40s)

`swy policy list` → `swy policy validate` → trip Rule 1 live (block message on screen, no provider call) → `swy audit policy` pointing at the fresh row → contrast PASS exec. Safe language: "evaluated locally, pre-execution; Developer tier; judgment calls live in Beadle's own queue."
