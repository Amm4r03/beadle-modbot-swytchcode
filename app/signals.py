import re
import time
from datetime import datetime, timezone

from app.state import Event, SignalResult

SIGNAL_VERSION = "v0.1"
URL_RE = re.compile(r"https?://\S+", re.I)
INTERROGATIVES = ("how", "what", "where", "when", "why", "can", "is", "does", "do", "anyone", "does anyone")
CONTACT_PHRASES = ("dm me", "contact me", "private message", "pm me", "message me")
SOLICIT_TERMS = ("wallet", "verify", "claim", "airdrop", "urgent", "seed phrase", "connect wallet")


def _result(signal_id: str, value: str | int, status: str, evidence: list[dict], started: float, unit: str | None = None) -> SignalResult:
    out: SignalResult = {
        "id": signal_id,
        "version": SIGNAL_VERSION,
        "value": value,
        "evidence": evidence,
        "input_status": status,
        "evaluated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cost_ms": int((time.perf_counter() - started) * 1000),
    }
    if unit:
        out["unit"] = unit
    return out


def question_shape(event: Event, _context: dict | None = None) -> SignalResult:
    started = time.perf_counter()
    text = event.get("text")
    if text is None:
        return _result("question_shape", "UNKNOWN", "MISSING", [], started)
    stripped = text.strip()
    first = stripped.split()[0].lower().strip(".,!") if stripped.split() else ""
    value = "TRUE" if stripped.endswith("?") or first in INTERROGATIVES else "FALSE"
    return _result("question_shape", value, "COMPLETE", [{"field": "text", "value": stripped[:120]}], started)


def solicitation(event: Event, _context: dict | None = None) -> SignalResult:
    started = time.perf_counter()
    text = event.get("text")
    if text is None:
        return _result("solicitation", "UNKNOWN", "MISSING", [], started)
    lowered = text.lower()
    has_contact = any(p in lowered for p in CONTACT_PHRASES)
    has_term = any(t in lowered for t in SOLICIT_TERMS)
    value = "TRUE" if (has_contact and has_term) else "FALSE"
    return _result("solicitation", value, "COMPLETE", [{"field": "contact_phrase", "value": has_contact}, {"field": "solicit_term", "value": has_term}], started)


def first_link(event: Event, context: dict | None = None) -> SignalResult:
    started = time.perf_counter()
    text = event.get("text")
    if text is None:
        return _result("first_link", "UNKNOWN", "MISSING", [], started)
    prior = (context or {}).get("prior_posts")
    has_url = bool(URL_RE.search(text))
    if prior is None:
        return _result("first_link", "UNKNOWN", "MISSING", [{"field": "prior_posts", "value": "unavailable"}], started)
    value = "TRUE" if (prior == 0 and has_url) else "FALSE"
    return _result("first_link", value, "COMPLETE", [{"field": "prior_posts", "value": prior}, {"field": "has_url", "value": has_url}], started)


def member_new(event: Event, _context: dict | None = None) -> SignalResult:
    started = time.perf_counter()
    joined = event.get("author_joined_at")
    occurred = event.get("occurred_at")
    if not joined or not occurred:
        return _result("member_new", "UNKNOWN", "MISSING", [], started)
    try:
        joined_at = datetime.fromisoformat(joined.replace("Z", "+00:00"))
        occurred_at = datetime.fromisoformat(occurred.replace("Z", "+00:00"))
        hours = (occurred_at - joined_at).total_seconds() / 3600
    except ValueError:
        return _result("member_new", "UNKNOWN", "ERROR", [], started)
    value = "TRUE" if hours < 24 else "FALSE"
    return _result("member_new", value, "COMPLETE", [{"field": "hours_since_join", "value": round(hours, 1)}], started, unit="hours")


ALL_SIGNALS = (member_new, solicitation, first_link, question_shape)


def run_signals(event: Event, context: dict | None = None) -> list[SignalResult]:
    return [signal(event, context) for signal in ALL_SIGNALS]
