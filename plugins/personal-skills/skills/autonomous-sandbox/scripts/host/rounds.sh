# Sourced by job.sbatch, after common.sh. Host side, plain bash, no LLM: it owns the loop's verdicts.
# One round = one maker container (driver.sh) -> one checker run in separate containers -> keep or revert.
# Why on the host (see references/failure-modes.md, L1-L4): the maker can read anything mounted in its container and
# rewrite anything it can write. So the hold-out, the counters and the keep/revert decision live where it can't
# reach: $SB/eval and $SB/host are never mounted into the maker; the check runs on a copy, never on /work.
#
# Trusted state: $H/round.state (sourced; written only here, numbers and shas only), $H/rounds.tsv, $H/rounds.log,
# $H/check/ (raw checker output, which may contain hold-out data, so the maker never sees it), $H/OUTCOME.
# Untrusted, never read back as code: everything under $SB/work, logs, scratch, pred, judge-home, out.

RS=$H/round.state; CK=$H/check; MSG=$H/msg
mkdir -p "$CK" "$MSG" "$SB/scratch" "$SB/pred" "$SB/empty" "$SB/artifacts"
STOPPING=""; CUR=""
hlog(){ echo "[$(date -u +%FT%TZ)] host: $*" | tee -a "$H/rounds.log"; }
# Host writes into agent-writable dirs only between containers (no agent process alive), after rm -f, so a planted
# symlink can't redirect the write.
hwrite(){ rm -f "$1"; cat > "$1"; }

load_state(){
  ACCEPTED=$(cat "$H/BASE"); BEST=""; ROUND=0; STALL=0; FAILS=0; ACCEPTED_N=0; COST=0
  PENDING=""; PCLAIM=""; CONFIRM=0     # a candidate awaiting its verdict; the next streak check to run (0 = none)
  [ -f "$RS" ] && source "$RS"
}
save_state(){
  printf 'ACCEPTED=%s\nBEST=%s\nROUND=%s\nSTALL=%s\nFAILS=%s\nACCEPTED_N=%s\nCOST=%s\nPENDING=%s\nPCLAIM=%s\nCONFIRM=%s\n' \
    "$ACCEPTED" "$BEST" "$ROUND" "$STALL" "$FAILS" "$ACCEPTED_N" "$COST" "$PENDING" "$PCLAIM" "$CONFIRM" > "$RS.tmp" && mv "$RS.tmp" "$RS"
}

# run_bg cmd...: run a container in the background so the USR1/TERM trap and the disk watchdog can kill it.
run_bg(){
  "$@" & CUR=$!; echo $CUR > "$H/CURPID"
  local r; while :; do wait $CUR; r=$?; kill -0 $CUR 2>/dev/null || break; done
  CUR=""; rm -f "$H/CURPID"; return $r
}
# Cut a round off only for the job's time limit (USR1/TERM) or the disk watchdog. An owner STOP waits for the
# current round's verdict and takes effect between rounds, so no checked work is thrown away.
interrupted(){ [ -n "$STOPPING" ] || grep -qs 'disk limit' "$SB/ctl/STOP"; }

# --- time planning. Every container step has a hard cap, so the host can tell in advance whether a step fits.
# LIMIT_END = the earlier of the run's DEADLINE (the hard maximum) and this Slurm job's end minus the USR1 margin.
# CHAINED = a next job is queued. Without one, work that can't finish before LIMIT_END ends the run as EXHAUSTED.
job_left(){ echo $(( LIMIT_END - $(date +%s) )); }
RESERVE=${CHECK_RESERVE_SECONDS:-$(( $(eval_seconds) + 600 ))}
# yield <why>: stop this job cleanly and let the chained job continue from round.state (return 3).
yield_job(){
  if [ -n "${CHAINED:-}" ]; then hlog "yielding to the next job: $1"; save_state; return 3; fi
  finish EXHAUSTED "deadline: $1${PENDING:+ (round $ROUND parked unverified at refs/rejected/round-$ROUND)}"
  [ -n "$PENDING" ] && { revert_to_accepted "$PENDING"; PENDING=""; save_state; }
  return 1
}

