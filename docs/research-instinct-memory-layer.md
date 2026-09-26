# Memory Layer Decision — Drop supermemory; sqlite-vec + FTS5 (Instinct research)

Date: 2026-09-26 · Source: email 68000. All options free/local; differences are footprint, deps, latency, ops.

## Recommendation (accepted as the working decision)

**Drop supermemory. Ship `sqlite-vec` + SQLite `FTS5` in the same SQLite file as the data plane, behind a `MemoryStore` interface.**

Why: zero added process, zero second storage system, <1MB footprint (vs supermemory's server + embedding model + LLM extraction pipeline); Beadle-scale data (thousands of learned patterns per community) sits deep inside sqlite-vec's fast zone (~5ms p50 @100K vectors); FTS5 + vectors in one file gives hybrid recall with one backup artifact; supermemory's LLM extraction pipeline duplicates what Jev already does.

## Comparison (condensed)

| Option | Added footprint | Extra process | LLM on write path | Latency at our scale | Second storage |
|---|---|---|---|---|---|
| **SQLite FTS5** | 0 | no | no | ~ms keyword | no |
| **sqlite-vec** ★ | <1MB | no | no | ~5ms p50 @100K | no (same file) |
| LanceDB | tens of MB | no | no | ~2ms p50 @100K | yes |
| Chroma | heavy | no | optional | ~1–2ms, RAM-bound | yes |
| Qdrant local | server | yes | no | ~ms | yes |
| mem0 | framework + store | yes | yes | seconds on writes | yes |
| supermemory local | server + models (258MB binary) | yes | yes | RTT + LLM on writes | yes |
| **Neo4j** | JVM server (hundreds of MB) | yes | no (custom extraction needed) | server-class | yes |

**Neo4j vs supermemory for our case:** Neo4j is a general graph database — great for deep traversals at scale, but it's a JVM server with its own ops/licensing story, and it gives us no memory extraction, no embeddings, no profiles. supermemory is turnkey memory (extraction + graph-lite + vectors) but heavy and duplicates Jev's judgment. For a one-day local build over a small per-community corpus, **both are overkill**: our graph needs (Updates/Extends/Derives) are simple FK columns + a few joins. If we ever need real graph traversal or >1M vectors, the documented swaps are Neo4j (graph) and LanceDB (vectors) — the interface below keeps that exit open.

## The drop-in interface (the user's requirement)

```python
class MemoryStore(Protocol):
    def remember(self, content: str, embedding: list[float], *, metadata: dict | None = None) -> str: ...
    def recall(self, embedding: list[float], *, k: int = 5, where: dict | None = None) -> list[Memory]: ...
    def forget(self, memory_id: str) -> None: ...
```

Rules that make the swap real: normalized `score` (higher = closer) across backends; `where` = plain equality dict (`{"user_id": ..., "community_id": ...}`); a shared adapter test suite per backend. Embeddings via `fastembed` (ONNX, CPU, local) or Gemini embeddings on free keys. `forget()` exists for per-user deletion.

## Portable learned-config (the "learn from their system / drop-in" requirement)

One JSON per community, versioned, stored as a row in the same SQLite file:
```json
{ "schema_version": 1, "community_id": "tg:-100...", "exported_at": "...",
  "thresholds": {"auto_act": 0.92, "quarantine_below": 0.60},
  "label_weights": {"spam_link": 0.85, "self_promo": 0.70},
  "admin_overrides": [{"pattern_hash": "a1b2c3", "verdict": "allow", "count": 14, "last_seen": "..."}],
  "model": {"name": "jev", "prompt_version": "gate-v3"} }
```
Memory entries reference patterns by `pattern_hash`, so config + memories travel together without ID collisions. Export = SELECT + write file; import = validate version + upsert.

## One-day build path

`pip install sqlite-vec fastembed` → two-table schema (memories vec0 table + learned_config row) → three-method adapter → `remember` wired into the gate's learn hop, `recall` into classify/gate. No new deployable.
