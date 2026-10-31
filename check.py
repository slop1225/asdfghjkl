#!/usr/bin/env python3
"""Poll the yuzurisa shadowban API and append results to data/history.json"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path

ACCOUNTS = ["keepsayinitkris", "insanejarona", "keptsayinitkris"]  # fallback
API = "https://shadowban-api.yuzurisa.com:444/{}"
HISTORY_PATH = Path("data/history.json")
MAX_ENTRIES = 2000

def fetch(handle: str, retries: int = 2) -> dict:
    url = API.format(handle)
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ShadowbanMonitor/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                raw = resp.read().decode()
                if not raw.strip().startswith("{"):
                    raise ValueError("Non-JSON response")
                return json.loads(raw)
        except Exception as e:
            if attempt == retries:
                return {"error": str(e), "profile": {"exists": False}}
            time.sleep(2)
    return {"error": "unknown", "profile": {"exists": False}}

def is_banned(tests: dict | None) -> bool | None:
    if not tests:
        return None
    search_ban = tests.get("search") is False
    suggestion_ban = tests.get("typeahead") is False
    ghost_ban = (tests.get("ghost") or {}).get("ban") is True
    reply_deboost = (tests.get("more_replies") or {}).get("ban") is True
    return bool(search_ban or suggestion_ban or ghost_ban or reply_deboost)

def load_accounts(history):
    tracked = history.get("trackedAccounts")
    if isinstance(tracked, list) and tracked:
        return [a if isinstance(a, str) else a.get("handle") for a in tracked if a]
    return ACCOUNTS

def main():
    history = {"accounts": {}, "lastUpdated": None, "trackedAccounts": ACCOUNTS}
    if HISTORY_PATH.exists():
        try:
            history = json.loads(HISTORY_PATH.read_text())
        except Exception:
            pass

    accounts = load_accounts(history)
    history["trackedAccounts"] = accounts

    now = int(time.time() * 1000)

    for handle in accounts:
        if not handle:
            continue
        data = fetch(handle)
        tests = data.get("tests")
        banned = is_banned(tests)

        entry = {
            "timestamp": now,
            "banned": banned,
            "exists": (data.get("profile") or {}).get("exists", False),
            "tests": tests,
            "error": data.get("error"),
            "source": "scheduled",
        }
        history.setdefault("accounts", {}).setdefault(handle, []).append(entry)
        history["accounts"][handle] = history["accounts"][handle][-MAX_ENTRIES:]

    history["lastUpdated"] = now
    HISTORY_PATH.write_text(json.dumps(history, indent=2))
    print(f"Updated history at {now}")

if __name__ == "__main__":
    main()
