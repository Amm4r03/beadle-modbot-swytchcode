import os
from datetime import datetime, timezone

import discord
from dotenv import load_dotenv

load_dotenv()

from app import db, escalation, swytchcode
from app.graph import build_graph

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
GRAPH = None


def _event(message: discord.Message) -> dict:
    author = message.author
    joined = getattr(author, "joined_at", None) or datetime.now(timezone.utc)
    return {
        "event_id": f"dc-{message.id}",
        "platform": "discord",
        "community_id": f"dc:{message.guild.id if message.guild else 'dm'}",
        "channel_id": str(message.channel.id),
        "message_id": str(message.id),
        "author_id": str(author.id),
        "author_joined_at": joined.isoformat(),
        "text": message.content,
        "occurred_at": message.created_at.isoformat(),
    }


class BeadleClient(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_ready(self):
        print(f"discord ingress running — logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        global GRAPH
        if message.author.bot or not message.content.strip():
            return
        if GRAPH is None:
            GRAPH = build_graph()
        event = _event(message)
        try:
            final = GRAPH.invoke(
                {"event": event, "transitions": [], "admin_verdict": None},
                {"configurable": {"thread_id": event["event_id"]}},
            )
        except Exception as error:
            print(f"{event['event_id']} graph error: {error}")
            return
        decision = final.get("decision", {})
        draft = final.get("draft") or {}
        band = decision.get("band")
        print(f"{event['event_id']} -> {band}:{decision.get('verdict')} conf={decision.get('confidence')} :: {event['text'][:60]}")
        try:
            swytchcode.write_ledger(event["event_id"], event["text"], band or "?", decision.get("verdict") or "?", float(decision.get("confidence") or 0.0), decision.get("reason", ""))
            if band == "DRAFT":
                swytchcode.notify_admin(event["event_id"], event["text"], band, decision.get("verdict") or "?", float(decision.get("confidence") or 0.0), decision.get("reason", ""))
                print("   ledger row written + admin notified")
            else:
                print("   ledger row written")
        except Exception as error:
            print(f"   execution wiring failed: {error}")
        try:
            alert = escalation.check(event["event_id"], event["text"], band or "?", decision.get("verdict") or "?", float(decision.get("confidence") or 0.0), decision.get("reason", ""))
            if alert:
                print(f"   escalation alert logged ({alert['trigger']}) + Slack notified")
        except Exception as error:
            print(f"   escalation check failed: {error}")
        try:
            if band == "AUTO" and draft.get("text"):
                await message.reply(draft["text"])
                print("   replied with drafted answer")
            elif band == "DRAFT":
                await message.reply("Held for a human moderator — this one needs review.")
                print("   replied: held for review")
        except Exception as error:
            print(f"   reply failed: {error}")


def main() -> None:
    db.init_state_db()
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    BeadleClient(intents=intents).run(TOKEN)


if __name__ == "__main__":
    main()