# --- comparisons (METRIC_GOAL lower|higher; the rubric total is always higher-is-better) ---------------------------
goal(){ [ "$CRITERION" = rubric ] && echo higher || echo "$METRIC_GOAL"; }
num(){ [[ "$1" =~ ^-?[0-9]+(\.[0-9]+)?([eE][-+]?[0-9]+)?$ ]]; }
better(){ [ -z "$2" ] && return 0; awk -v a="$1" -v b="$2" -v d="${MIN_DELTA:-0}" -v g="$(goal)" \
  'BEGIN{exit !((g=="lower") ? a<b-d : a>b+d)}'; }
worse(){ [ -z "$2" ] && return 1; awk -v a="$1" -v b="$2" -v t="${REGRESS_TOLERANCE:-0}" -v g="$(goal)" \
  'BEGIN{exit !((g=="lower") ? a>b+t : a<b-t)}'; }
meets(){ [ "$CRITERION" = rubric ] && { [ "$M_ALLPASS" = 1 ]; return; }
  awk -v a="$1" -v th="$THRESHOLD" -v g="$METRIC_GOAL" 'BEGIN{exit !((g=="lower") ? a<=th : a>=th)}'; }

# --- the checker ------------------------------------------------------------------------------------------------
# Copy the committed work tree (with its ignored deps) to $SB/scratch, so checks can write and /work is never touched.
prepare_copy(){
  rm -rf "$SB/scratch/$REPO"
  SBX_NOSOCK=1 run_bg sandbox_exec --bind "$SB/work:/work:ro" --bind "$SB/scratch:/scratch" -- \
    bash -c "cp -a /work/$REPO /scratch/"
}
# The project's own tests on the copy, with the GPUs. Output goes to logs/, which the maker reads (no hold-out mounted).
run_tests(){
  rm -f "$SB/logs/round-$ROUND-tests.log"
  SBX_GPU=1 SBX_PWD=/scratch/$REPO run_bg sandbox_exec --bind "$SB/scratch:/scratch" -- \
    bash -c 'source /run-ctl/sandbox.conf; timeout "$CHECK_SECONDS" bash -c "$TEST_CMD"' \
    > "$SB/logs/round-$ROUND-tests.log" 2>&1
}
# The full training run, by the host, on the copy, with the GPUs, capped at TRAIN_SECONDS. It sees $SB/data
# (read-only) but never the hold-out. Checkpoints go to /artifacts. Its log goes to logs/: the maker reads it next
# round (loss curves, errors). Reads through the proxy unless TRAIN_OFFLINE=1.
run_train(){
  local seed=$1 off=""; [ "${TRAIN_OFFLINE:-0}" = 1 ] && off=1
  rm -rf "$SB/artifacts"; mkdir -p "$SB/artifacts"; rm -f "$SB/logs/round-$ROUND-train-seed-$seed.log"
  hlog "round $ROUND: training (seed $seed, cap ${TRAIN_SECONDS}s)"
  SBX_NOSOCK=$off SBX_GPU=1 SBX_PWD=/scratch/$REPO run_bg sandbox_exec --env CHECK_SEED=$seed \
    --bind "$SB/scratch:/scratch" --bind "$SB/artifacts:/artifacts" -- \
    bash -c 'source /run-ctl/sandbox.conf; timeout "$TRAIN_SECONDS" bash -c "$TRAIN_CMD"' \
    > "$SB/logs/round-$ROUND-train-seed-$seed.log" 2>&1
}
# measure <seed>: sets M_VAL (empty if none) and M_FAIL (why not); for a rubric also M_ALLPASS and M_FEEDBACK.
# Returns 2 when interrupted.
measure(){
  local seed=$1 tag=round-$ROUND-seed-$1; M_VAL=""; M_ALLPASS=0; M_FEEDBACK=""; M_FAIL="the check produced no metric"
  if [ "$CRITERION" = rubric ]; then run_judge "$seed"; interrupted && return 2; return 0; fi
  if [ -n "${TRAIN_CMD:-}" ] && { [ "$seed" = 1 ] || [ "${STREAK_RETRAIN:-1}" = 1 ]; }; then
    run_train "$seed"; local trc=$?; interrupted && return 2
    [ $trc -eq 124 ] && { M_FAIL="training hit TRAIN_SECONDS (${TRAIN_SECONDS}s)"; return 0; }
    [ $trc -ne 0 ] && { M_FAIL="training failed (rc=$trc)"; return 0; }
  fi
  # Stage 1: SUCCESS_CMD runs the agent's code, fully offline, with the GPUs and the checkpoints read-only. With
  # SCORE_CMD set it sees only the hold-out inputs and writes predictions to /pred; without it, it sees all of
  # $SB/eval and must print METRIC itself.
  local ev=(--bind "$SB/eval:/eval:ro"); [ -n "${SCORE_CMD:-}" ] && ev=(--bind "$SB/eval/inputs:/eval/inputs:ro")
  rm -rf "$SB/pred"; mkdir -p "$SB/pred"
  SBX_NOSOCK=1 SBX_GPU=1 SBX_PWD=/scratch/$REPO run_bg sandbox_exec --env CHECK_SEED=$seed \
    --bind "$SB/scratch:/scratch" --bind "$SB/artifacts:/artifacts:ro" --bind "$SB/pred:/pred" "${ev[@]}" -- \
    bash -c 'source /run-ctl/sandbox.conf; timeout "$CHECK_SECONDS" bash -c "$SUCCESS_CMD"' > "$CK/$tag-stage1.log" 2>&1
  interrupted && return 2
  local src="$CK/$tag-stage1.log"
  if [ -n "${SCORE_CMD:-}" ]; then
    # Stage 2: the owner's frozen scorer, with labels and predictions only. No agent code is mounted at all.
    SBX_NOSOCK=1 SBX_PWD=/eval run_bg sandbox_exec --env CHECK_SEED=$seed \
      --bind "$SB/eval:/eval:ro" --bind "$SB/pred:/pred:ro" -- \
      bash -c 'source /run-ctl/sandbox.conf; timeout "$CHECK_SECONDS" bash -c "$SCORE_CMD"' > "$CK/$tag-stage2.log" 2>&1
    interrupted && return 2
    src="$CK/$tag-stage2.log"
  fi
  local v; v=$(grep -E '^METRIC ' "$src" | tail -1 | cut -d' ' -f2)
  num "$v" && M_VAL=$v
  return 0
}
# Level-4 judge: a fresh claude -p, same model unless JUDGE_MODEL says otherwise, in its own empty home, started
# outside the repo (so no repo CLAUDE.md loads), with the copy read-only and docs/autonomy (the maker's own claims)
# masked. No web tools: a planted URL can't steer it. Its verdict is still the model's opinion: report it as level 4.
run_judge(){
  local seed=$1 out="$CK/round-$ROUND-judge-$1.json" mask=()
  rm -rf "$SB/judge-home"; mkdir -p "$SB/judge-home"
  local d="$SB/scratch/$REPO/docs/autonomy"
  [ -L "$d" ] && rm -f "$d"
  [ -d "$d" ] && mask=(--bind "$SB/empty:/cand/$REPO/docs/autonomy:ro")
  SBX_HOME=$SB/judge-home SBX_PWD=/home/agent run_bg sandbox_exec --bind "$SB/scratch:/cand:ro" "${mask[@]}" -- \
    bash -c 'source /run-ctl/sandbox.conf; cat /run-ctl/JUDGE_PROMPT.md /run-ctl/RUBRIC.md | timeout "$JUDGE_SECONDS" \
      /opt/claude/bin/claude -p --dangerously-skip-permissions --disallowedTools WebFetch WebSearch \
      --model "${JUDGE_MODEL:-$MODEL}" --max-turns "$JUDGE_MAX_TURNS" --output-format json' > "$out" 2>"$out.err"
  local r; r=$(python3 -I "$H/judge-parse.py" "$out") || r=""
  local t; t=$(sed -n 's/^TOTAL //p' <<<"$r")
  num "$t" && M_VAL=$t
  M_ALLPASS=$(sed -n 's/^ALLPASS //p' <<<"$r")
  M_FEEDBACK=$(sed -n '/^FEEDBACK$/,$p' <<<"$r" | tail -n +2)
  JCOST=$(grep -o '"total_cost_usd":[0-9.eE-]*' "$out" | tail -1 | cut -d: -f2); num "$JCOST" && add_cost "$JCOST"
}
add_cost(){ COST=$(awk -v a="$COST" -v b="$1" 'BEGIN{printf "%.4f", a+b}'); }

