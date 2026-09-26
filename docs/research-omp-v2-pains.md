# v2 Customer Deep-Dives + Flows (omp-research-2)

Date: 2026-09-25 (evening) · Task: msg 22 assignments · Method: customer research first per `docs/research-v2-brief.md`.
Note: web search throttled at write time (all providers bot-walled); pains below reuse the already-sourced threads distilled in `docs/research-deepseek-panel-verdicts.md` (r/jira, r/CustomerSuccess, r/solana/wallet scams, r/ExperiencedDevs meetings, r/weddingplanning, r/smallbusiness late invoices) plus supermemory primary docs. Anything beyond those sources is tagged `[INFERENCE]` per §8.

---

## 1. Per-track customer deep-dives

### T1 — Software Engineer: the pain is context assembly, not code writing

The user is a mid-level engineer handed a Jira ticket with a one-line description and a stack trace. Sourced pain: practitioners describe "drowning in a 1000+ ticket backlog" and the standard advice is "cancel everything >6 months" — but nobody dares without evidence (panel verdicts, r/jira + r/agile threads). The v2 brief locks the approved direction: context assembly + reproduction + ticket, **not** fix generation.
- **Real workflow observed:** engineer opens ticket → hunts GitHub for the owning service → reads 3 stale PRs → asks in Slack "anyone know this area?" → waits → reproduces locally (30–90 min gone) → only then starts solving `[INFERENCE]`.
- **Workaround today:** tribal Slack questions, `git blame` archaeology, keeping personal "how X works" notes `[INFERENCE]`.
- **What success means:** a Slack workspace/bot that hands them the full context pack — suspect files, related issues, repro steps, linked commits — before they write a line. Time-to-first-understanding drops, not lines-of-code-written.
- **Budget signal:** engineering time is the budget; a tool that saves 1h per ticket pays for itself in a week `[INFERENCE]`.
- **Delight test:** the engineer says "it already knew" — not "it wrote code for me."

### T2 — Knowledge Worker: knowledge walks out with the person

The user is a team lead whose veteran (say, 8-year backend owner) resigns with 2 weeks' notice. Sourced pain: "KB was 40% stale", "docs said yes, the code said no" (panel verdicts, r/CustomerSuccess + r/B2BSaaS threads). The handover is a rushed doc + panicked Slacks after departure `[INFERENCE]`.
- **Real workflow observed:** leaver writes a hasty brain-dump under time pressure → successor discovers gaps months later when something breaks → asks around → reinvents `[INFERENCE]`.
- **Workaround today:** shadowing (expensive), recorded Loom tours (unsearchable), nothing `[INFERENCE]`.
- **What success means:** the successor can ask "why does the billing retry work that way?" and get an answer citing the leaver's actual docs/threads — a browsable organizational memory, consented and reviewed.
- **Consent is the product constraint:** per the brief's Ghost variant rule, the leaver opts in and reviews the memory. Without this the demo dies in Q&A on privacy. See flow §2.
- **Viability lead:** supermemory's graph (Updates/Extends/Derives + profiles + forgetting) maps 1:1 onto "beliefs that stay true over time" — the tech story is credible if consent UX is designed first.

### T3 — Community: launch is day one, the grind is day 2–365

The user is a solo-founder-turned-community-manager whose launch spike decays into silence plus scam DMs. Sourced pain: wallets drained via fake admin DMs, "19.45 SOL lost" (panel verdicts, r/solana + r/CryptoScams threads); r/CommunityManager exists as a standing practice community (verified subreddit). Launch-day-only tooling (my v1 Firefighter) was correctly judged too narrow.
- **Real workflow observed:** launch spike → same 5 questions on loop → mods burn out answering → lurkers stay silent → scammers arrive → engagement flatlines by month 2 `[INFERENCE]`.
- **Workaround today:** pinned FAQs nobody reads, volunteer mods, manual ban-hammer `[INFERENCE]`.
- **What success means (ongoing, not event):** a loop that keeps running — answer repeats, activate lurkers, quarantine scams, log everything — such that week-12 looks healthier than week-2. See loop + metrics §3.
- **Delight test:** the manager opens Monday to a digest that says what got handled, who newly spoke up, and what needs only their judgment.

