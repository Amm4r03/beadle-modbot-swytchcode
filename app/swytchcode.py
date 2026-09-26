import json
import os
import subprocess

SWY_BIN = os.environ.get("SWY_BIN", "swy")
DEFAULT_TIMEOUT = 60


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
    return exec_action("slack.chat.postmessage.create", body={"channel": channel, "text": text}, dry_run=dry_run)


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


def send_digest(to_email: str, subject: str, text: str, dry_run: bool = False) -> dict:
    body = {"from": os.environ.get("RESEND_FROM", "Beadle <onboarding@resend.dev>"), "to": [to_email], "subject": subject, "text": text}
    return exec_action("resend.email.create", body=body, dry_run=dry_run)


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

    def ledger_step():
        result = create_notion_page(
            parent_page_id,
            f"Decision ledger - {event_id}",
            f"Event {event_id} in {community_id}: gate decision recorded. Chain step 1 (Notion).",
            dry_run=dry_run,
        )
        ledger_holder["url"] = (result.get("data") or {}).get("url", "")
        return result

    def slack_step():
        return post_slack_message(
            slack_channel,
            f"Beadle: gate decision for {event_id} - ledger: {ledger_holder.get('url') or 'pending'}",
            dry_run=dry_run,
        )

    def discord_step():
        return post_discord_message(
            discord_channel,
            f"Beadle: decision for {event_id} - ledger: {ledger_holder.get('url') or 'pending'}",
            dry_run=dry_run,
        )

    def digest_step():
        return send_digest(
            digest_to,
            f"Beadle digest - {event_id}",
            f"Chain complete for {event_id}. Ledger: {ledger_holder.get('url') or 'pending'}",
            dry_run=dry_run,
        )

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
