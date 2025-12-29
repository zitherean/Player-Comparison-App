from datetime import datetime, timezone
from pathlib import Path
import json

def write_last_update():
    path = Path("data/last_update.json")
    path.parent.mkdir(parents=True, exist_ok=True)

    today_utc = datetime.now(timezone.utc)

    payload = {
        "status": "success",
        "updated_at_utc": f"{today_utc.strftime('%A')} {today_utc.day} {today_utc.strftime('%B %Y')}"
    }

    with open(path, "w") as f:
        json.dump(payload, f, indent=2)

def get_last_update():
    path = Path("data/last_update.json")
    if not path.exists():
        return None

    with open(path) as f:
        return json.load(f)