from tasklog import cli, store
from tasklog.export import export_tasks
from tasklog.models import Task


def test_csv_basic():
    text = export_tasks([Task(id=1, title="Buy milk")], "csv")
    assert text.splitlines()[0] == "id,title,done,due,tags"
    assert text.splitlines()[1].startswith("1,Buy milk,false")


def test_xml_has_root():
    text = export_tasks([Task(id=1, title="Buy milk")], "xml")
    assert text.startswith("<tasks>")


def test_cli_export_stdout(tmp_path, monkeypatch, capsys):
    path = tmp_path / "t.json"
    monkeypatch.setenv("TASKLOG_FILE", str(path))
    store.save(path, [Task(id=1, title="Buy milk")])
    assert cli.main(["export"]) == 0
    assert "Buy milk" in capsys.readouterr().out
