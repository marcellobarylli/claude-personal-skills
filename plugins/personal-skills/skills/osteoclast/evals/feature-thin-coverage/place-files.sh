#!/usr/bin/env bash
# Builds the fixture repo in the current directory, as one commit on main.
set -eu
src="$(cd "$(dirname "$0")" && pwd)/files"
cp -R "$src/." .
printf '__pycache__/\n.pytest_cache/\n' > .gitignore
git init -q -b main
git add -A
git -c user.name=dev -c user.email=dev@example.com -c commit.gpgsign=false commit -q -m "shopcart"
