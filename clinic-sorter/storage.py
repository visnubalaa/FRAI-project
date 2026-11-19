"""Small JSON-file storage for the nurse queue."""
from __future__ import annotations
import json
import uuid
from datetime import datetime
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent / "data" / "queue.json"

def load_records(path: Path = DATA_FILE) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []

def save_records(records: list[dict], path: Path = DATA_FILE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")

def make_record(processed: dict) -> dict:
    now = datetime.now().astimezone()
    return {
        "record_id": uuid.uuid4().hex[:8].upper(),
        "created_at": now.isoformat(timespec="seconds"),
        "reviewed": False,
        **processed,
    }

def add_record(processed: dict, path: Path = DATA_FILE) -> dict:
    record = make_record(processed)
    records = load_records(path)
    records.insert(0, record)
    save_records(records, path)
    return record

def update_reviewed(record_id: str, reviewed: bool, path: Path = DATA_FILE) -> bool:
    records = load_records(path)
    found = False
    for record in records:
        if record.get("record_id") == record_id:
            record["reviewed"] = bool(reviewed)
            found = True
    if found:
        save_records(records, path)
    return found

def delete_record(record_id: str, path: Path = DATA_FILE) -> bool:
    records = load_records(path)
    new_records = [r for r in records if r.get("record_id") != record_id]
    if len(new_records) == len(records):
        return False
    save_records(new_records, path)
    return True
