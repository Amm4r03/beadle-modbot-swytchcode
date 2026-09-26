import sqlite3
from pathlib import Path

DATA_DIR = Path("data")
STATE_DB = DATA_DIR / "state.db"
CHECKPOINT_DB = DATA_DIR / "checkpoints.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS inbox_events (
  id TEXT PRIMARY KEY,
  community_id TEXT NOT NULL,
  platform TEXT NOT NULL,
  external_event_id TEXT NOT NULL,
  payload_hash TEXT,
  received_at TEXT NOT NULL,
  state TEXT NOT NULL,
  lease_until TEXT,
  attempt_count INTEGER NOT NULL DEFAULT 0,
  UNIQUE(community_id, platform, external_event_id)
);
CREATE TABLE IF NOT EXISTS normalized_events (
  event_id TEXT PRIMARY KEY,
  channel_id TEXT, message_id TEXT, author_id TEXT,
  author_joined_at TEXT, text TEXT, occurred_at TEXT,
  normalization_version TEXT
);
CREATE TABLE IF NOT EXISTS signal_runs (
  event_id TEXT NOT NULL,
  signal_version TEXT NOT NULL,
  result_json TEXT NOT NULL,
  evaluated_at TEXT NOT NULL,
  PRIMARY KEY(event_id, signal_version)
);
CREATE TABLE IF NOT EXISTS decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL,
  policy_version TEXT, gate_version TEXT, model_id TEXT, prompt_version TEXT,
  verdict TEXT, band TEXT, confidence REAL, reason TEXT,
  context_refs_json TEXT, decided_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS action_intents (
  id TEXT PRIMARY KEY,
  event_id TEXT NOT NULL,
  action_type TEXT NOT NULL,
  target_key TEXT,
  payload_hash TEXT,
  idempotency_key TEXT UNIQUE,
  status TEXT NOT NULL,
  swytchcode_ref TEXT, platform_ref TEXT,
  attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS event_transitions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL,
  from_state TEXT, to_state TEXT NOT NULL,
  occurred_at TEXT NOT NULL, reason_code TEXT
);
CREATE TABLE IF NOT EXISTS overrides (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL,
  admin_user_id TEXT,
  verdict TEXT NOT NULL,
  reason_code TEXT,
  message_class TEXT,
  jev_scores_json TEXT,
  resulting_action TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS threshold_versions (
  version INTEGER PRIMARY KEY,
  bundle_json TEXT NOT NULL,
  reason TEXT,
  activated_at TEXT,
  rollback_of INTEGER
);
CREATE TABLE IF NOT EXISTS token_usage (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  provider TEXT, model TEXT, workflow TEXT,
  input_tokens INTEGER, output_tokens INTEGER, cache_tokens INTEGER,
  recorded_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY, handle TEXT, auth_subject TEXT, created_at TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL, community_id TEXT,
  expires_at TEXT, created_at TEXT, revoked_at TEXT
);
CREATE TABLE IF NOT EXISTS audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  community_id TEXT, actor TEXT, action TEXT, detail_json TEXT,
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS learned_config (
  community_id TEXT PRIMARY KEY,
  schema_version INTEGER NOT NULL,
  config_json TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
"""


def connect(path: Path = STATE_DB) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(path))
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=5000")
    con.row_factory = sqlite3.Row
    return con


def init_state_db() -> None:
    con = connect()
    con.executescript(SCHEMA)
    con.commit()
    con.close()
