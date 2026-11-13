#!/usr/bin/env bash
# Same fixture as feature-thin-coverage: one commit on main.
set -eu
exec bash "$(cd "$(dirname "$0")" && pwd)/../feature-thin-coverage/place-files.sh"
