import json
from dataclasses import asdict
from pathlib import Path

from .models import Task


def load(path):
    p = Path(path)
    if not p.exists():
        return []
    tasks = [Task(**item) for item in json.loads(p.read_text())]
    ids = [t.id for t in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate task ids in store")
    return tasks


def save(path, tasks):
    Path(path).write_text(json.dumps([asdict(t) for t in tasks], indent=2))


def next_id(tasks):
    return max((t.id for t in tasks), default=0) + 1


def migrate_v0(raw):
    """Convert the pre-1.0 dict-of-dicts layout to a list. Kept for old files."""
    out = []
    for key, value in raw.items():
        item = dict(value)
        item["id"] = int(key)
        item.setdefault("tags", [])
        out.append(item)
    return out


class StoreStats:
    def __init__(self, tasks):
        self.tasks = tasks

    def total(self):
        return len(self.tasks)

    def open(self):
        return len([t for t in self.tasks if not t.done])
