# Policy Schema, Competitive Battle & Names — Instinct Research Pack 3

Date: 2026-09-26 (~02:40 IST) · Source: email 67968. All claims sourced in the original. Distilled for build use.

## ASK 1 — Policy/guardrail design: language + value, and evolution

### Schema v1 (adopt as-is, recommended)

A policy = **natural-language statement + structured question + decision bands**; Jev answers the question, bands decide action. Consistent with Discord AutoMod's trigger-metadata-action shape and Microsoft's agent-governance spec (verdicts allow/deny/escalate/transform, `evaluate_only` ≈ our `--dry-run`, fail-closed errors).

```yaml
policy_id: pol_scam_quarantine
version: 4                      # monotonic, bumped on every accepted change
status: active                  # draft | active | retired
statement: >
  "Messages offering free crypto, airdrops, or wallet-verification links from
   accounts under 7 days old are scams. Quarantine them and alert an admin.
   Never auto-ban on this policy."
question:
  type: noul                    # noul | choice | score
  text: "Is this message soliciting wallet credentials or funds under a false premise?"
bands:
  auto:  { when: "yes and confidence >= 0.90", action: quarantine_and_alert }
  draft: { when: "yes and confidence 0.60-0.89", action: escalate_packet }
  deny:  { when: "no or confidence < 0.60", action: none }
scope: { communities: [c_123], channels: [all-except: [#mod-lounge]], action_classes: [message_moderation] }
never_auto: [ban_member, delete_channel, message_older_than: 24h]
metadata: { created_by, source: manual|learned, parent_version, effective_at, review_after }
```

**Three worked policies:** (1) Public answer — choice `faq_answerable/needs_human/not_a_question`; auto ≥0.85 post with source link, draft 0.60–0.84, deny else; never_auto: DM replies, roles. (2) Scam quarantine — as above. (3) Member nudge — noul; auto ≥0.80 nudge, draft 0.50–0.79, deny else; never_auto: nudging same member twice in 7d, serious-support channels.

### Jev calibration practices (7)
1. **Atomic questions only** — one policy = one question (compound questions fail silently).
2. **Prefer noul/choice over score** — binary/low-precision is more reliable; score only with real anchors.
3. **Criteria with boundary examples** — include near-misses ("a member warning ABOUT a scam is not a scam").
4. **Calibrate with real corrections** — promote representative overrides as few-shot examples; track agreement rate.
5. **Deterministic first, judge second** — format/length/link checks are code; Jev only for judgment.
6. **Every call:** noul for gates, choice for routing; **never display output as a probability** — show band + historical agreement; one event per call for auto-band; **fail closed** on judge error.
7. **Replay before activate** — run changed policy against frozen past decisions; show agreement.

### Evolution pipeline (deterministic until the human step)
Collect overrides → **propose** after ≥N (e.g., 5 in 7 days) consistent overrides (draft, `source: learned`, nothing self-activates) → **replay** against frozen set ("would have matched 17/20 vs 11/20") → **admin accept/edit/reject** → version bump + effective date → **one-click rollback** (new version copying old; history never rewritten).

### Visible history (console + digest)
Reason card example: *"Scam quarantine v3 → v4 (effective Sep 27). Changed because you overrode 6 of the last 20 auto-quarantines, all involving members sharing scam warnings. What changed: policy now asks 'is this message itself soliciting funds?' and treats warnings-about-scams as not-a-scam. Threshold unchanged. [See the 6 decisions] [Replay results] [Undo]."* Digest line: *"2 policies changed, 1 proposal waiting, 94% gate agreement."* **Two clicks** from policy row → history → card, always linked to the exact overrides.

### Never learn / always auditable
Never learn: `never_auto` items (bans, destructive, roles/permissions, payments/refunds, legal/self-harm). Never cross-community. Never silently (no activation without human accept; no edit without version bump + reason card). Auditable by construction (immutable versions, overrides, replay results, accept events — exportable).

### Failure guards
Overfitting → min sample + single-admin concentration flag (multi-admin: ≥2 admins or "low confidence"). Thrash → 72h cooldown + hysteresis (+15 replay points). Silent drift → human accept + history/digest. Confidence misuse → bands + agreement rate, fail closed.

## ASK 2 — Competitive battle

**Battle card (condensed):** Discord AutoMod — free, only true pre-post filter, but 6 keyword rules / 1,000 keywords / 10 regex, English-only presets, no scam category. MEE6 — €11.99/mo, huge base, paywall backlash ("everything requires premium"). Dyno — $4.90–11.99/mo, reliable filter/commands, no judgment/learning. Carl-bot — generous free tier, roles/logging. Wick — raid/nuke shield (250k-account raid claim). Vortex — OSS moderation, Pro capped 25 servers. Statbot — analytics, 30-day free cutoff, measures never acts. Supervisor — AI classifier, £13.99/mo, deletes AFTER posting, no gate/learning. Common Room — $2,500/mo enterprise. Bettermode — $1,500/mo platform. Telegram Miss Rose/Combot/GroupButler — command-driven; **TeleClaw** — closest in spirit (NL instructions) but no human gate, no per-admin learning, no audit.

**Wedge sentence:** *"Your bots enforce rules you write. T3 handles the judgment calls your rules can't write — and every correction you make teaches it your standard."* Components: judgment under uncertainty · learned policies · decision packets · audit · memory. **Not:** command bot (Dyno/Carl-bot win), pre-post filter (AutoMod wins), raid shield (Wick wins), analytics (Statbot/Common Room win) — concede these unprompted.

**Moat (honest):** control plane (auditable learned policy layer — engineering lead, not a structural lock), data flywheel (per-community overrides, modest), taste (packets/reason cards). **Risks:** Discord could ship AI AutoMod; Supervisor/TeleClaw exist; a big bot adding "learn from corrections" is real. Defense: ship the learning loop visibly and first.

**Objections → answers:** false positives → three bands, only high-confidence acts; privacy → per-community containers, scoped keys, export/delete; cost → free tiers vs MEE6 paywall; lock-in → plain-language exportable policies; "Discord will build it" → years of 6 keyword rules, and we're cross-platform.

**Never claim:** pre-post blocking; zero false positives or "92% sure"; replacing AutoMod/Wick; anti-raid strength; enterprise analytics; "AI moderation is solved."

## ASK 3 — Product name shortlist (npm/domain checked 2026-09-26)

| Name | Rationale | npm | Domains |
|---|---|---|---|
| **Beadle** ★ | Historical community officer who kept order — human gatekeeper with judgment | FREE | beadle.app/.io likely free |
| **Folkmoot** | Old English community assembly where decisions were made | FREE | folkmoot.com likely free |
| Gatewise | "The gate that gets wiser" (literal) | FREE | gatewise.io likely free |
| Catchpole | Medieval officer who chased down what slipped through | FREE | catchpole.app likely free |
| Mootly / Sexton / Usherly | Friendly moot / custodian / guide | FREE | mixed |

**Recommendation:** **Beadle** first (ownable, meaningful, npm free), **Folkmoot** second. Re-verify at a registrar before slides.
