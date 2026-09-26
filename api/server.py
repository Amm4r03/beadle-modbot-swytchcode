import json
import sqlite3
import time
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "state.db"

app = FastAPI(title="Beadle read API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, timeout=5)
    con.execute("PRAGMA query_only=ON")
    con.row_factory = sqlite3.Row
    return con


def rows(sql: str, params: tuple = ()) -> list[dict]:
    con = connect()
    try:
        return [dict(r) for r in con.execute(sql, params).fetchall()]
    finally:
        con.close()


@app.get("/health")
def health():
    counts = rows(
        "SELECT (SELECT COUNT(*) FROM normalized_events) AS events, (SELECT COUNT(*) FROM decisions) AS decisions, (SELECT COUNT(*) FROM action_intents) AS actions"
    )
    return {"ok": True, "db": str(DB_PATH), "counts": counts[0] if counts else {}}


@app.get("/api/communities/{community_id}/counts")
def counts(community_id: str):
    observed = rows("SELECT COUNT(*) AS n FROM inbox_events WHERE community_id = ?", (community_id,))[0]["n"]
    bands = rows(
        """SELECT d.band, COUNT(DISTINCT d.event_id) AS n FROM decisions d
           JOIN inbox_events i ON i.id = d.event_id
           WHERE i.community_id = ? GROUP BY d.band""",
        (community_id,),
    )
    quarantined = rows(
        """SELECT COUNT(DISTINCT a.event_id) AS n FROM action_intents a
           JOIN inbox_events i ON i.id = a.event_id
           WHERE i.community_id = ? AND a.action_type = 'mod_queue_card' AND a.status = 'pending'""",
        (community_id,),
    )[0]["n"]
    resolved = rows(
        """SELECT COUNT(DISTINCT o.event_id) AS n FROM overrides o
           JOIN inbox_events i ON i.id = o.event_id WHERE i.community_id = ?""",
        (community_id,),
    )[0]["n"]
    return {
        "community_id": community_id,
        "observed": observed,
        "by_band": {r["band"]: r["n"] for r in bands},
        "quarantined": quarantined,
        "resolved": resolved,
    }


@app.get("/api/events")
def events(community_id: str, limit: int = Query(50, le=200)):
    return rows(
        """SELECT e.id AS event_id, e.platform, e.received_at, n.text, n.author_id,
                  d.verdict, d.band, d.confidence, d.reason
           FROM inbox_events e
           LEFT JOIN normalized_events n ON n.event_id = e.id
           LEFT JOIN decisions d ON d.event_id = e.id
             AND d.id = (SELECT MAX(id) FROM decisions WHERE event_id = e.id)
           WHERE e.community_id = ?
           ORDER BY e.received_at DESC, e.id DESC LIMIT ?""",
        (community_id, limit),
    )


@app.get("/api/decisions/{event_id}")
def decision(event_id: str):
    return rows("SELECT * FROM decisions WHERE event_id = ? ORDER BY id DESC", (event_id,))


@app.get("/api/trace/{event_id}")
def trace(event_id: str):
    return {
        "event_id": event_id,
        "transitions": rows(
            "SELECT from_state, to_state, reason_code, occurred_at FROM event_transitions WHERE event_id = ? ORDER BY id",
            (event_id,),
        ),
        "signals": rows(
            "SELECT signal_version, result_json, evaluated_at FROM signal_runs WHERE event_id = ? ORDER BY signal_version",
            (event_id,),
        ),
        "decisions": rows(
            "SELECT verdict, band, confidence, reason, prompt_version, prompt_hash, model_id, result_status, decided_at FROM decisions WHERE event_id = ? ORDER BY id DESC",
            (event_id,),
        ),
        "actions": rows(
            "SELECT action_type, status, idempotency_key, created_at, updated_at FROM action_intents WHERE event_id = ? ORDER BY created_at",
            (event_id,),
        ),
        "overrides": rows(
            "SELECT verdict, reason_code, resulting_action, created_at FROM overrides WHERE event_id = ? ORDER BY id",
            (event_id,),
        ),
    }


class ResolveRequest(BaseModel):
    verdict: str
    reason_code: str | None = None
    admin_user_id: str = "admin-demo"
    resulting_action: str | None = None


@app.post("/api/quarantine/{event_id}/resolve")
def resolve_quarantine(event_id: str, request: ResolveRequest):
    con = sqlite3.connect(DB_PATH, timeout=5)
    con.execute("PRAGMA busy_timeout=5000")
    con.row_factory = sqlite3.Row
    try:
        community = con.execute(
            "SELECT community_id FROM inbox_events WHERE id = ?", (event_id,)
        ).fetchone()
        con.execute(
            "INSERT INTO overrides (event_id, admin_user_id, verdict, reason_code, message_class, resulting_action, created_at) VALUES (?,?,?,?,?,?,datetime('now'))",
            (event_id, request.admin_user_id, request.verdict, request.reason_code, "quarantine_resolution", request.resulting_action),
        )
        override_id = con.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        updated = con.execute(
            "UPDATE action_intents SET status = 'resolved', updated_at = datetime('now') WHERE event_id = ? AND action_type = 'mod_queue_card'",
            (event_id,),
        ).rowcount
        con.execute(
            "INSERT INTO audit (community_id, actor, action, detail_json, created_at) VALUES (?,?,?,?,datetime('now'))",
            (
                community["community_id"] if community else None,
                request.admin_user_id,
                "quarantine_resolved",
                json.dumps({"event_id": event_id, "verdict": request.verdict, "reason_code": request.reason_code, "resulting_action": request.resulting_action}),
            ),
        )
        con.commit()
        return {"ok": True, "event_id": event_id, "override_id": override_id, "cards_updated": updated}
    finally:
        con.close()


@app.get("/api/stream")
def stream():
    def gen():
        last = None
        while True:
            con = connect()
            d = con.execute("SELECT COALESCE(MAX(id),0) AS n FROM decisions").fetchone()["n"]
            t = con.execute("SELECT COALESCE(MAX(id),0) AS n FROM event_transitions").fetchone()["n"]
            a = con.execute("SELECT COALESCE(MAX(rowid),0) AS n FROM action_intents").fetchone()["n"]
            con.close()
            cursor = (d, t, a)
            if cursor != last:
                last = cursor
                yield f"data: {json.dumps({'decisions': d, 'transitions': t, 'actions': a, 'ts': time.time()})}\n\n"
            time.sleep(2)

    return StreamingResponse(gen(), media_type="text/event-stream")
