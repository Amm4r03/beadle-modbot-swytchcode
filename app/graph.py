import hashlib
import json
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph

from app import db, generate, jev, memory, signals
from app.state import AgentState, now, transition

GATE_VERSION = "gate-v0.1"
POLICY_VERSION = "policy-v0.1"


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def record(state: AgentState, to_state: str, reason_code: str = "") -> None:
    transitions = state.get("transitions") or []
    previous = transitions[-1]["to_state"] if transitions else None
    transition(state, to_state, reason_code)
    con = db.connect()
    con.execute(
        "INSERT INTO event_transitions (event_id, from_state, to_state, occurred_at, reason_code) VALUES (?,?,?,?,?)",
        (state["event"]["event_id"], previous, to_state, now(), reason_code),
    )
    con.commit()
    con.close()


def observe(state: AgentState) -> AgentState:
    event = state["event"]
    con = db.connect()
    con.execute(
        "INSERT OR IGNORE INTO inbox_events (id, community_id, platform, external_event_id, payload_hash, received_at, state) VALUES (?,?,?,?,?,?,?)",
        (event["event_id"], event["community_id"], event["platform"], event["message_id"], _hash(event.get("text", "")), event["occurred_at"], "received"),
    )
    con.execute(
        "INSERT OR IGNORE INTO normalized_events (event_id, channel_id, message_id, author_id, author_joined_at, text, occurred_at, normalization_version) VALUES (?,?,?,?,?,?,?,?)",
        (event["event_id"], event.get("channel_id"), event.get("message_id"), event.get("author_id"), event.get("author_joined_at"), event.get("text"), event.get("occurred_at"), "norm-v0.1"),
    )
    con.commit()
    con.close()
    record(state, "received", "ingested")
    return state


def classify(state: AgentState) -> AgentState:
    event = state["event"]
    results = signals.run_signals(event, signals.build_context(event))
    jev_result = jev.run_classify(event.get("text", ""))
    con = db.connect()
    for result in results:
        con.execute(
            "INSERT OR REPLACE INTO signal_runs (event_id, signal_version, result_json, evaluated_at) VALUES (?,?,?,?)",
            (event["event_id"], f"{result['id']}@{result['version']}", json.dumps(result), result["evaluated_at"]),
        )
    for name, value in (jev_result.get("scores") or {}).items():
        con.execute(
            "INSERT OR REPLACE INTO signal_runs (event_id, signal_version, result_json, evaluated_at) VALUES (?,?,?,?)",
            (
                event["event_id"],
                f"{name}@{jev_result['prompt_version']}",
                json.dumps(
                    {
                        "signal": name,
                        "value": value,
                        "model_id": jev_result.get("model_id"),
                        "prompt_hash": jev_result.get("prompt_hash"),
                        "result_status": jev_result.get("result_status"),
                    }
                ),
                now(),
            ),
        )
    con.commit()
    con.close()
    state["signals"] = results
    state["jev"] = jev_result
    usage = jev_result.get("usage") or {}
    if usage:
        con = db.connect()
        con.execute(
            "INSERT INTO token_usage (provider, model, workflow, input_tokens, output_tokens, recorded_at) VALUES (?,?,?,?,?,?)",
            ("jev", jev_result.get("model_id"), "classify", usage.get("input_tokens"), usage.get("output_tokens"), now()),
        )
        con.commit()
        con.close()
    names = [r["id"] for r in results] + [f"jev:{name}" for name in (jev_result.get("scores") or {}).keys()]
    knowledge = {"passages": [], "answerable_p": None}
    question_p = (jev_result.get("scores") or {}).get("question_shape") or 0.0
    if question_p >= 0.5:
        passages = memory.recall(event.get("text", ""), k=3)
        if passages:
            check = jev.check_answerable(event.get("text", ""), passages)
            knowledge = {
                "passages": [p["doc_id"] for p in passages],
                "answerable_p": check.get("answerable_p"),
                "internal_p": check.get("internal_p"),
            }
            con = db.connect()
            con.execute(
                "INSERT OR REPLACE INTO signal_runs (event_id, signal_version, result_json, evaluated_at) VALUES (?,?,?,?)",
                (
                    event["event_id"],
                    "knowledge_answer@v0.1",
                    json.dumps({"signal": "knowledge_answer", "value": knowledge["answerable_p"], "passages": knowledge["passages"]}),
                    now(),
                ),
            )
            con.commit()
            con.close()
            if check.get("usage"):
                con = db.connect()
                con.execute(
                    "INSERT INTO token_usage (provider, model, workflow, input_tokens, output_tokens, recorded_at) VALUES (?,?,?,?,?,?)",
                    ("jev", check.get("model_id"), "knowledge_check", check["usage"].get("input_tokens"), check["usage"].get("output_tokens"), now()),
                )
                con.commit()
                con.close()
            names.append("knowledge_answer")
    state["knowledge"] = knowledge
    transition(state, "signals_ready", ",".join(names))
    return state


