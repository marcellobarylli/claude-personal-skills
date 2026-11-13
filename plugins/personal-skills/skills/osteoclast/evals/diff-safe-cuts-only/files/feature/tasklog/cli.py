import argparse
import os
import sys
from pathlib import Path

from . import store
from .export import export_tasks
from .export.registry import default_registry
from .models import Task


def build_parser():
    parser = argparse.ArgumentParser(prog="tasklog")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add")
    add.add_argument("title")
    add.add_argument("--due")
    add.add_argument("--tag", action="append", default=[])

    sub.add_parser("list")

    done = sub.add_parser("done")
    done.add_argument("id", type=int)

    export = sub.add_parser("export")
    export.add_argument("--format", choices=default_registry.names(), default="csv")
    export.add_argument("--out")
    export.add_argument("--force", action="store_true")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    path = os.environ.get("TASKLOG_FILE", "tasks.json")
    tasks = store.load(path)

    if args.command == "add":
        task = Task(id=store.next_id(tasks), title=args.title, due=args.due, tags=args.tag)
        tasks.append(task)
        store.save(path, tasks)
        print(f"added {task.id}")
        return 0

    if args.command == "list":
        for t in tasks:
            mark = "x" if t.done else " "
            print(f"[{mark}] {t.id} {t.title}")
        return 0

    if args.command == "done":
        for t in tasks:
            if t.id == args.id:
                t.done = True
                store.save(path, tasks)
                print(f"done {t.id}")
                return 0
        print(f"no task {args.id}", file=sys.stderr)
        return 1

    if args.command == "export":
        # Make sure we have a list of tasks before exporting
        if tasks is None:
            tasks = []
        try:
            text = export_tasks(tasks, args.format)
        except Exception as exc:  # pragma: no cover - defensive
            print(f"export failed: {exc}", file=sys.stderr)
            return 1
        if args.out:
            out = Path(args.out)
            if out.exists() and not args.force:
                print(f"refusing to overwrite {out} (use --force)", file=sys.stderr)
                return 1
            out.write_text(text)
            print(f"wrote {len(tasks)} tasks to {out}")
        else:
            sys.stdout.write(text)
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
