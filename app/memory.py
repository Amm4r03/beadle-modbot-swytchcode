import re

from app import db
from app.state import now


def remember(doc_id: str, title: str, text: str, tags: str = "") -> None:
    con = db.connect()
    con.execute(
        "INSERT OR REPLACE INTO knowledge_docs (doc_id, title, text, tags, added_at) VALUES (?,?,?,?,?)",
        (doc_id, title, text, tags, now()),
    )
    con.execute("DELETE FROM knowledge_fts WHERE doc_id = ?", (doc_id,))
    con.execute("INSERT INTO knowledge_fts (doc_id, title, text) VALUES (?,?,?)", (doc_id, title, text))
    con.commit()
    con.close()


def recall(query: str, k: int = 3) -> list[dict]:
    terms = re.findall(r"[a-z0-9]+", query.lower())
    if not terms:
        return []
    match = " OR ".join(terms[:12])
    con = db.connect()
    try:
        rows = con.execute(
            """SELECT doc_id, title, text, bm25(knowledge_fts) AS score
               FROM knowledge_fts WHERE knowledge_fts MATCH ? ORDER BY score LIMIT ?""",
            (match, k),
        ).fetchall()
    except Exception:
        return []
    finally:
        con.close()
    return [{"doc_id": r["doc_id"], "title": r["title"], "text": r["text"], "score": r["score"]} for r in rows]


def forget(doc_id: str) -> None:
    con = db.connect()
    con.execute("DELETE FROM knowledge_docs WHERE doc_id = ?", (doc_id,))
    con.execute("DELETE FROM knowledge_fts WHERE doc_id = ?", (doc_id,))
    con.commit()
    con.close()


def count() -> int:
    con = db.connect()
    try:
        return con.execute("SELECT COUNT(*) FROM knowledge_docs").fetchone()[0]
    finally:
        con.close()
