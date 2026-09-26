import os

import httpx

BASE_URL = os.environ.get("TYPESAFE_BASE_URL", "https://api.typesafe.ai")
MODEL = os.environ.get("JEV_MODEL", "jev-1.13.0")


class JevBlocked(Exception):
    pass


def require_key() -> str:
    key = os.environ.get("JEV_API_KEY") or os.environ.get("TYPESAFE_API_KEY")
    if not key:
        raise JevBlocked("JEV_API_KEY missing - live Jev required; ask the user. No fabricated scores.")
    return key


def score(state_text: str, questions: dict, model: str | None = None, timeout: float = 20.0) -> dict:
    key = require_key()
    response = httpx.post(
        f"{BASE_URL}/v1/systemone",
        headers={"Authorization": f"Bearer {key}"},
        json={"model": model or MODEL, "state": state_text, "questions": questions},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def gate_questions() -> dict:
    return {
        "suspicious_solicitation": {
            "type": "noul",
            "instructions": "Is this message soliciting wallet credentials, funds, or account verification under a false premise? A member warning others ABOUT a scam is not a scam.",
        },
        "answerable_from_source": {
            "type": "noul",
            "instructions": "Is this a genuine member question answerable from an approved community FAQ?",
        },
        "needs_human_review": {
            "type": "noul",
            "instructions": "Does this message require human moderator judgment before any action is taken?",
        },
    }


def evaluate(event_text: str) -> dict:
    try:
        raw = score(event_text, gate_questions())
    except Exception as error:
        return {
            "verdict": "review",
            "band": "DRAFT",
            "confidence": 0.0,
            "reason": f"gate unavailable - fail closed to human review ({type(error).__name__}: {str(error)[:120]})",
            "scores": {"scam_p": None, "answerable_p": None, "review_p": None},
            "model_id": MODEL,
            "degraded": True,
        }
    answers = raw.get("answers", {})
    scam_p = float(answers.get("suspicious_solicitation", {}).get("noul", 0.0))
    answerable_p = float(answers.get("answerable_from_source", {}).get("noul", 0.0))
    review_p = float(answers.get("needs_human_review", {}).get("noul", 0.0))
    model_id = raw.get("model", MODEL)

    if scam_p >= 0.70:
        verdict, band = "quarantine", "DRAFT"
        reason = f"gate: solicitation probability {scam_p:.2f} at/above 0.70 - quarantine for review"
    elif answerable_p >= 0.85 and review_p < 0.50:
        verdict, band = "answer", "AUTO"
        reason = f"gate: answerable probability {answerable_p:.2f} at/above 0.85 and review not required"
    elif review_p >= 0.50 or answerable_p >= 0.60:
        verdict, band = "review", "DRAFT"
        reason = f"gate: uncertain (answerable {answerable_p:.2f}, review {review_p:.2f}) - send to admin"
    else:
        verdict, band = "no_action", "DENY"
        reason = f"gate: no action warranted (answerable {answerable_p:.2f}, scam {scam_p:.2f})"

    return {
        "verdict": verdict,
        "band": band,
        "confidence": max(scam_p, answerable_p, review_p),
        "reason": reason,
        "scores": {"scam_p": scam_p, "answerable_p": answerable_p, "review_p": review_p},
        "model_id": model_id,
    }
