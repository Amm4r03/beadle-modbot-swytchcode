import json
import os
from datetime import datetime, timezone

from app import db, jev, swytchcode

WINDOW_MINUTES = 10
DRAFT_THRESHOLD = 3
HIGH_RISK = 0.90
ESCALATION_QUESTION = {
    "escalation_urgency": {
        "type": "noul",
        "instructions": "Does this held case, given the recent cluster of held cases, warrant an immediate admin heads-up rather than routine review? Judge urgency of attention, not whether the case is harmful.",
    }
}


def check(event_id: str, text: str, band: str, verdict: str, confidence: float, reason: str) -> dict | None:
    if band != "DRAFT":
        return None
    con = db.connect()
    row = con.execute(
        "SELECT COUNT(DISTINCT event_id) AS n FROM decisions WHERE band = 'DRAFT' AND decided_at >= datetime('now', ?)",
        (f"-{WINDOW_MINUTES} minutes",),
    ).fetchone()
    con.close()
    count = row["n"] if row else 0
    high_risk = confidence >= HIGH_RISK
    if not high_risk and count < DRAFT_THRESHOLD:
        return None
    trigger = "high_risk_case" if high_risk else f"surge:{count}_cases_in_{WINDOW_MINUTES}m"
    try:
        raw = jev.score(text, ESCALATION_QUESTION)
        jev_call = {
            "question": "escalation_urgency",
            "score": float(raw["answers"]["escalation_urgency"]["noul"]),
            "model": raw.get("model"),
        }
    except Exception as error:
        jev_call = {"question": "escalation_urgency", "score": None, "error": str(error)[:120]}
    detail = {
        "event_id": event_id,
        "trigger": trigger,
        "band": band,
        "verdict": verdict,
        "confidence": confidence,
        "reason": reason,
        "window_minutes": WINDOW_MINUTES,
        "draft_count": count,
        "text": text[:200],
        "jev": jev_call,
        "raised_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    con = db.connect()
    con.execute(
        "INSERT INTO audit (community_id, actor, action, detail_json, created_at) VALUES (?,?,?,?,datetime('now'))",
        (None, "beadle", "escalation_alert", json.dumps(detail)),
    )
    con.commit()
    con.close()
    channel = os.environ.get("SLACK_CHANNEL_ID", "")
    if channel:
        try:
            swytchcode.post_slack_message(
                channel,
                f"Beadle escalation alert ({trigger})\nEvent: {event_id}\nDecision: {band}:{verdict} (conf {confidence:.2f})\nJev escalation_urgency: {jev_call.get('score')}\nMessage: {text[:160]}\nReason: {reason}\nModeration continues - this is an admin heads-up.",
            )
        except Exception:
            pass
    return detail
