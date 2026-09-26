import hashlib
import os
import re
import time
from datetime import datetime, timedelta, timezone

from app import db
from app.state import Event, SignalResult

SIGNAL_VERSION = "v0.2"
URL_RE = re.compile(r"https?://\S+", re.I)
DOMAIN_RE = re.compile(r"(?:[a-z0-9-]+\.)+[a-z]{2,}", re.I)
INTERROGATIVES = ("how", "what", "where", "when", "why", "can", "is", "does", "do", "anyone", "does anyone")
CONTACT_PHRASES = ("dm me", "contact me", "private message", "pm me", "message me")
SOLICIT_TERMS = ("wallet", "verify", "claim", "airdrop", "urgent", "seed phrase", "connect wallet")
BLOCKED_DOMAINS = frozenset(
    d.strip().lower()
    for d in os.environ.get("DOMAIN_BLOCKLIST", "maplenest-verify.xyz,maplenest-rewards.xyz,t.me-verify-maplenest.xyz").split(",")
    if d.strip()
)
RATE_WINDOW_MINUTES = 10
RATE_BURST_THRESHOLD = 5
DUPLICATE_THRESHOLD = 2
THREAT_RE = re.compile(r"\b(delete|destroy|shut\s?down|burn|kill|nuke|raid)\b[^.!?]{0,30}\b(community|group|server|channel|chat)\b", re.I)


def _domains(text: str) -> list[str]:
    normalized = text.replace("[.]", ".").replace("(.)", ".").replace(" dot ", ".")
    return sorted({match.lower() for match in DOMAIN_RE.findall(normalized)})


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
    normalized = text.replace("[.]", ".").replace("(.)", ".")
    has_url = bool(URL_RE.search(normalized)) or bool(DOMAIN_RE.search(normalized))
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


def rate_burst(event: Event, context: dict | None = None) -> SignalResult:
    started = time.perf_counter()
    count = (context or {}).get("member_recent_count")
    if count is None:
        return _result("rate_burst", "UNKNOWN", "MISSING", [{"field": "member_recent_count", "value": "unavailable"}], started)
    value = "TRUE" if count >= RATE_BURST_THRESHOLD else "FALSE"
    return _result(
        "rate_burst",
        value,
        "COMPLETE",
        [{"field": "member_recent_count", "value": count}, {"field": "window_minutes", "value": RATE_WINDOW_MINUTES}],
        started,
    )


def duplicate_payload(event: Event, context: dict | None = None) -> SignalResult:
    started = time.perf_counter()
    repeats = (context or {}).get("payload_repeat_count")
    if repeats is None:
        return _result("duplicate_payload", "UNKNOWN", "MISSING", [{"field": "payload_repeat_count", "value": "unavailable"}], started)
    value = "TRUE" if repeats >= DUPLICATE_THRESHOLD else "FALSE"
    return _result(
        "duplicate_payload",
        value,
        "COMPLETE",
        [{"field": "payload_repeat_count", "value": repeats}, {"field": "window_minutes", "value": RATE_WINDOW_MINUTES}],
        started,
    )


def domain_allow_or_block(event: Event, _context: dict | None = None) -> SignalResult:
    started = time.perf_counter()
    text = event.get("text")
    if text is None:
        return _result("domain_allow_or_block", "UNKNOWN", "MISSING", [], started)
    domains = _domains(text)
    if not domains:
        return _result("domain_allow_or_block", "UNKNOWN", "COMPLETE", [{"field": "domains", "value": []}], started)
    blocked = [domain for domain in domains if domain in BLOCKED_DOMAINS]
    value = "TRUE" if blocked else "FALSE"
    return _result(
        "domain_allow_or_block",
        value,
        "COMPLETE",
        [{"field": "domains", "value": domains}, {"field": "blocked", "value": blocked}],
        started,
    )


def known_trust_or_override(event: Event, context: dict | None = None) -> SignalResult:
    started = time.perf_counter()
    trust = (context or {}).get("member_trust")
    if trust is None:
        return _result("known_trust_or_override", "UNKNOWN", "MISSING", [{"field": "member_trust", "value": "store unavailable"}], started)
    value = "TRUE" if trust else "FALSE"
    return _result("known_trust_or_override", value, "COMPLETE", [{"field": "member_trust", "value": trust}], started)


def threat_terms(event: Event, _context: dict | None = None) -> SignalResult:
    started = time.perf_counter()
    text = event.get("text")
    if text is None:
        return _result("threat_terms", "UNKNOWN", "MISSING", [], started)
    match = THREAT_RE.search(text)
    value = "TRUE" if match else "FALSE"
    evidence = [{"field": "pattern", "value": match.group(0)[:80]}] if match else []
    return _result("threat_terms", value, "COMPLETE", evidence, started)


def build_context(event: Event) -> dict:
    context: dict = {}
    occurred = event.get("occurred_at")
    author = event.get("author_id")
    text = event.get("text") or ""
    if not occurred or not author:
        return context
    try:
        window_start = (datetime.fromisoformat(occurred.replace("Z", "+00:00")) - timedelta(minutes=RATE_WINDOW_MINUTES)).isoformat(timespec="seconds")
        payload_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        con = db.connect()
        context["member_recent_count"] = con.execute(
            "SELECT COUNT(*) FROM normalized_events WHERE author_id = ? AND occurred_at >= ?",
            (author, window_start),
        ).fetchone()[0]
        context["prior_posts"] = con.execute(
            "SELECT COUNT(*) FROM normalized_events WHERE author_id = ? AND occurred_at < ?",
            (author, occurred),
        ).fetchone()[0]
        context["payload_repeat_count"] = con.execute(
            """SELECT COUNT(*) FROM normalized_events n JOIN inbox_events i ON i.id = n.event_id
               WHERE i.payload_hash = ? AND n.author_id != ? AND n.occurred_at >= ?""",
            (payload_hash, author, window_start),
        ).fetchone()[0]
        con.close()
    except Exception:
        return {}
    return context


ALL_SIGNALS = (
    member_new,
    first_link,
    rate_burst,
    duplicate_payload,
    domain_allow_or_block,
    known_trust_or_override,
    threat_terms,
    solicitation,
    question_shape,
)


def run_signals(event: Event, context: dict | None = None) -> list[SignalResult]:
    return [signal(event, context) for signal in ALL_SIGNALS]
