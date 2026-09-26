import json

from app import db

DEFAULT_POLICY = {"threat": "delete", "harassment": "delete", "solicitation": "delete", "review": "hold"}


def class_from_reason(reason: str) -> str:
    lowered = (reason or "").lower()
    for key in ("threat", "harassment", "solicitation"):
        if key in lowered:
            return key
    return "review"


def _load(community_id: str) -> dict:
    con = db.connect()
    row = con.execute("SELECT config_json FROM learned_config WHERE community_id = ?", (community_id,)).fetchone()
    con.close()
    if row:
        try:
            return json.loads(row["config_json"]) or {}
        except Exception:
            return {}
    return {}


def action_for(community_id: str, reason: str) -> str:
    policies = dict(DEFAULT_POLICY)
    policies.update((_load(community_id).get("policies") or {}))
    return policies.get(class_from_reason(reason), "hold")


def update_from_override(community_id: str, message_class: str, action: str) -> dict:
    config = _load(community_id)
    config.setdefault("policies", {})
    config["policies"][message_class] = action
    con = db.connect()
    con.execute(
        "INSERT OR REPLACE INTO learned_config (community_id, schema_version, config_json, updated_at) VALUES (?,?,?,datetime('now'))",
        (community_id, 1, json.dumps(config)),
    )
    con.commit()
    con.close()
    return config
