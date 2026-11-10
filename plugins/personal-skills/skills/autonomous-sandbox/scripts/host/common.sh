# Sourced by the host-side scripts in $SB/host, which is never bound into the container.
# Rule: the host never sources, runs or uses git on anything the container can write ($SB/home, work, state,
# logs, out). It sources only $SB/ctl, which is read-only inside the container.
: "${SB:?SB not set}"
source "$SB/ctl/sandbox.conf"
H=$SB/host
TOKEN_FILE=${TOKEN_FILE:-$H/secrets/claude.env}

# sandbox_exec [apptainer args...] -- cmd args...
# --containall: own PID, IPC and mount namespaces, no host home, clean /tmp. --net --network none: loopback only;
# the host proxy's Unix socket is the only way out. --no-privs: no capabilities. Binds are listed explicitly.
# The Claude CLI comes from $SB/cli, read-only, so the agent cannot patch it to ignore the managed settings.
# Optional environment for one call:
#   SBX_HOME   sandbox home to mount (default $SB/home; the judge gets its own, fresh, so the maker can't plant rules)
#   SBX_PWD    working directory (default /work/$REPO; the judge starts outside the repo so no repo CLAUDE.md loads)
#   SBX_NOSOCK=1  don't mount the proxy socket at all: fully offline, no inference (hold-out checks)
#   SBX_GPU=1     pass the job's GPUs in (--nv), if USE_GPU=1: maker, tests, training, stage 1. Never the judge or git
# $SB/data (the owner's training data, never the hold-out) is mounted read-only at /data when it exists.
sandbox_exec(){
  local extra=(); while [ $# -gt 0 ] && [ "$1" != "--" ]; do extra+=("$1"); shift; done; shift
  local sock=(--bind "$SB/sock:/sock:ro"); [ -n "${SBX_NOSOCK:-}" ] && sock=(--env SANDBOX_OFFLINE=1)
  local gpu=() data=() genv=()
  if [ -n "${SBX_GPU:-}" ] && [ "${USE_GPU:-0}" = 1 ]; then
    gpu=(--nv)
    # --cleanenv drops Slurm's CUDA_VISIBLE_DEVICES; APPTAINERENV_ passes it (its commas would break --env).
    [ -n "${CUDA_VISIBLE_DEVICES:-}" ] && genv=("APPTAINERENV_CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES")
  fi
  [ -d "$SB/data" ] && data=(--bind "$SB/data:/data:ro")
  env "${genv[@]}" apptainer exec --containall --cleanenv --no-privs --no-mount hostfs,bind-paths \
    --net --network none \
    --home "${SBX_HOME:-$SB/home}:/home/agent" \
    --bind "$SB/ctl:/run-ctl:ro" --bind "$SB/ctl/managed:/etc/claude-code:ro" "${sock[@]}" \
    --bind "$SB/cli:/opt/claude:ro" \
    "${gpu[@]}" "${data[@]}" "${extra[@]}" --pwd "${SBX_PWD:-/work/$REPO}" "$SB/image/agent.sif" /bin/bash /run-ctl/sandbox-env.sh "$@"
}

# Git on the agent's repo, always inside an offline container, never on the host (X5). The agent controls
# .git/config, so hooks, fsmonitor and the pager are switched off for every call.
G='git -c core.fsmonitor= -c core.hooksPath=/dev/null -c core.pager=cat --no-pager'
git_ro(){ SBX_NOSOCK=1 sandbox_exec --bind "$SB/work:/work:ro" -- bash -c "$G $*"; }
git_rw(){ SBX_NOSOCK=1 sandbox_exec --bind "$SB/work:/work" "${@:2}" -- bash -c "G='$G'; $1"; }
# Upper bound on one check, from the hard caps: tests, training, stage 1 and stage 2 (or the judge).
eval_seconds(){
  if [ "${CRITERION:-metric}" = rubric ]; then echo $(( CHECK_SECONDS + JUDGE_SECONDS + 300 ))
  else
    local n=2 t=0; [ -n "${SCORE_CMD:-}" ] && n=3; [ -n "${TRAIN_CMD:-}" ] && t=${TRAIN_SECONDS:-0}
    echo $(( n * CHECK_SECONDS + t + 300 ))
  fi
}
is_sha(){ [[ "$1" =~ ^[0-9a-f]{40}$ ]]; }

PROXY_PID=""
start_proxy(){
  [ -s "$TOKEN_FILE" ] || { echo "fatal: token file $TOKEN_FILE missing"; return 1; }
  rm -f "$SB/sock/proxy.sock"
  python3 "$H/egress-proxy.py" serve "$SB/sock/proxy.sock" "$H/ca" "$TOKEN_FILE" "$H/proxy.log" \
    >> "$H/proxy.stderr" 2>&1 &
  PROXY_PID=$!
  for _ in $(seq 100); do [ -S "$SB/sock/proxy.sock" ] && return 0; sleep 0.1; done
  echo "fatal: proxy did not start (see $H/proxy.stderr)"; return 1
}
stop_proxy(){ [ -n "$PROXY_PID" ] && kill "$PROXY_PID" 2>/dev/null; PROXY_PID=""; rm -f "$SB/sock/proxy.sock"; }