# --- keep / revert / record (git only in offline containers, never on the host) -----------------------------------
revert_to_accepted(){   # <candidate sha or empty>: park the attempt for the owner, reset the branch.
  local park=":"; is_sha "$1" && park="\$G update-ref refs/rejected/round-$ROUND $1"
  git_rw "$park; \$G checkout -q -f $BRANCH && \$G reset -q --hard $ACCEPTED && \$G clean -fdq" >> "$H/rounds.log" 2>&1
}
# record <decision> <reason>: one row in the host's tsv, one in docs/autonomy/rounds.md (committed, so the next
# round's fresh context learns what was tried, even after a reset), and the maker-facing verdict file.
record(){
  local decision=$1 reason=$2 now; now=$(date -u +%FT%TZ)
  [ -f "$H/rounds.tsv" ] || printf 'round\ttime\tdecision\tmetric\tbest\tstall\tcost_total\taccepted_total\treason\n' > "$H/rounds.tsv"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$ROUND" "$now" "$decision" "${M_VAL:--}" "${BEST:--}" "$STALL" \
    "$COST" "$ACCEPTED_N" "$reason" >> "$H/rounds.tsv"
  hlog "round $ROUND $decision: $reason (metric ${M_VAL:--}, best ${BEST:--}, stall $STALL/$STALL_ROUNDS)"
  printf '| %s | %s | %s | %s | %s | %s |\n' "$ROUND" "$now" "$decision" "${M_VAL:--}" "${BEST:--}" "$reason" > "$MSG/line"
  git_rw 'f=docs/autonomy/rounds.md; mkdir -p docs/autonomy
    [ -f $f ] || printf "%s\n" "# Rounds (written by the host after each check; do not edit)" "" \
      "| round | time | decision | metric | best | reason |" "|---|---|---|---|---|---|" > $f
    cat /msg/line >> $f && $G add $f && $G commit -q --no-verify -m "round '"$ROUND"': '"$decision"' (host verdict)"' \
    --bind "$MSG:/msg:ro" >> "$H/rounds.log" 2>&1
  local h; h=$(git_ro "rev-parse HEAD" 2>/dev/null | tail -1); is_sha "$h" && ACCEPTED=$h
  { echo "Round $ROUND: $decision. $reason"
    echo "Metric this round: ${M_VAL:--}. Best accepted: ${BEST:--}. Goal: $(goal), threshold ${THRESHOLD:-all rubric criteria pass}."
    echo "Rounds without improvement: $STALL of $STALL_ROUNDS. Tests: /logs/round-$ROUND-tests.log"
    [ -n "${TRAIN_CMD:-}" ] && echo "Training log: /logs/round-$ROUND-train-seed-1.log"
    [ -n "$M_FEEDBACK" ] && { echo "Judge feedback (level 4, model opinion):"; echo "$M_FEEDBACK"; }
  } | hwrite "$SB/logs/round-$ROUND-verdict.txt"
  save_state
}

