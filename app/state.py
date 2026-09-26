from datetime import datetime, timezone
from typing import Literal, TypedDict


class Event(TypedDict, total=False):
    event_id: str
    platform: Literal["telegram", "discord"]
    community_id: str
    channel_id: str
    message_id: str
    author_id: str
    author_joined_at: str
    text: str
    occurred_at: str
    is_bot: bool


class SignalResult(TypedDict, total=False):
    id: str
    version: str
    value: str | int
    unit: str
    evidence: list[dict]
    input_status: Literal["COMPLETE", "MISSING", "STALE", "ERROR"]
    evaluated_at: str
    cost_ms: int


class Decision(TypedDict, total=False):
    event_id: str
    policy_version: str
    gate_version: str
    model_id: str
    prompt_version: str
    verdict: Literal["answer", "quarantine", "review", "no_action"]
    band: Literal["AUTO", "DRAFT", "DENY"]
    confidence: float
    reason: str
    signals_fired: list[str]
    retrieved_ids: list[str]
    decided_at: str


class AgentState(TypedDict, total=False):
    event: Event
    signals: list[SignalResult]
    decision: Decision
    action: dict
    admin_verdict: dict | None
    transitions: list[dict]
    needs_attention: bool
    error: str


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def transition(state: AgentState, to_state: str, reason_code: str = "") -> AgentState:
    state.setdefault("transitions", []).append(
        {"to_state": to_state, "occurred_at": now(), "reason_code": reason_code}
    )
    return state