def gate(state: AgentState) -> AgentState:
    event = state["event"]
    jev_result = state.get("jev", {})
    verdict = jev.reduce_gate(jev_result)
    decision = {
        "event_id": event["event_id"],
        "policy_version": POLICY_VERSION,
        "gate_version": GATE_VERSION,
        "model_id": verdict["model_id"],
        "prompt_version": jev_result.get("prompt_version"),
        "prompt_hash": jev_result.get("prompt_hash"),
        "norm_version": jev.NORM_VERSION,
        "example_snapshot_id": jev.EXAMPLE_SNAPSHOT_ID,
        "result_status": jev_result.get("result_status"),
        "verdict": verdict["verdict"],
        "band": verdict["band"],
        "confidence": verdict["confidence"],
        "reason": verdict["reason"],
        "signals_fired": [r["id"] for r in state.get("signals", []) if r["value"] == "TRUE"],
        "retrieved_ids": state.get("knowledge", {}).get("passages", []),
    }
    knowledge = state.get("knowledge", {})
    if knowledge.get("answerable_p") is not None:
        decision["reason"] += f" · knowledge answerable {knowledge['answerable_p']:.2f} ({','.join(knowledge.get('passages', []))})"
    con = db.connect()
    con.execute(
        "INSERT INTO decisions (event_id, policy_version, gate_version, model_id, prompt_version, verdict, band, confidence, reason, context_refs_json, prompt_hash, norm_version, example_snapshot_id, result_status, decided_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))",
        (
            decision["event_id"],
            decision["policy_version"],
            decision["gate_version"],
            decision["model_id"],
            decision["prompt_version"],
            decision["verdict"],
            decision["band"],
            decision["confidence"],
            decision["reason"],
            json.dumps(decision["retrieved_ids"]),
            decision["prompt_hash"],
            decision["norm_version"],
            decision["example_snapshot_id"],
            decision["result_status"],
        ),
    )
    con.commit()
    con.close()
    state["decision"] = decision
    record(state, "decided", f"{decision['band']}:{decision['verdict']}")
    return state


def draft(state: AgentState) -> AgentState:
    event = state["event"]
    knowledge = state.get("knowledge", {})
    doc_ids = knowledge.get("passages", [])
    docs = [d for d in memory.recall(event.get("text", ""), k=3) if d["doc_id"] in doc_ids] if doc_ids else []
    answerable = knowledge.get("answerable_p") or 0.0
    internal = knowledge.get("internal_p") or 0.0
    result = {
        "text": "",
        "source_ids": [],
        "uncertainty": "not a knowledge question" if internal < 0.50 else "not answerable from the knowledge base",
        "escalate": True,
    }
    if docs and answerable >= 0.70 and internal >= 0.50:
        result = generate.draft_answer(event.get("text", ""), docs)
    state["draft"] = result
    con = db.connect()
    con.execute(
        "INSERT INTO audit (community_id, actor, action, detail_json, created_at) VALUES (?,?,?,?,datetime('now'))",
        (event.get("community_id"), "beadle", "draft_answer", json.dumps({"event_id": event["event_id"], **result})),
    )
    con.commit()
    con.close()
    reason = (
        f"faq draft from {','.join(result.get('source_ids') or [])}"
        if result.get("source_ids")
        else f"no doc-grounded draft ({result.get('uncertainty')})"
    )
    record(state, "drafted", reason)
    return state