### T4 — Meeting: the currency is hours returned, not summaries produced

The user is a senior IC/lead spending 20+ hours/week in Meets where half the sessions produce no decision, doc, or follow-up. Sourced pain: standing "time wasted in meetings" threads (panel verdicts, r/ExperiencedDevs + r/programming). The v2 brief locks the direction: **condense, don't attend** — propose compactions, execute the compaction (concise email/update instead of attendance).
- **Real workflow observed:** calendar fills by default → declining feels political → attends exhausted → real work shifts to nights `[INFERENCE]`.
- **Workaround today:** "no-meeting Wednesdays" (erodes), async standup bots (shallow), declining and hoping `[INFERENCE]`.
- **What success means:** a number — "you got 6.5 hours back this week" — backed by the compaction artifacts (the emails/updates sent in their place). Every recommendation anchored to evidence (no decision produced, no docs, no follow-ups), never vibes — otherwise it's an opinion bot.
- **Delight test:** Friday shows a week with fewer boxes and nothing dropped.

### T5 — Wedding: nobody wants a "war room in Slack" — unify the chaos

User pushback verbatim: "I cannot think of someone who is going to make a wedding war room in Slack… the only utility is weather notifications? That feels off." Correct. The user is a couple (or family coordinator) juggling vendors, payments, guests, and deadlines across WhatsApp groups, spreadsheets, and memory. Sourced pain: vendor payment anxiety threads ("constantly nervous… making payments to various vendors"), planning stress levels varying with family/financial complexity (r/weddingplanning threads, verified live). Weather is one input, not the product — the brief mandates unification.
- **Real workflow observed:** venue/photographer/caterer each paid on different schedules with different advance balances → tracked in a spreadsheet someone stops updating → guest list in another sheet → deadlines live in someone's head `[INFERENCE]`.
- **Workaround today:** one giant spreadsheet + family group chat + planner charging crisis fees when it breaks `[INFERENCE]`.
- **What success means:** one surface where money owed, money paid, vendor deadlines, guest confirmations, and tasks live together — weather/panchang-style external inputs feed deadlines, they don't headline. The demo beat is "nothing is due that you don't know about," not a rain alert.
- **Honest viability flag:** the 5 listed APIs (OpenWeather, Gmail, Notion, Slack, Resend) contain no payments API and no guest-RSVP channel — money/guest tracking must ride on Notion + Gmail/Resend. Wedding unification feasibility (deepseek + email agent) must confirm this shapes the MVP before we commit.

### T6 — Business Operator: invoices paid late is chronic, measurable pain

The user is a freelancer/small agency owner chasing money. Sourced pain: ~40% of invoices paid late, payroll scramble threads (panel verdicts, r/smallbusinessUS + r/Solopreneur). No pushback on this track — Order-to-Cash stands, re-validated here.
- **Real workflow observed:** work delivered → invoice emailed → silence → awkward nudge → partial pay → spreadsheet updated never `[INFERENCE]`.
- **Workaround today:** manual follow-up calendar, "payable on receipt" ignored, factoring at a haircut `[INFERENCE]`.
- **What success means:** money moves without the owner becoming a debt collector — invoice → tracked → reminded → reconciled, with the policy guardrail (discount caps, refund blocks) as the trust story. The refund-block stage beat is the most photographable across all tracks (panel edge pick).
- **Cost flag (sourced):** custom policies are Pro tier ($29/mo) — first-30-min check tomorrow: `swy get`/`swy info`/`swy exec --explain`, else the block runs via `--demo`.

---

## 2. T2 consent-first onboarding flow (supermemory architecture)

