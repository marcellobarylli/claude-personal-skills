#!/bin/bash
# Runs INSIDE the maker container, from /run-ctl (read-only to the agent). It runs exactly ONE round: one headless
# Claude session that plans, gets a critique, makes one change and commits it. It does not judge the round; the host
# (host/rounds.sh) checks the result in a separate container and keeps or reverts it.
# Exit codes, read by the host:  0 session ended normally   124 round hit its time budget
#   10 rate or usage limit   11 other failure   20 MCP servers were loaded   30 TERM received (job ending)
# The supervisor edits this on the host: write driver.sh.new, `bash -n` it, then `mv` it over (M2).
set -u
source /run-ctl/sandbox.conf
CTL=/run-ctl; LOGS=/logs; WORK=/work/$REPO
: "${ROUND:?ROUND not set}" "${ROUND_BUDGET:?ROUND_BUDGET not set}"
DEADLINE=$(cat $CTL/DEADLINE)
log(){ echo "[$(date -u +%FT%TZ)] round $ROUND: $*" | tee -a $LOGS/driver.log; }
CHILD=""; WATCH=""
safety_commit(){        # local only. Hooks are skipped so agent-written hooks cannot block it.
  cd $WORK || return
  if [ -n "$(git status --porcelain)" ]; then
    git add -A && git -c core.hooksPath=/dev/null commit -q --no-verify -m "wip: round $ROUND safety commit $(date -u +%FT%TZ)"
  fi
}
stop_child(){
  [ -n "$WATCH" ] && kill $WATCH 2>/dev/null; WATCH=""
  [ -n "$CHILD" ] || return
  kill -TERM -- -$CHILD 2>/dev/null; sleep 20; kill -KILL -- -$CHILD 2>/dev/null; CHILD=""
}
on_term(){ log "TERM received; stopping"; stop_child; safety_commit; exit 30; }
trap on_term TERM INT

out=$LOGS/round-$ROUND.jsonl
note="Driver note: this is round $ROUND. You have $((ROUND_BUDGET/60)) minutes before the session is killed (run ends $(date -u -d @$DEADLINE +%FT%TZ)). Make ONE change and commit it well within that. Results of earlier rounds, including why rejected ones failed: docs/autonomy/rounds.md and /logs/round-*-verdict.txt."
log "start (budget ${ROUND_BUDGET}s)"
cd $WORK
setsid timeout -k 60 $ROUND_BUDGET /opt/claude/bin/claude -p "$(cat $CTL/LOOP_PROMPT.md)

$note" --dangerously-skip-permissions --model "$MODEL" --max-turns "$MAX_TURNS" \
    --output-format stream-json --verbose > $out 2> $LOGS/round-$ROUND.err < /dev/null &
CHILD=$!
# Stall watchdog: a session whose log has not grown for STALL_SECONDS is killed (e.g. idle sleep timers, R2).
( while sleep 300; do
    age=$(( $(date +%s) - $(stat -c %Y $out) ))
    [ $age -gt $STALL_SECONDS ] && { echo "[$(date -u +%FT%TZ)] round $ROUND: watchdog: stalled ${age}s; killing" >> $LOGS/driver.log; kill -TERM -- -$CHILD; break; }
  done ) & WATCH=$!
wait $CHILD; rc=$?
kill $WATCH 2>/dev/null; WATCH=""
kill -KILL -- -$CHILD 2>/dev/null; CHILD=""     # stray servers / background jobs of the round (R10)
safety_commit
log "end rc=$rc head $(git rev-parse --short HEAD 2>/dev/null)"

# Defence in depth: the managed MCP config allows no servers (search for init; it is not always line 1).
init=$(grep -m1 '"subtype":"init"' $out)
if [ -n "$init" ] && ! echo "$init" | grep -q '"mcp_servers":\[\]'; then log "MCP servers loaded"; exit 20; fi
# Judge the session by its FINAL result line only (R1).
final=$(tail -1 $out | grep '"type":"result"')
[ $rc -eq 124 ] && exit 124
[ $rc -eq 0 ] && [ -n "$final" ] && ! echo "$final" | grep -q '"is_error":true' && exit 0
{ echo "$final"; tail -5 $LOGS/round-$ROUND.err; } | grep -qiE 'rate.?limit|usage limit|limit reached|429|overloaded' && exit 10
exit 11
