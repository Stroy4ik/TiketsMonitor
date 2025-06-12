import json
from pathlib import Path

SUBS_FILE = Path("subscriptions.json")

def load_subscriptions():
    if SUBS_FILE.exists():
        with open(SUBS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_subscriptions(data):
    with open(SUBS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
