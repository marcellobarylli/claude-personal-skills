import argparse
import os
import sys

from . import store
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

    return 2


if __name__ == "__main__":
    sys.exit(main())
