# Learning Loop & Pitch — Instinct Research (Karpathy autoresearch + marketing)

Date: 2026-09-26 · Source: email 67967 (`~/Downloads/` PDF if attached). Distilled; full text in the mailbox. Research draft — not a claim that T3 implements these features.

## Part 1 — An honest learning loop (autoresearch discipline, not its architecture)

**Bottom line:** borrow the *experimental discipline* of Karpathy's `autoresearch` — freeze the evaluator and test cases, make one narrow candidate change, replay against the same cases, retain only measured improvement that doesn't worsen safety, keep a human-readable receipt. Call it **"learning from admin decisions through checked policy updates,"** never "a model retraining itself."

**Analogue table:** changeable artifact = bounded routing rule (e.g., impersonation escalation threshold per community) · fixed comparator = locked labeled replay cases + eval function outside the proposer's scope · budget = small fixed replay set/time · decision = promote only if guardrails + metric pass and an admin approves · trace = proposal ID, policy version, case IDs, before/after, approver, rollback pointer.

**Smallest honest loop (demoable):**
1. **Capture the event** — community, policy version, case, signals, proposed action, escalation reason (no private member text in screenshots); admin verdict + reason code; distinguish "draft approved" from "harmful action later undone."
2. **Propose ONE bounded change** — typed config diff, one parameter, bounded range (e.g., `review_if(score >= .80) → .72`, illustrative). Never let a single verdict silently rewrite policy.
3. **Replay fixed examples** — tiny preregistered set: true positives + benign lookalikes + a protected hard-stop case (e.g., 8 synthetic cases: 4 tuning / 4 untouched holdout). Show a 2×2 before/after (missed harmful, benign escalated, review load, unsafe auto-actions). Stop if unsafe auto-actions increase; define success before running.
4. **Gate promotion** — candidate until admin approves the diff + sees replay; version it, deploy only to that community/category, one-click revert; sensitive actions stay human-approval forever.
5. **Show the receipt** — `policy_v4 → candidate_v5`, source decision ID, reason, the one-param diff, case-set fingerprint, before/after outcomes, timestamp, rollback. Render "what changed / who approved / why / what would have happened on the same examples."

**What "really improves" means:** error rates on **untouched examples** per community/category at the same review budget, alongside review minutes and undo rate — compared to the frozen baseline. Confidence intervals + more cases before any production claim.

**Routes compared:** versioned rule + replay = **Yes (smallest believable loop)** · memory of corrected examples = optional explanation only, never automatic authority · learned ranker/online calibration = later, not 8h · fine-tune/self-modification = No (eval gaming, drift, cost).

**Recommendation:** ship route 1; memory only to explain/propose; global policy human-edited; community config isolated; sensitive hard stops non-learnable.

## Part 2 — Selling to judges

**Recommended positioning line:** *"T3 is a community operator with a human gate that learns from each admin correction, so routine work moves faster without giving up control."* Category: **human-governed community operations** — not an autonomous moderator, not an agent framework.

**Three proof points to make visible:** (1) the admin case (impersonation that looks ordinary until context is assembled); (2) execution + safety (one allowed Swytchcode action + one blocked/routed-for-approval with visible reason/audit); (3) the learning receipt (same borderline case before/after, visible config diff, untouched holdout, revert button). If no held-out eval: say "the rule updated in a controlled demo," not "we proved it gets smarter."

**Suggested 2-min sequence:** admin decision framing (0:00–0:15) → context packet + approval ask (0:15–0:40) → admin rejects + reason, candidate diff shown (0:40–1:05) → replay same cases: missed impersonation now escalates, benign lookalike passes, counts + holdout (1:05–1:30) → admin approves, Swytchcode allowed + denied calls with audit (1:30–1:50) → "turns corrections into reviewable operating rules" (1:50–2:00). Label synthetic data as synthetic.

**Judge archetypes:** technical → typed diff, frozen replay, execution boundary, no autoresearch-training claims · business → who the admin is, what decision takes time, what metric validates · design → approval card with context/reason/undo, clear before/after.

**Failure checklist:** feature tours → one scenario; glossy-no-proof → click-through + code path; overclaiming learning → separate rule change / memory / statistically verified improvement; no user/number → sourced pain + measured demo counts only; ignoring host → show where Swytchcode makes execution safer; confirm the official rubric on-site.

**Sources:** karpathy/autoresearch README + program.md + issue #599 (eval-gaming risk, community-reported) · ModSandbox CHI 2023 · model-moderator uncertainty paper · Meta bandits calibration · Reflexion · CLIN · Devpost judge interviews + criteria + demo guide · MLH judging plan · event Luma page.
