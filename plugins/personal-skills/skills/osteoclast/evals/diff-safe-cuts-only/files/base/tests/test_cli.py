from tasklog import cli


def test_add_list_done(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("TASKLOG_FILE", str(tmp_path / "t.json"))
    assert cli.main(["add", "Buy milk", "--tag", "home"]) == 0
    assert cli.main(["done", "1"]) == 0
    capsys.readouterr()
    assert cli.main(["list"]) == 0
    assert capsys.readouterr().out == "[x] 1 Buy milk\n"


def test_done_unknown_id(tmp_path, monkeypatch):
    monkeypatch.setenv("TASKLOG_FILE", str(tmp_path / "t.json"))
    assert cli.main(["done", "9"]) == 1
