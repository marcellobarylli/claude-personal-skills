#!/bin/bash
# Supervisor's read-only window into the agent's repo. Never run git in $SB/work on the host: the agent controls
# that repo's .git/config (core.fsmonitor, core.pager, diff drivers), so host git would run the agent's code as you.
# This runs the command in a fresh container with no network and the work tree mounted read-only.
#   SB=... bash $SB/host/inspect.sh 'log --oneline -10'     (the arguments go to git)
set -u; : "${SB:?SB not set}"; source "$SB/host/common.sh"
sandbox_exec --env SANDBOX_OFFLINE=1 --bind "$SB/work:/work:ro" -- bash -c "git -c core.fsmonitor= -c core.pager=cat --no-pager $*" 2>&1 \
  | head -c 200000
