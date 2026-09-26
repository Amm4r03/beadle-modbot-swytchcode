import json
import os
import sqlite3
import subprocess
from pathlib import Path

SWY_BIN = os.environ.get("SWY_BIN", "swy")
DEFAULT_TIMEOUT = 60
STATE_DB = Path(__file__).resolve().parent.parent / "data" / "state.db"


def decision_context(event_id: str) -> dict:
    try:
        con = sqlite3.connect(str(STATE_DB), timeout=5)
        con.row_factory = sqlite3.Row
        decision = con.execute(
            "SELECT band, verdict, confidence, reason, prompt_version FROM decisions WHERE event_id = ? ORDER BY id DESC LIMIT 1",
            (event_id,),
        ).fetchone()
        event = con.execute(
            "SELECT platform, community_id FROM inbox_events WHERE id = ?", (event_id,)
        ).fetchone()
        con.close()
        return {"decision": dict(decision) if decision else {}, "event": dict(event) if event else {}}
    except Exception:
        return {"decision": {}, "event": {}}


class SwytchcodeError(RuntimeError):
    pass


def _run(cmd: list[str], timeout: int = DEFAULT_TIMEOUT) -> dict:
    completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    payload = None
    for line in reversed(completed.stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                payload = json.loads(line)
                break
            except json.JSONDecodeError:
                continue
    if completed.returncode != 0:
        error = (payload or {}).get("error") or completed.stderr.strip()[-200:] or "unknown error"
        raise SwytchcodeError(f"exit {completed.returncode}: {error}")
    return payload or {}


def exec_action(canonical_id: str, *, inputs: dict | None = None, body: dict | None = None, dry_run: bool = False) -> dict:
    cmd = [SWY_BIN, "exec", canonical_id, "--json"]
    for key, value in (inputs or {}).items():
        cmd += ["--input", f"{key}={value}"]
    if body is not None:
        cmd += ["--body", json.dumps(body)]
    if dry_run:
        cmd.append("--dry-run")
    return _run(cmd)


def post_discord_message(channel_id: str, content: str, dry_run: bool = False) -> dict:
    return exec_action(
        "discord.message.create",
        inputs={"channel_id": channel_id},
        body={"content": content},
        dry_run=dry_run,
    )


def post_slack_message(channel: str, text: str, dry_run: bool = False) -> dict:
    result = exec_action("slack.chat.postmessage.create", body={"channel": channel, "text": text}, dry_run=dry_run)
    data = result.get("data") or {}
    if data.get("ok") is False:
        raise SwytchcodeError(f"slack error: {data.get('error')}")
    return result


def create_notion_page(parent_page_id: str, title: str, text: str, dry_run: bool = False) -> dict:
    body = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "properties": {"title": {"title": [{"text": {"content": title}}]}},
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]},
            }
        ],
    }
    return exec_action("notion.page.create", body=body, dry_run=dry_run)


def send_digest(to_email: str, subject: str, text: str, html: str | None = None, dry_run: bool = False) -> dict:
    allowed = os.environ.get("DIGEST_TO", "")
    if to_email != allowed:
        raise SwytchcodeError(f"recipient {to_email!r} is not the configured admin address - member-triggered email is blocked")
    body = {"from": os.environ.get("RESEND_FROM", "Beadle <onboarding@resend.dev>"), "to": [to_email], "subject": subject, "text": text}
    if html:
        body["html"] = html
    return exec_action("resend.email.create", body=body, dry_run=dry_run)


def write_ledger(event_id: str, text: str, band: str, verdict: str, confidence: float, reason: str) -> dict:
    parent = os.environ.get("NOTION_PARENT_PAGE_ID", "")
    title = f"Ledger - {event_id} ({band}:{verdict})"
    body = f"Event: {event_id}\nDecision: {band}:{verdict} - confidence {confidence:.2f}\nMessage: {text[:200]}\nReason: {reason}"
    return create_notion_page(parent, title, body)


def notify_admin(event_id: str, text: str, band: str, verdict: str, confidence: float, reason: str) -> dict:
    to = os.environ.get("DIGEST_TO", "")
    subject = f"Beadle escalation - {event_id} ({band}:{verdict})"
    body = (
        f"Escalation from the gate engine (admin notification only - members cannot trigger email).\n"
        f"Event: {event_id}\nDecision: {band}:{verdict} (confidence {confidence:.2f})\n"
        f"Message: {text[:200]}\nReason: {reason}\nConsole: http://localhost:5173/admin"
    )
    return send_digest(to, subject, body)


