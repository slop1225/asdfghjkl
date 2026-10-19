#!/usr/bin/env python3
"""Poll the yuzurisa shadowban API and append results to data/history.json"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path

ACCOUNTS = ["keepsayinitkris", "insanejarona", "keptsayinitkris"]
API = "https://shadowban-api.yuzurisa.com:444/{}"
HISTORY_PATH = Path("data/history.json")
MAX_ENTRIES = 2000  # keep last N checks per account

def fetch(handle: str) -> dict:
    url = API.format(handle)
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e), "profile": {"exists": False}}

def is_banned(tests: dict | None) -> bool | None:
    if not tests:
        return None
    search_ban = tests.get("search") is False
    suggestion_ban = tests.get("typeahead") is False
    ghost_ban = (tests.get("ghost") or {}).get("ban") is True
    reply_deboost = (tests.get("more_replies") or {}).get("ban") is True
    return search_ban or suggestion_ban or ghost_ban or reply_deboost

def main():
    history = {"accounts": {}, "lastUpdated": None}
    if HISTORY_PATH.exists():
        history = json.loads(HISTORY_PATH.read_text())

    now = int(time.time() * 1000)

    for handle in ACCOUNTS:
        data = fetch(handle)
        tests = data.get("tests")
        entry = {
            "timestamp": now,
            "banned": is_banned(tests),
            "exists": (data.get("profile") or {}).get("exists", False),
            "tests": tests,
            "error": data.get("error"),
        }
        history.setdefault("accounts", {}).setdefault(handle, []).append(entry)
        # trim old entries
        history["accounts"][handle] = history["accounts"][handle][-MAX_ENTRIES:]

    history["lastUpdated"] = now
    HISTORY_PATH.write_text(json.dumps(history, indent=2))
    print(f"Updated history at {now}")

if __name__ == "__main__":
    main()