# finish <STATE> <reason>: a named terminal state. Only SUCCESS is success; nothing else is reported as one.
finish(){
  [ -s "$H/OUTCOME" ] && { hlog "already ended ($(cut -f1 "$H/OUTCOME")); not recording $1"; return; }   # first outcome wins
  hlog "OUTCOME $1: $2"
  printf '%s\t%s\t%s\n' "$1" "$(date -u +%FT%TZ)" "$2" > "$H/OUTCOME"
  mkdir -p "$SB/out"; hwrite "$SB/out/OUTCOME" < "$H/OUTCOME"
  [ -f "$H/rounds.tsv" ] && hwrite "$SB/out/rounds.tsv" < "$H/rounds.tsv"
  echo "run ended: $1: $2" > "$SB/ctl/STOP"                 # keeps any chained job from starting another round
  [ -n "${SLURM_JOB_ID:-}" ] && [ -s "$H/NEXT_JOB" ] && scancel "$(cat "$H/NEXT_JOB")" 2>/dev/null
}

# --- one round: maker, check, decide. Returns 0 to continue, 1 when the run has ended, 2 when interrupted,
# 3 when this job yields to the chained one.
baseline(){
  hlog "baseline: measuring the starting commit $ACCEPTED"
  [ $(job_left) -lt "$RESERVE" ] && { yield_job "not enough job time for the baseline"; return; }
  prepare_copy; interrupted && return 2
  measure 1 || return 2
  BEST=$M_VAL; save_state
  hlog "baseline metric ${BEST:-none: $M_FAIL}"
  if [ -n "$BEST" ] && meets "$BEST"; then hlog "baseline already meets the criterion; confirming"; CONFIRM=2; save_state; confirm_streak; return; fi
  return 0
}
# Re-run the check SUCCESS_STREAK-1 more times on the accepted commit (CHECK_SEED 2..n; with TRAIN_CMD and
# STREAK_RETRAIN=1, each one retrains from scratch). All must meet the criterion. Resumable across jobs: CONFIRM
# holds the next check to run, so a resumed streak doesn't repeat a passed check.
confirm_streak(){
  local k; [ "$CONFIRM" -ge 2 ] 2>/dev/null || CONFIRM=2
  prepare_copy; interrupted && return 2
  for k in $(seq "$CONFIRM" "${SUCCESS_STREAK:-3}"); do
    [ $(job_left) -lt "$RESERVE" ] && { yield_job "not enough job time for streak check $k"; return; }
    measure "$k" || return 2
    if [ -z "$M_VAL" ] || ! meets "$M_VAL"; then
      hlog "streak broken at check $k (metric ${M_VAL:-none: $M_FAIL})"; CONFIRM=0; save_state; return 0
    fi
    CONFIRM=$((k+1)); save_state; hlog "streak check $k passed (metric $M_VAL)"
  done
  CONFIRM=0; save_state
  finish SUCCESS "criterion met on ${SUCCESS_STREAK:-3} consecutive checks at $ACCEPTED (metric $BEST; $( [ "$CRITERION" = rubric ] && echo 'level 4: same-model judge, separate context' || echo 'level 1: frozen check'))"
  return 1
}
# After a verdict: the agent's claim and the stall detector.
after_verdict(){
  [ "$1" = NO-OP ] && { finish NO-OP "the agent reported nothing left to do (criterion not met)"; return 1; }
  [ "$1" = BLOCKED ] && { finish BLOCKED "the agent reported the remaining work needs the owner (see STATE.md, Needs owner)"; return 1; }
  [ "$STALL" -ge "$STALL_ROUNDS" ] && { finish STALLED "$STALL rounds without improving the metric (best ${BEST:-none})"; return 1; }
  return 0
}
reject(){ revert_to_accepted "$PENDING"; PENDING=""; STALL=$((STALL+1)); record REVERTED "$1"; }
# Check the pending candidate and keep or revert it. Resumable: if the job ends first, PENDING survives.
evaluate(){
  local claim=$PCLAIM
  [ $(job_left) -lt "$RESERVE" ] && { yield_job "not enough job time to check round $ROUND (needs ${RESERVE}s)"; return; }
  hlog "round $ROUND: checking $PENDING"
  prepare_copy; interrupted && return 2
  run_tests; local trc=$?; interrupted && return 2
  if [ $trc -ne 0 ]; then reject "tests failed (rc=$trc)"
  else
    measure 1 || return 2
    if [ -z "$M_VAL" ]; then reject "$M_FAIL"
    elif worse "$M_VAL" "$BEST"; then reject "metric regressed beyond REGRESS_TOLERANCE"
    else
      ACCEPTED=$PENDING; PENDING=""; ACCEPTED_N=$((ACCEPTED_N+1))
      if better "$M_VAL" "$BEST"; then BEST=$M_VAL; STALL=0; record KEPT "improved the metric"
      else STALL=$((STALL+1)); record KEPT "kept (no regression) but no improvement"; fi
      if meets "$M_VAL"; then
        hlog "criterion met at round $ROUND; confirming the streak"; CONFIRM=2; save_state
        confirm_streak; local s=$?; [ $s -ne 0 ] && return $s
      fi
    fi
  fi
  after_verdict "$claim"
}

