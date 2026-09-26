import hashlib
import json
import os

import httpx

BASE_URL = os.environ.get("TYPESAFE_BASE_URL", "https://api.typesafe.ai")
MODEL = os.environ.get("JEV_MODEL", "jev-1.13.0")
PROMPT_VERSION = "classify-v0.5"
NORM_VERSION = "norms-v0.1"
EXAMPLE_SNAPSHOT_ID = "examples-empty-v0.1"
KNOWLEDGE_PROMPT_VERSION = "knowledge-v0.2"


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


def classify_questions() -> dict:
    return {
        "solicitation": {
            "type": "noul",
            "instructions": "Does the author seek to promote or direct readers toward an offer, payment, contact, external signup, or similar action - the author pushing others? If the author is asking for help or information for themselves, or discussing a topic, answer false. A member warning others about a scam is not a scam.",
        },
        "question_shape": {
            "type": "noul",
            "instructions": "Is the main intent a genuine request for help or information in this community, rather than an offer or engagement bait? A question mark alone is insufficient.",
        },
        "needs_human_review": {
            "type": "noul",
            "instructions": "Is a moderator needed because the relevant meaning or applicable community norm is materially uncertain, sensitive, or disputed? Do not infer this merely because a score is near a threshold; the reducer handles score bands.",
        },
        "threat_or_harm": {
            "type": "noul",
            "instructions": "Does the message threaten violence, destruction, or serious harm to people, the community, or its property - including threats to delete, destroy, or shut the community down? Discussing hypotheticals, reporting a threat, or warning others is not a threat.",
        },
    }


def prompt_hash() -> str:
    canonical = json.dumps(classify_questions(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def run_classify(event_text: str) -> dict:
    result = {
        "prompt_version": PROMPT_VERSION,
        "prompt_hash": prompt_hash(),
        "model_id": MODEL,
        "result_status": "ok",
        "scores": {},
        "degraded": False,
        "error": None,
    }
    try:
        raw = score(event_text, classify_questions())
    except Exception as error:
        result.update(
            result_status="timeout" if isinstance(error, httpx.TimeoutException) else "error",
            degraded=True,
            scores={"solicitation": None, "question_shape": None, "needs_human_review": None, "threat_or_harm": None},
            error=f"{type(error).__name__}: {str(error)[:120]}",
        )
        return result
    answers = raw.get("answers", {})
    try:
        result["scores"] = {
            "solicitation": float(answers["solicitation"]["noul"]),
            "question_shape": float(answers["question_shape"]["noul"]),
            "needs_human_review": float(answers["needs_human_review"]["noul"]),
            "threat_or_harm": float(answers["threat_or_harm"]["noul"]),
        }
        result["model_id"] = raw.get("model", MODEL)
        result["usage"] = raw.get("usage", {})
    except (KeyError, TypeError, ValueError):
        result.update(
            result_status="parse_error",
            degraded=True,
            scores={"solicitation": None, "question_shape": None, "needs_human_review": None, "threat_or_harm": None},
            error="missing or malformed noul value",
        )
    return result


def check_answerable(question: str, passages: list[dict]) -> dict:
    state_text = "QUESTION:\n" + question + "\n\nPASSAGES:\n" + "\n".join(
        f"[{p['doc_id']}] {p['title']}: {p['text'][:600]}" for p in passages
    )
    questions = {
        "internal_knowledge_question": {
            "type": "noul",
            "instructions": "Is the QUESTION the kind of community question this knowledge base is meant to answer - about the same community topics as the PASSAGES - rather than a promotion, personal offer, or unrelated matter?",
        },
        "answerable": {
            "type": "noul",
            "instructions": "Is the QUESTION answerable using only the PASSAGES above? Judge only from the passages; if the passages do not contain the answer, answer false.",
        },
    }
    try:
        raw = score(state_text, questions)
        return {
            "internal_p": float(raw["answers"]["internal_knowledge_question"]["noul"]),
            "answerable_p": float(raw["answers"]["answerable"]["noul"]),
            "model_id": raw.get("model", MODEL),
            "usage": raw.get("usage", {}),
        }
    except Exception as error:
        return {"answerable_p": None, "model_id": MODEL, "error": f"{type(error).__name__}: {str(error)[:120]}"}


def reduce_gate(jev_result: dict, knowledge: dict | None = None) -> dict:
    scores = jev_result.get("scores", {})
    scam_p = scores.get("solicitation")
    question_p = scores.get("question_shape")
    review_p = scores.get("needs_human_review")
    threat_p = scores.get("threat_or_harm")
    knowledge = knowledge or {}
    knowledge_ok = (knowledge.get("answerable_p") or 0) >= 0.70 and (knowledge.get("internal_p") or 0) >= 0.50
    if jev_result.get("degraded") or scam_p is None or question_p is None or review_p is None or threat_p is None:
        return {
            "verdict": "review",
            "band": "DRAFT",
            "confidence": 0.0,
            "reason": f"gate: fail closed to human review (classify {jev_result.get('result_status', 'error')})",
            "scores": scores,
            "model_id": jev_result.get("model_id"),
        }
    if threat_p >= 0.70:
        verdict, band = "quarantine", "DRAFT"
        reason = f"gate: threat/harm probability {threat_p:.2f} at/above 0.70 - quarantine for review"
    elif scam_p >= 0.70:
        verdict, band = "quarantine", "DRAFT"
        reason = f"gate: solicitation probability {scam_p:.2f} at/above 0.70 - quarantine for review"
    elif question_p >= 0.85 and review_p < 0.50 and (scam_p <= 0.10 or knowledge_ok):
        verdict, band = "answer", "AUTO"
        reason = (
            f"gate: genuine question probability {question_p:.2f} at/above 0.85, solicitation {scam_p:.2f} at/below 0.10 - answer"
            if scam_p <= 0.10
            else f"gate: genuine question {question_p:.2f} at/above 0.85 and answerable from the knowledge base - answer"
        )
    elif review_p >= 0.50 or question_p >= 0.50 or scam_p >= 0.40:
        verdict, band = "review", "DRAFT"
        reason = f"gate: uncertain (solicitation {scam_p:.2f}, question {question_p:.2f}, review {review_p:.2f}) - send to admin"
    else:
        verdict, band = "no_action", "DENY"
        reason = f"gate: no action warranted (solicitation {scam_p:.2f}, question {question_p:.2f})"
    return {
        "verdict": verdict,
        "band": band,
        "confidence": max(scam_p, question_p, review_p),
        "reason": reason,
        "scores": scores,
        "model_id": jev_result.get("model_id"),
    }
