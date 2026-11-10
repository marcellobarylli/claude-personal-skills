#!/bin/bash
# Host side of the compute node: plain bash, no LLM. Starts the egress proxy, then runs the round loop
# (rounds.sh): maker container -> checker containers -> keep or revert, until a named terminal state or the deadline.
# Chains the next job for runs longer than one Slurm job.
# Submit with:  source $SB/ctl/sandbox.conf; sbatch $SBATCH_OPTS -o $SB/logs/job-%j.log --export=ALL,SB=$SB $SB/host/job.sbatch
# Without Slurm: SB=... bash job.sbatch   (no chaining, no signal forwarding)
set -u
: "${SB:?SB not set}"; source "$SB/host/common.sh"
echo "job ${SLURM_JOB_ID:-local} on $(hostname) at $(date -u)"
# ctl/STOP is written by the owner, the disk watchdog or finish(); ctl is read-only to the container.
[ -e "$SB/ctl/STOP" ] && { echo "STOP present: $(head -c 200 "$SB/ctl/STOP"); not starting"; exit 0; }
[ -s "$SB/ctl/DEADLINE" ] || echo $(( $(date +%s) + RUN_HOURS*3600 )) > "$SB/ctl/DEADLINE"
DEADLINE=$(cat "$SB/ctl/DEADLINE")
# This job's own end, so a training run is never started where the time limit would cut it off.
JOB_END=$DEADLINE
if [ -n "${SLURM_JOB_ID:-}" ]; then
  e=$(squeue -h -j "$SLURM_JOB_ID" -o %e 2>/dev/null); e=$(date -d "$e" +%s 2>/dev/null) && JOB_END=$e
fi
LIMIT_END=$(( JOB_END - 900 )); [ $LIMIT_END -gt $DEADLINE ] && LIMIT_END=$DEADLINE   # 900 s: the USR1 margin
CHAINED=""
source "$SB/host/rounds.sh"
load_state
jobs=$(( $(cat "$H/JOBS" 2>/dev/null || echo 0) + 1 )); echo $jobs > "$H/JOBS"
max_jobs=${MAX_JOBS:-$(( RUN_HOURS/23 + 3 ))}          # hard cap on chained jobs and restarts, whatever DEADLINE says
if [ $jobs -gt $max_jobs ]; then
  [ -n "$PENDING" ] && revert_to_accepted "$PENDING"   # never hand over an unverified candidate
  finish EXHAUSTED "job cap reached ($jobs > $max_jobs)"; exit 0
fi
# Chain the next job when the run's deadline lies beyond this job's end (a yield then hands over cleanly).
if [ -n "${SLURM_JOB_ID:-}" ] && [ $DEADLINE -gt $LIMIT_END ] && [ $jobs -lt $max_jobs ]; then
  next=$(sbatch --parsable $SBATCH_OPTS -o "$SB/logs/job-%j.log" --export=ALL,SB="$SB" \
         --dependency=afterany:$SLURM_JOB_ID "$H/job.sbatch") && CHAINED=1
  echo "$next" > "$H/NEXT_JOB"; echo "chained next job $next"
fi
echo "run deadline $(date -u -d @$DEADLINE +%FT%TZ); this job plans to $(date -u -d @$LIMIT_END +%FT%TZ); one check needs up to ${RESERVE}s"
start_proxy || exit 1
# Disk watchdog, host side. Over the limit, the current container is killed outright and STOP is written.
( while sleep "${DISK_CHECK_SECONDS:-60}"; do
    used=$(du -sm "$SB/work" "$SB/home" "$SB/logs" "$SB/state" "$SB/scratch" "$SB/pred" "$SB/artifacts" 2>/dev/null | awk '{s+=$1} END {print s+0}')
    if [ "$used" -gt $(( ${DISK_LIMIT_GB:-50} * 1024 )) ]; then
      echo "host: disk limit ${DISK_LIMIT_GB:-50} GB exceeded (${used} MB) at $(date -u +%FT%TZ)" | tee "$SB/ctl/STOP"
      [ -s "$H/CURPID" ] && kill -KILL "$(cat "$H/CURPID")"; break
    fi
  done ) & DISKW=$!
stopping(){ echo "$1: stopping the current container"; STOPPING=1; [ -n "$CUR" ] && kill -TERM "$CUR"; }
trap 'stopping USR1' USR1
trap 'stopping TERM' TERM

r=0
[ -f "$RS" ] || { baseline; r=$?; }
while [ $r -eq 0 ]; do one_round; r=$?; done
if [ $r -eq 2 ] && [ "$ROUND" -gt 0 ]; then      # an interrupted baseline is simply redone next job
  if grep -qs 'disk limit' "$SB/ctl/STOP"; then
    c=$(git_ro "rev-parse refs/heads/$BRANCH" 2>/dev/null | tail -1)        # park whatever is unverified
    is_sha "$c" && [ "$c" != "$ACCEPTED" ] && revert_to_accepted "$c"
    PENDING=""; CONFIRM=0; M_VAL=""; record INTERRUPTED "disk limit; parked, not kept"
    finish ERROR "$(head -c 200 "$SB/ctl/STOP")"
  else
    abandon_round        # the job's time limit: the chained job resumes from $H/round.state
  fi
fi
kill $DISKW 2>/dev/null
stop_proxy
echo "job done at $(date -u); round $ROUND, accepted $ACCEPTED_N, best ${BEST:-none}; proxy denials this job: $(grep -c ' DENY ' "$H/proxy.log" 2>/dev/null)"