one_round(){
  local left budget rc claim cand head
  # Resume what a previous job left open, before anything new.
  if [ -n "$PENDING" ]; then hlog "resuming the check of round $ROUND"; evaluate; return; fi
  if [ "$CONFIRM" -gt 0 ]; then hlog "resuming the streak confirmation"; confirm_streak; local s=$?; [ $s -ne 0 ] && return $s; fi
  grep -qs '^run ended:' "$SB/ctl/STOP" && return 1
  [ -e "$SB/ctl/STOP" ] && { finish STOPPED "owner STOP: $(head -c 200 "$SB/ctl/STOP")"; return 1; }
  left=$(( DEADLINE - $(date +%s) ))
  [ $left -lt $(( MIN_ROUND_SECONDS + RESERVE )) ] && { finish EXHAUSTED "deadline: less than a round (maker ${MIN_ROUND_SECONDS}s + check ${RESERVE}s) left"; return 1; }
  [ $(job_left) -lt $(( MIN_ROUND_SECONDS + RESERVE )) ] && { yield_job "not enough job time for a round"; return; }
  budget=$(( $(job_left) - RESERVE )); [ $budget -gt "$ROUND_MAX_SECONDS" ] && budget=$ROUND_MAX_SECONDS
  ROUND=$((ROUND+1)); save_state; M_VAL=""; M_FEEDBACK=""
  rm -f "$SB/logs/round-$ROUND-verdict.txt"
  hlog "round $ROUND: maker start (budget ${budget}s, $((left/3600))h left in the run)"
  SBX_GPU=1 run_bg sandbox_exec --bind "$SB/work:/work" --bind "$SB/state:/state" --bind "$SB/logs:/logs" \
    --env ROUND=$ROUND --env ROUND_BUDGET=$budget -- bash /run-ctl/driver.sh; rc=$?
  local c; c=$(tail -1 "$SB/logs/round-$ROUND.jsonl" 2>/dev/null | grep -o '"total_cost_usd":[0-9.eE-]*' | cut -d: -f2)
  num "$c" && add_cost "$c"
  interrupted && return 2
  case $rc in
    0|124) FAILS=0 ;;
    10) revert_to_accepted ""; record LIMIT "rate or usage limit; not counted as a round result"
        hlog "backing off ${BACKOFF_SECONDS}s"; sleep "$BACKOFF_SECONDS" & wait $!; return 0 ;;
    20) revert_to_accepted ""; record REVERTED "maker loaded MCP servers"
        finish ERROR "the managed MCP lockout failed in round $ROUND"; return 1 ;;
    *)  FAILS=$((FAILS+1)); revert_to_accepted ""; record REVERTED "maker session failed (rc=$rc)"
        [ $FAILS -ge "$MAX_CONSECUTIVE_FAILURES" ] && { finish ERROR "$FAILS consecutive maker failures"; return 1; }
        sleep $((120*FAILS)) & wait $!; return 0 ;;
  esac
  # The agent's only say in the outcome: it may end the run as NO-OP or BLOCKED, never as SUCCESS.
  claim=$(tail -1 "$SB/logs/round-$ROUND.jsonl" 2>/dev/null | grep -oE 'ROUND-RESULT: (CHANGE|NO-OP|BLOCKED)' | tail -1 | cut -d' ' -f2)
  cand=$(git_ro "rev-parse refs/heads/$BRANCH" 2>/dev/null | tail -1); head=$(git_ro "rev-parse HEAD" 2>/dev/null | tail -1)
  if ! is_sha "$cand"; then revert_to_accepted ""; STALL=$((STALL+1)); record REVERTED "branch $BRANCH unreadable"
  elif [ "$cand" = "$ACCEPTED" ]; then STALL=$((STALL+1)); record BARREN "no change committed${claim:+ (agent: $claim)}"
  elif [ "$head" != "$cand" ]; then PENDING=$cand; reject "HEAD was not on $BRANCH"
  elif ! git_ro "merge-base --is-ancestor $ACCEPTED $cand" >/dev/null 2>&1; then
    PENDING=$cand; reject "history rewritten: last accepted commit is not an ancestor"
  else
    PENDING=$cand; PCLAIM=$claim; save_state
    evaluate; return
  fi
  after_verdict "$claim"
}

