from pathlib import Path
import json
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_metadata(source_id: str) -> dict:
    p = Path(f"/data/metadata/{source_id}.json")
    if not p.exists():
        return {"source_id": source_id, "error_count": 0}
    return json.loads(p.read_text())


def save_metadata(source_id: str, payload: dict) -> None:
    p = Path(f"/data/metadata/{source_id}.json")
    tmp = p.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp.replace(p)
