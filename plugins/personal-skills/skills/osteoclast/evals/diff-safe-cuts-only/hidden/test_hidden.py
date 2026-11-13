import json

import pytest

from tasklog import cli, store
from tasklog.export import export_tasks
from tasklog.models import Task

TASKS = [
    Task(id=2, title="Call, Bob", done=True),
    Task(id=1, title="Buy milk", due="2026-01-05", tags=["home", "errand"]),
]


def seed(tmp_path, monkeypatch, tasks=TASKS):
    path = tmp_path / "t.json"
    monkeypatch.setenv("TASKLOG_FILE", str(path))
    store.save(path, tasks)
    return path


def test_csv_exact():
    assert export_tasks(TASKS, "csv") == (
        "id,title,done,due,tags\n"
        '2,"Call, Bob",true,,\n'
        "1,Buy milk,false,2026-01-05,home;errand\n"
    )


def test_json_exact():
    expected = [
        {"id": 1, "title": "Buy milk", "done": False, "due": "2026-01-05", "tags": ["home", "errand"]},
        {"id": 2, "title": "Call, Bob", "done": True, "due": None, "tags": []},
    ]
    assert export_tasks(TASKS, "json") == json.dumps(expected, indent=2)


def test_default_format_is_csv():
    assert export_tasks(TASKS) == export_tasks(TASKS, "csv")


def test_cli_rejects_unknown_format(tmp_path, monkeypatch):
    seed(tmp_path, monkeypatch)
    with pytest.raises(SystemExit) as exc:
        cli.main(["export", "--format", "yaml"])
    assert exc.value.code == 2


def test_cli_json_stdout(tmp_path, monkeypatch, capsys):
    seed(tmp_path, monkeypatch)
    assert cli.main(["export", "--format", "json"]) == 0
    assert [t["id"] for t in json.loads(capsys.readouterr().out)] == [1, 2]


def test_cli_out_writes_file(tmp_path, monkeypatch):
    seed(tmp_path, monkeypatch)
    out = tmp_path / "out.csv"
    assert cli.main(["export", "--out", str(out)]) == 0
    assert out.read_text() == export_tasks(TASKS, "csv")


def test_cli_refuses_overwrite(tmp_path, monkeypatch, capsys):
    seed(tmp_path, monkeypatch)
    out = tmp_path / "out.csv"
    out.write_text("precious")
    assert cli.main(["export", "--out", str(out)]) == 1
    assert out.read_text() == "precious"
    assert "overwrite" in capsys.readouterr().err


def test_cli_force_overwrites(tmp_path, monkeypatch):
    seed(tmp_path, monkeypatch)
    out = tmp_path / "out.csv"
    out.write_text("old")
    assert cli.main(["export", "--out", str(out), "--force"]) == 0
    assert out.read_text().startswith("id,title")


def test_empty_store_exports_header_only(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TASKLOG_FILE", str(tmp_path / "none.json"))
    assert cli.main(["export"]) == 0
    assert capsys.readouterr().out == "id,title,done,due,tags\n"


def test_base_commands_still_work(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TASKLOG_FILE", str(tmp_path / "t.json"))
    assert cli.main(["add", "A"]) == 0
    assert cli.main(["done", "1"]) == 0
    capsys.readouterr()
    cli.main(["list"])
    assert capsys.readouterr().out == "[x] 1 A\n"
