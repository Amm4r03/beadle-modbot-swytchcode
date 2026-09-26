import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from app import db
from app.graph import build_graph
from app.state import now

FIXTURE = Path("fixtures/maple_nest/telegram_messages.json")


def fixture_event(role: str = "genuine_member_question") -> dict:
    data = json.loads(FIXTURE.read_text())
    message = next(m for m in data["live_pair"] if m["role"] == role)
    joined = "2026-09-18T09:00:00+05:30" if "lurker" in message.get("from_meta", "") else "2026-05-19T09:00:00+05:30"
    return {
        "event_id": f"tg-demo-{message['id'].lower()}",
        "platform": "telegram",
        "community_id": "tg:maplenest",
        "channel_id": "-1001234567890",
        "message_id": message["id"],
        "author_id": message["from"],
        "author_joined_at": joined,
        "text": message["text"],
        "occurred_at": "2026-09-26T12:10:00+05:30",
    }


def run(role: str) -> dict:
    db.init_state_db()
    graph = build_graph()
    event = fixture_event(role)
    config = {"configurable": {"thread_id": event["event_id"]}}
    final = graph.invoke({"event": event, "transitions": [], "admin_verdict": None}, config)
    return final


if __name__ == "__main__":
    for role in ("genuine_member_question", "polished_scam"):
        result = run(role)
        decision = result["decision"]
        print(f"\n=== {role} ===")
        print(f"verdict: {decision['verdict']} | band: {decision['band']} | confidence: {decision['confidence']:.2f}")
        print(f"reason: {decision['reason']}")
        print(f"signals fired: {decision['signals_fired']}")
        print("transitions:")
        for item in result["transitions"]:
            print(f"  -> {item['to_state']} ({item['reason_code']})")
