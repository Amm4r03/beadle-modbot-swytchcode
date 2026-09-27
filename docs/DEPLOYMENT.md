# Beadle — Deployment & Runbook

> Written after the hackathon win (2026-09-26). Everything below runs from the repo root. No Docker is required to run locally; a compose sketch is included for the pilot path but **do not run it until the auth/scoping work lands** (see Next Steps).

## 1 · Run it locally (all services)

```bash
# --- setup (once) ---
cp .env.example .env && ${EDITOR:-vi} .env      # JEV_API_KEY, GROQ_API_KEY, TELEGRAM_BOT_TOKEN,
                                                # DISCORD_BOT_TOKEN, NOTION_API_KEY, RESEND_API_KEY,
                                                # DISCORD_CHANNEL_ID, TELEGRAM_CHAT_ID, NOTION_PARENT_PAGE_ID,
                                                # SLACK_CHANNEL_ID, SLACK_REASONING_CHANNEL, DIGEST_TO, RESEND_FROM
pip install -r requirements.txt
pnpm --dir console install
python3 -c "from app import db; db.init_state_db()"   # create tables (idempotent)
scripts/knowledge seed                                # load knowledge/*.md into the FTS index

# --- smoke test (fixture pair, live Jev) ---
python3 -m app.main

# --- services (each in its own terminal/pane) ---
python3 -m uvicorn api.server:app --port 8788   # API + /test + /live + /test/learning
pnpm --dir console run dev                      # admin console → http://localhost:5173/admin-new
python3 -m app.telegram_ingest                  # Telegram reader (replies, deletes threats)
python3 -m app.discord_ingest                   # Discord reader (requires Message Content intent)
python3 bridge/server.py                        # bridge chat + Instinct webhook (8787)
ngrok http 8787                                 # public tunnel for the bridge (optional)
```

## 2 · One-off utilities

```bash
python3 -m app.swytchcode <event_id>            # live chain: Notion report → Slack escalation → Resend digest
python3 -m app.swytchcode <event_id> --dry-run  # same, no network calls
scripts/trace <event_id>                        # full state trail from the CLI
scripts/knowledge seed | add <file.md> | search "<query>" | list
swy auth status && swy doctor                   # Swytchcode provider connections + diagnostics
swy audit network -n 20 && swy audit policy -n 20
```

## 3 · What runs where

| Service | Port | Notes |
|---|---|---|
| Read API (+ /test, /live, /test/learning) | 8788 | reads `data/state.db` with `PRAGMA query_only`; write paths: ingest/resolve/announce/knowledge |
| Admin console (Vite) | 5173 | `/admin-new` (sidebar dashboard), `/admin` (older) |
| Bridge | 8787 | user chat surface + Instinct webhook + mail poller |
| ngrok | → 8787 | public URL for the bridge |
| Telegram reader | — | direct Bot API long-poll; needs bot in group + privacy off |
| Discord reader | — | gateway; needs **Message Content Intent** on |
| SQLite | — | `data/state.db` (ledger, single writer) + `data/checkpoints.db` (disposable) |

## 4 · Deployment path (what a real pilot needs)

| # | Gap | Work | Est. |
|---|---|---|---|
| 1 | Hosting | VPS/Fly/Railway, process supervision (systemd or Docker), daily SQLite backups, tunnel → webhooks where possible | 2–3 days |
| 2 | Auth | real login on the console (users/sessions tables exist); role check on resolve/announce/knowledge; no more demo admin | 2–3 days |
| 3 | Per-community scoping | `community_id` on knowledge docs; enforce scope server-side on every read (E4 access module) | 2–3 days |
| 4 | Readers at scale | supervise the Telegram poller (restart/backoff), Discord gateway process, Slack Socket Mode reader | 3–5 days |
| 5 | Ops/compliance | retention jobs (raw 7d / derived 90d), PII redaction policy, terms/privacy | 2–3 days |
| 6 | Onboarding | "connect your community" flow: bot tokens, invite links, channel picker, first-run checklist | 3–5 days |
| 7 | Swytchcode blockers | Telegram bundle URL-placeholder bug, Discord OAuth 401 — wait for vendor fix or keep direct APIs (documented) | vendor-dependent |

**Pilot estimate: ~1–2 weeks** (single community, self-hosted, admin-operated). **Multi-tenant product: ~1–2 months** (auth/roles, billing, per-community everything, reliability, support).

Compose sketch for later (not to be run yet):

```yaml
# docker-compose.yml (sketch — pending auth + scoping)
services:
  api:
    build: .
    command: python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8788
    env_file: .env
    volumes: ["./data:/app/data"]
  telegram:
    build: .
    command: python3 -m app.telegram_ingest
    env_file: .env
    volumes: ["./data:/app/data"]
  console:
    build: ./console
    command: pnpm run preview --host
    ports: ["5173:5173"]
```

## 5 · Next steps (when we resume)

1. **Auth + per-community scoping** (gates everything else — the console currently trusts any caller).
2. **Hosting + backups + supervision** (make it survive a restart and a week of uptime).
3. **Reader hardening** (supervised Telegram poller; Discord intent + gateway; Slack Socket Mode).
4. **Onboarding flow** (connect a community end-to-end without a terminal).
5. **Retention + data policy** (7d raw / 90d derived jobs; PII redaction).
6. **Vendor follow-ups** (Swytchcode Telegram bundle bug, Discord OAuth 401; keep the bug report handy).
7. **`topic-decision` skill** (see `docs/TOPIC-SELECTION.md` — codify the process that picked this project).
