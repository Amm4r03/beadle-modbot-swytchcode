import os

import httpx

BASE = "https://api.telegram.org"


class TelegramDirect:
    def __init__(self, token: str | None = None):
        self.token = token or os.environ["TELEGRAM_BOT_TOKEN"]
        self.base = f"{BASE}/bot{self.token}"

    def _call(self, method: str, **params):
        response = httpx.post(f"{self.base}/{method}", json=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(f"telegram {method} failed: {data.get('description')}")
        return data["result"]

    def get_me(self) -> dict:
        return self._call("getMe")

    def send_message(self, chat_id: str, text: str, reply_to_message_id: int | None = None, parse_mode: str | None = None) -> dict:
        params = {"chat_id": chat_id, "text": text}
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        if parse_mode:
            params["parse_mode"] = parse_mode
        return self._call("sendMessage", **params)

    def delete_message(self, chat_id: str, message_id: int) -> bool:
        return self._call("deleteMessage", chat_id=chat_id, message_id=message_id)

    def get_updates(self, offset: int | None = None, timeout: int = 25) -> list:
        params = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset
        return self._call("getUpdates", **params)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    bot = TelegramDirect()
    me = bot.get_me()
    print(f"telegram direct ok: @{me['username']} (id {me['id']})")
