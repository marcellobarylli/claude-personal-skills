#!/usr/bin/env bash
# Builds the fixture repo in the current directory: `main` holds the app,
# `feature/export` adds the export feature an agent overbuilt.
set -eu
src="$(cd "$(dirname "$0")" && pwd)/files"
g() { git -c user.name=dev -c user.email=dev@example.com -c commit.gpgsign=false "$@"; }
cp -R "$src/base/." .
printf '__pycache__/\n.pytest_cache/\n' > .gitignore
git init -q -b main
g add -A
g commit -q -m "tasklog: add, list, done"
git checkout -q -b feature/export
cp -R "$src/feature/." .
g add -A
g commit -q -m "Add export command (see docs/export-request.md)"
