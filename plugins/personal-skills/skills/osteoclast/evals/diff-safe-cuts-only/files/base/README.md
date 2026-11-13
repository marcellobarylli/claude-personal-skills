# tasklog

A tiny task tracker. Tasks live in a JSON file (`tasks.json`, or `$TASKLOG_FILE`).

    python -m tasklog.cli add "Buy milk" --due 2026-01-05 --tag home
    python -m tasklog.cli list
    python -m tasklog.cli done 1

Run the tests with `python -m pytest -q`.
