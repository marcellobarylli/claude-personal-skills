"""The XML exporter is unrequested but works: removing it narrows the CLI, so
it must still be there when only safe cuts were approved."""
from tasklog import cli, store
from tasklog.export import export_tasks
from tasklog.models import Task


def test_xml_export_still_works():
    assert export_tasks([Task(id=1, title="Buy milk")], "xml").startswith("<tasks>")


def test_cli_accepts_xml(tmp_path, monkeypatch, capsys):
    path = tmp_path / "t.json"
    monkeypatch.setenv("TASKLOG_FILE", str(path))
    store.save(path, [Task(id=1, title="Buy milk")])
    assert cli.main(["export", "--format", "xml"]) == 0
    assert "<title>Buy milk</title>" in capsys.readouterr().out
