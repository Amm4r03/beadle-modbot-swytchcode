import time
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from app import db
from app.graph import build_graph
from app.telegram_direct import TelegramDirect


def _event(update: dict) -> dict | None:
    message = update.get("message") or update.get("edited_message") or {}
    text = (message.get("text") or "").strip()
    chat = message.get("chat") or {}
    author = message.get("from") or {}
    if not text or not chat:
        return None
    return {
        "event_id": f"tg-{update['update_id']}",
        "platform": "telegram",
        "community_id": f"tg:{chat.get('id')}",
        "channel_id": str(chat.get("id")),
        "message_id": str(message.get("message_id", update["update_id"])),
        "author_id": str(author.get("id") or author.get("username") or "unknown"),
        "author_joined_at": "2026-09-01T09:00:00+05:30",
        "text": text,
        "occurred_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "_reply_to": message.get("message_id"),
    }


def main() -> None:
    db.init_state_db()
    bot = TelegramDirect()
    graph = build_graph()
    offset = None
    print("telegram ingress running — send a message in the group where the bot is invited")
    while True:
        try:
            updates = bot.get_updates(offset=offset, timeout=10)
        except Exception as error:
            print(f"poll error: {error}")
            time.sleep(3)
            continue
        for update in updates:
            offset = update["update_id"] + 1
            event = _event(update)
            if not event:
                continue
            reply_to = event.pop("_reply_to")
            final = graph.invoke({"event": event, "transitions": [], "admin_verdict": None}, {"configurable": {"thread_id": event["event_id"]}})
            decision = final.get("decision", {})
            draft = final.get("draft") or {}
            band = decision.get("band")
            print(f"{event['event_id']} -> {band}:{decision.get('verdict')} conf={decision.get('confidence')} :: {event['text'][:60]}")
            try:
                if band == "AUTO" and draft.get("text"):
                    bot.send_message(event["channel_id"], draft["text"], reply_to_message_id=reply_to)
                    print("   replied with drafted answer")
                elif band == "AUTO":
                    bot.send_message(
                        event["channel_id"],
                        "I couldn't answer this from the knowledge base - passing it to a human moderator.",
                        reply_to_message_id=reply_to,
                    )
                    print("   replied: no grounded answer - passed to moderator")
                elif band == "DRAFT":
                    if "threat" in decision.get("reason", ""):
                        try:
                            bot.delete_message(event["channel_id"], reply_to)
                            print("   deleted the harmful message")
                        except Exception as error:
                            print(f"   delete failed (needs delete rights/admin): {error}")
                        bot.send_message(event["channel_id"], "Removed for violating community rules - moderators notified.")
                        print("   replied: removed for review")
                    else:
                        bot.send_message(event["channel_id"], "Held for a human moderator - this one needs review.", reply_to_message_id=reply_to)
                        print("   replied: held for review")
            except Exception as error:
                print(f"   reply failed: {error}")
        time.sleep(1)


if __name__ == "__main__":
    main()
