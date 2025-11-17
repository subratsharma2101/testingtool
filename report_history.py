import json
import os
import threading
from datetime import datetime
from typing import Dict, List

HISTORY_FILE = os.path.join('reports', 'run_history.json')
_lock = threading.Lock()


def _read_history() -> List[Dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as handle:
            return json.load(handle)
    except Exception:
        return []


def add_entry(entry: Dict):
    """Append a new run entry to history."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    entry.setdefault('timestamp', datetime.utcnow().isoformat())
    with _lock:
        history = _read_history()
        history.insert(0, entry)
        history = history[:25]
        with open(HISTORY_FILE, 'w', encoding='utf-8') as handle:
            json.dump(history, handle, indent=2, ensure_ascii=False)


def get_history(limit: int = 25) -> List[Dict]:
    """Return recent history entries."""
    with _lock:
        history = _read_history()
    return history[:limit]