# The job is ending mid-round (time limit or disk). A maker session cut off is parked and reverted, never kept
# unverified. A committed candidate whose check was cut off stays PENDING: the next job re-checks it from scratch.
abandon_round(){
  if [ -z "${CHAINED:-}" ] && { [ -n "$PENDING" ] || [ "$CONFIRM" -gt 0 ]; }; then   # last job: nothing will resume it
    [ -n "$PENDING" ] && revert_to_accepted "$PENDING"; PENDING=""; CONFIRM=0
    M_VAL=""; record INTERRUPTED "the last job ended mid-check; parked, not kept"
    finish EXHAUSTED "the last job ended before round $ROUND's check finished"; return
  fi
  if [ -n "$PENDING" ]; then hlog "round $ROUND: check cut off; the next job re-checks $PENDING"; save_state; return; fi
  [ "$CONFIRM" -gt 0 ] && { hlog "streak confirmation cut off; the next job resumes it"; save_state; return; }
  local cand; cand=$(git_ro "rev-parse refs/heads/$BRANCH" 2>/dev/null | tail -1)
  if is_sha "$cand" && [ "$cand" != "$ACCEPTED" ]; then revert_to_accepted "$cand"; fi
  M_VAL=""; record INTERRUPTED "maker session cut off before committing a checked change; parked, not kept"
}
