import re

from app import db


def recall_examples(community_id: str, text: str, k: int = 3) -> list[dict]:
    con = db.connect()
    rows = con.execute(
        """SELECT o.id, o.event_id, o.verdict, o.reason_code, o.resulting_action, o.created_at, n.text AS event_text
           FROM overrides o
           JOIN normalized_events n ON n.event_id = o.event_id
           JOIN inbox_events i ON i.id = o.event_id
           WHERE i.community_id = ?
           ORDER BY o.id DESC LIMIT 50""",
        (community_id,),
    ).fetchall()
    con.close()
    terms = set(re.findall(r"[a-z0-9]+", (text or "").lower()))
    if not terms:
        return []
    scored: list[tuple[int, dict]] = []
    for row in rows:
        event_terms = set(re.findall(r"[a-z0-9]+", (row["event_text"] or "").lower()))
        overlap = len(terms & event_terms)
        if overlap >= 2:
            scored.append((overlap, dict(row)))
    scored.sort(key=lambda item: -item[0])
    return [row for _, row in scored[:k]]