def route_after_gate(state: AgentState) -> str:
    band = state["decision"]["band"]
    if band == "AUTO":
        return "resolve"
    if band == "DRAFT":
        return "escalate"
    return "learn"


def escalate(state: AgentState) -> AgentState:
    event = state["event"]
    decision = state["decision"]
    intent_id = f"card-{event['event_id']}"
    con = db.connect()
    con.execute(
        "INSERT OR REPLACE INTO action_intents (id, event_id, action_type, target_key, idempotency_key, status, created_at, updated_at) VALUES (?,?,?,?,?,?,datetime('now'),datetime('now'))",
        (intent_id, event["event_id"], "mod_queue_card", event.get("channel_id", ""), f"{event['community_id']}:{event['event_id']}:card", "pending"),
    )
    con.commit()
    con.close()
    state["action"] = {"type": "mod_queue_card", "intent_id": intent_id, "reason": decision["reason"]}
    record(state, "approval_pending", "quarantine card created")
    return state


def resolve(state: AgentState) -> AgentState:
    event = state["event"]
    decision = state["decision"]
    action_type = "post_answer" if decision["verdict"] == "answer" else "no_action"
    intent_id = f"act-{event['event_id']}"
    con = db.connect()
    con.execute(
        "INSERT OR REPLACE INTO action_intents (id, event_id, action_type, target_key, idempotency_key, status, created_at, updated_at) VALUES (?,?,?,?,?,?,datetime('now'),datetime('now'))",
        (intent_id, event["event_id"], action_type, event.get("channel_id", ""), f"{event['community_id']}:{event['event_id']}:{action_type}", "pending"),
    )
    con.commit()
    con.close()
    state["action"] = {"type": action_type, "intent_id": intent_id, "reason": decision["reason"]}
    record(state, "action_pending", action_type)
    return state


def learn(state: AgentState) -> AgentState:
    event = state["event"]
    admin = state.get("admin_verdict")
    if admin:
        con = db.connect()
        con.execute(
            "INSERT INTO overrides (event_id, admin_user_id, verdict, reason_code, message_class, resulting_action, created_at) VALUES (?,?,?,?,?,?,datetime('now'))",
            (event["event_id"], admin.get("admin_user_id"), admin.get("verdict"), admin.get("reason_code"), admin.get("message_class"), admin.get("resulting_action")),
        )
        con.commit()
        con.close()
        record(state, "learning_candidate", "override recorded")
    else:
        record(state, "recorded", "awaiting human verdict")
    return state


def build_graph(checkpoint_path=db.CHECKPOINT_DB):
    builder = StateGraph(AgentState)
    builder.add_node("observe", observe)
    builder.add_node("classify", classify)
    builder.add_node("gate", gate)
    builder.add_node("draft", draft)
    builder.add_node("escalate", escalate)
    builder.add_node("resolve", resolve)
    builder.add_node("learn", learn)
    builder.add_edge(START, "observe")
    builder.add_edge("observe", "classify")
    builder.add_edge("classify", "gate")
    builder.add_conditional_edges("gate", route_after_gate, {"resolve": "draft", "escalate": "escalate", "learn": "learn"})
    builder.add_edge("draft", "resolve")
    builder.add_edge("escalate", "learn")
    builder.add_edge("resolve", "learn")
    builder.add_edge("learn", END)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpointer = SqliteSaver(sqlite3.connect(str(checkpoint_path), check_same_thread=False))
    return builder.compile(checkpointer=checkpointer)
