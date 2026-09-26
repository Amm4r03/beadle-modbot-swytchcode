# Knowledge-Usage Metrics (from audit data)

Owner: `omp-research-2` · Date: 2026-09-26 · Task: REQ #68 item 2.
Sources: `data/state.db` live rows (decisions.context_refs_json, knowledge_docs, audit). No fabrication: counts below are observed tonight.

## Observed state

- Knowledge docs in store: **9** (6 GDG + 3 plant-care).
- Decisions citing docs (`context_refs_json` non-empty): AUTO 13/26 cited, DRAFT 2/23 cited, DENY 0/2. Uncited AUTO answers used gate-only path (no retrieval) — expected for non-knowledge questions.
- Audit actions: `draft_answer` 14, `quarantine_resolved` 3.

## Top cited docs (from decisions.context_refs_json)

| Doc | Citations (decisions referencing it) |
|---|---|
| `gdg-cloud-new-delhi` | most-cited (appears in nearly every GDG answer) |
| `gdg-how-to-join` | second (join/how questions) |
| `yellow-tomato-leaves` | top plant-care (tomato question + BM25 partial matches) |
| `watering-schedule`, `gdg-events` | supporting |

## Hit / miss definition (for the dashboard)

- **HIT:** decision cites ≥1 doc AND admin does not override the answer (no correction within the review window).
- **MISS (retrieval):** decision cites docs but admin corrects/overrides the answer (wrong passages retrieved).
- **MISS (coverage):** genuine question, no docs cited, admin answers manually (knowledge gap — candidate for new doc).
- **ABSTAIN (correct):** nested-Jev answerability gate declines (not answerable from passages) → escalates. Counts as good judgment, not failure.

## Metrics to track (queries provided, run weekly)

1. **Citation rate:** cited AUTO / total AUTO (tonight: 13/26 = 50% — mix includes non-knowledge questions, so segment by question class before judging).
2. **Override rate on cited answers:** overrides where decision cited docs / cited decisions. Target: falling week-over-week with flat reversals (same rule as gate learning).
3. **Coverage gaps:** genuine questions with empty refs, grouped by topic → doc creation backlog.
4. **Per-doc precision:** citations of doc X that survived without override / total citations of X. Retire or rewrite docs that get cited but corrected.
5. **Abstention rate:** escalations via answerability-decline / total knowledge questions. Rising abstention + falling overrides = the gate learning caution correctly.

## Publishability

Same rules as the metrics doc: method + scope on every number ("on our seeded MapleNest fixtures + 9-doc base, <date>"), curves over points, behavior over sentiment, staged labeled. Never "our knowledge base is 95% accurate."