Grounded in supermemory primary docs ([how-it-works](https://supermemory.ai/docs/concepts/how-it-works), [graph-memory](https://supermemory.ai/docs/concepts/graph-memory)) + container isolation model.

**Actors:** the exiting user (consenter), the successor (consumer), the admin (configures retention/scope).

**Flow:**
1. **Invite + scope consent.** Leaver gets a consent screen: which sources (Notion spaces, Gmail labels/folders, Drive folders — never whole-account-by-default), what date range, and what is excluded (a blocklist: e.g. personal labels, HR threads). Consent is per-source, revocable, expiring (e.g. 90 days then re-ask or auto-purge) `[INFERENCE: expiry UX]`.
2. **Ingest under isolation.** Each source ingests into supermemory under a dedicated `containerTag` (e.g. `handover_kavya_q3`) — the docs' hard isolation boundary — with `customId` per conversation/file for diff-billing and updates. Scoped API keys prevent cross-container reads.
3. **Dreaming builds beliefs.** The pipeline (extract → chunk → embed → index) plus the **dreaming** phase derives the memory graph: facts ("billing retry is 3× with backoff"), `Updates` (policy changed in March), `Extends` (owns payments + leads team of 5), `Derives` (likely owns the fraud-detection integration). `dreaming: "instant"` for the demo ("graph now"), `dynamic` for production quality.
4. **Leaver review (the privacy beat).** Before anyone else sees it, the leaver reviews the profile + memory list: keep / edit / forget per item (supermemory has forget + memory-review APIs). Low-confidence derives are flagged for explicit approval. This review screen IS the demo's trust moment — judges see consent enforced, not promised.
5. **Successor surface.** The successor asks in Slack ("why does the billing retry work that way?") → agent searches the container (memories + SuperRAG chunks for grounding) → answers **with citations to the leaver's actual docs**. Contradictions (leaver said X, wiki says Y) surface via `Updates` edges — which dovetails with the Contradiction Hunter pick.
6. **Decay + purge.** Time-based forgetting drops ephemeral facts; on expiry/revocation the container is purged. Admin sees audit (what was ingested, who queried, what was forgotten) `[INFERENCE: admin view]`.

**Viability verdict:** feasible — every primitive exists (connectors, containerTags, dreaming modes, forget/review APIs, MCP server). The 8-hour MVP: one consented Gmail label + one Notion space → ingest → leaver review screen → 3 seeded successor questions answered with citations. Biggest risk is ingest latency on stage (dreaming takes minutes) — pre-dream fixtures, show one live `instant` add as the money shot.

---

## 3. T3 post-launch success loop + 3 metrics

**The loop (runs weekly, forever — this is the product, not the launch):**
`Listen (X/Telegram/Slack firehose) → Answer repeats instantly + cluster novel questions → Activate (nudge lurkers with one relevant thread) → Protect (quarantine scam patterns, warn plainly) → Log (Notion transparency record) → Digest (Resend Sunday brief: handled / new voices / needs-your-judgment) → manager acts only on judgment items → loop learns (answered rate up, scam latency down).`

**3 candidate success metrics (what the demo proves):**
1. **Median first-answer time on repeat questions** — before: hours (mod availability); after: seconds (agent), with % answered without human touch. Proves load lifted `[INFERENCE: thresholds]`.
2. **Lurker activation rate** — % of silent members posting their first message per week, and 4-week retention of the activated cohort. Proves growth from inside, not join-begging `[INFERENCE: thresholds]`.
3. **Scam time-to-quarantine + victim count** — minutes from first scam DM pattern to quarantine + warning, and reported victims per month trending to zero. Proves the trust moat `[INFERENCE: thresholds]`.

Demo shape: show week-N dashboard with the three numbers moving the right way on seeded data, then one live novel question routed to the manager — the "needs-your-judgment" beat that proves the human stays in charge.