def _attempt(name: str, fn) -> dict:
    try:
        return {"step": name, "result": fn()}
    except Exception as error:
        return {"step": name, "error": str(error)}


def run_chain(event_id: str, community_id: str = "tg:maplenest", dry_run: bool = False) -> dict:
    parent_page_id = os.environ.get("NOTION_PARENT_PAGE_ID", "")
    slack_channel = os.environ.get("SLACK_CHANNEL_ID", "")
    discord_channel = os.environ.get("DISCORD_CHANNEL_ID", "")
    digest_to = os.environ.get("DIGEST_TO", "")
    ledger_holder: dict = {}

    context = decision_context(event_id)
    decision = context["decision"]
    origin = context["event"]
    platform = origin.get("platform", "telegram")
    community = origin.get("community_id", community_id)
    band = decision.get("band", "?")
    verdict = decision.get("verdict", "?")
    confidence = float(decision.get("confidence") or 0.0)
    reason = decision.get("reason", "no decision recorded")
    prompt_version = decision.get("prompt_version", "?")

    report_text = (
        f"Beadle decision report\n"
        f"Event: {event_id} · {platform} · {community}\n"
        f"Decision: {band}:{verdict} · confidence {confidence:.2f}\n"
        f"Reason: {reason}\n"
        f"Prompt: {prompt_version}\n"
        f"Chain: Notion report -> Slack escalation -> Resend digest"
    )

    def ledger_step():
        result = create_notion_page(parent_page_id, f"Beadle report - {event_id}", report_text, dry_run=dry_run)
        ledger_holder["url"] = (result.get("data") or {}).get("url", "")
        return result

    def slack_step():
        return post_slack_message(
            slack_channel,
            f"Beadle escalation: {event_id} ({platform}/{community}) -> {band}:{verdict} (conf {confidence:.2f}). Report: {ledger_holder.get('url') or 'pending'}",
            dry_run=dry_run,
        )

    def discord_step():
        return post_discord_message(
            discord_channel,
            f"Beadle: {event_id} -> {band}:{verdict} (conf {confidence:.2f}). Report: {ledger_holder.get('url') or 'pending'}",
            dry_run=dry_run,
        )

    def digest_step():
        report_url = ledger_holder.get("url") or "pending"
        text = (
            f"Beadle Agent - escalation digest\n"
            f"Where this came from: {platform} · {community} · event {event_id}\n"
            f"Decision: {band}:{verdict} (confidence {confidence:.2f})\n"
            f"Reason: {reason}\n"
            f"Report: {report_url}\n"
        )
        html = f"""<div style="font-family:ui-monospace,Menlo,monospace;background:#0b0e13;color:#e6ecf5;padding:24px;border-radius:10px;max-width:640px">
<h2 style="margin:0 0 2px">Beadle Agent</h2>
<p style="color:#8b98ad;margin:0 0 16px;font-size:12px">Escalation digest - generated by the gate engine</p>
<p style="margin:6px 0"><b>Where this came from:</b> {platform} · {community} · event <code>{event_id}</code></p>
<p style="margin:6px 0"><b>Decision:</b> {band}:{verdict} · confidence {confidence:.2f}</p>
<p style="margin:6px 0"><b>Reason:</b> {reason}</p>
<p style="margin:6px 0"><b>Report:</b> <a style="color:#7aa2f7" href="{report_url}">{report_url}</a></p>
<p style="color:#8b98ad;font-size:12px;margin-top:16px">Chain: Notion report &rarr; Slack escalation &rarr; this digest. Prompt {prompt_version}.</p>
</div>"""
        return send_digest(digest_to, f"Beadle Agent - escalation {event_id}", text, html=html, dry_run=dry_run)

    steps = [_attempt("notion.page.create", ledger_step)]
    steps.append(_attempt("slack.chat.postmessage.create", slack_step) if slack_channel else {"step": "slack.chat.postmessage.create", "skipped": "SLACK_CHANNEL_ID missing"})
    steps.append(_attempt("discord.message.create", discord_step) if discord_channel else {"step": "discord.message.create", "skipped": "DISCORD_CHANNEL_ID missing"})
    steps.append(_attempt("resend.email.create", digest_step) if digest_to else {"step": "resend.email.create", "skipped": "DIGEST_TO missing"})
    return {"event_id": event_id, "dry_run": dry_run, "steps": steps}


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "tg-demo-msg-a"
    result = run_chain(target, dry_run="--dry-run" in sys.argv)
    print(json.dumps(result, indent=2, default=str))
