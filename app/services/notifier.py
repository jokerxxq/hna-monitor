from __future__ import annotations

import requests

from app.config import settings


def send_wechat_message(title: str, desp: str) -> tuple[bool, str]:
    if settings.wechat_provider.lower() != "serverchan":
        return False, "Unsupported wechat_provider. Use serverchan."

    if not settings.serverchan_sendkey:
        return False, "SERVERCHAN_SENDKEY is empty."

    url = f"https://sctapi.ftqq.com/{settings.serverchan_sendkey}.send"
    try:
        resp = requests.post(url, data={"title": title, "desp": desp}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 0:
            return True, "ok"
        return False, str(data)
    except Exception as exc:
        return False, f"request error: {exc}"
