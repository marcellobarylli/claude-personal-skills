import json

import pytest

from tasklog import store
from tasklog.models import Task


def test_roundtrip(tmp_path):
    path = tmp_path / "t.json"
    store.save(path, [Task(id=1, title="a"), Task(id=2, title="b", done=True)])
    assert [t.title for t in store.load(path)] == ["a", "b"]


def test_missing_file_is_empty(tmp_path):
    assert store.load(tmp_path / "nope.json") == []


def test_duplicate_ids_rejected(tmp_path):
    path = tmp_path / "t.json"
    path.write_text(json.dumps([{"id": 1, "title": "a"}, {"id": 1, "title": "b"}]))
    with pytest.raises(ValueError):
        store.load(path)
