#!/bin/bash
#SBATCH -J sandbox-preflight
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:20:00
# sbatch -p <partition> -o $SB/logs/preflight-%j.log --export=ALL,SB=$SB $SB/host/preflight.sbatch
# Every line must say OK before launch. INFO lines are for the loop prompt.
set -u; : "${SB:?SB not set}"; source "$SB/host/common.sh"
RUN(){ sandbox_exec --bind "$SB/work:/work" --bind "$SB/state:/state" --bind "$SB/logs:/logs" -- bash -c "$1"; }
CODE(){ echo "curl -s -o /dev/null -m 30 -w '%{http_code}' $1"; }
start_proxy || exit 1
trap stop_proxy EXIT
H0=$(eval echo ~$USER)

echo "== filesystem and cluster"
RUN "ls $H0 >/dev/null 2>&1 && echo 'FAIL host home visible' || echo 'OK host home hidden'"
RUN "ls /run/munge >/dev/null 2>&1 && echo 'FAIL munge visible' || echo 'OK munge hidden'; command -v sbatch >/dev/null && echo 'FAIL sbatch inside' || echo 'OK no sbatch'"
RUN "[ \$(ls /proc | grep -c '^[0-9]') -lt 20 ] && echo 'OK own PID namespace' || echo 'FAIL host processes visible'"
RUN "touch /run-ctl/probe 2>/dev/null && echo 'FAIL /run-ctl writable' || echo 'OK /run-ctl read-only'; touch /etc/claude-code/probe 2>/dev/null && echo 'FAIL managed settings writable' || echo 'OK managed settings read-only'"
RUN "touch /sock/probe 2>/dev/null && echo 'FAIL /sock writable' || echo 'OK /sock read-only'"

RUN "[ \"\$(command -v claude)\" = /opt/claude/bin/claude ] && echo 'OK claude CLI from /opt/claude' || echo 'FAIL claude CLI path'; touch /opt/claude/probe 2>/dev/null && echo 'FAIL CLI writable' || echo 'OK CLI read-only'"
echo "== credentials"
RUN "ls ~/.ssh/id_* ~/.codex/auth.json ~/.claude/.credentials.json 2>/dev/null | grep -q . && echo 'FAIL credential files in sandbox home' || echo 'OK no credential files in home'"
RUN "[ \"\$CLAUDE_CODE_OAUTH_TOKEN\" = sk-ant-oat01-sandbox-placeholder ] && echo 'OK only the placeholder token' || echo 'FAIL token env is not the placeholder'"
python3 "$H/egress-proxy.py" find-token "$TOKEN_FILE" "$SB/home" "$SB/work" "$SB/ctl" "$SB/logs" "$SB/state" \
  && echo 'OK real token not in any container-visible path' || echo 'FAIL real token in a container-visible path'

echo "== git"
RUN "[ -z \"\$(git remote)\" ] && echo 'OK no git remotes' || echo 'FAIL remotes: '\$(git remote)"
RUN "[ \"\$(git rev-parse --abbrev-ref HEAD)\" = $BRANCH ] && echo 'OK on $BRANCH' || echo 'FAIL not on $BRANCH'"

echo "== network: only loopback, only through the proxy"
RUN "[ \$(tail -n +3 /proc/net/dev | grep -vc '^ *lo:') -eq 0 ] && echo 'OK only loopback interface' || echo 'FAIL other interfaces present'"
RUN "c=\$(curl -s -o /dev/null -m 10 --noproxy '*' -w '%{http_code}' https://example.com); [ \"\$c\" = 000 ] && echo 'OK no direct egress' || echo \"FAIL direct egress \$c\""
RUN "c=\$($(CODE https://example.com/)); [ \"\$c\" = 200 ] && echo 'OK read any public site (GET example.com)' || echo \"FAIL GET example.com \$c\""
RUN "c=\$($(CODE '-X POST -d x=1 https://httpbin.org/post')); [ \"\$c\" = 403 ] && echo 'OK write refused (POST httpbin)' || echo \"FAIL POST httpbin \$c\""
RUN "c=\$($(CODE '-X POST -d x https://api.anthropic.com/v1/files')); [ \"\$c\" = 403 ] && echo 'OK Anthropic non-inference write refused' || echo \"FAIL POST /v1/files \$c\""
RUN "c=\$($(CODE https://10.0.0.1/)); [ \"\$c\" != 200 ] && echo 'OK private address refused' || echo 'FAIL private address reachable'"
RUN "cd /tmp && git clone -q --depth 1 https://github.com/octocat/Hello-World.git hw 2>/dev/null && echo 'OK git clone over https' || echo 'FAIL git clone'"
RUN "cd /tmp && git clone -q --depth 1 https://github.com/octocat/Hello-World.git hw && cd hw && git commit -q --allow-empty -m t && git push -q origin HEAD:refs/heads/sandbox-probe 2>/dev/null </dev/null && echo 'FAIL push succeeded' || echo 'OK git push impossible'"
RUN "npm view --silent left-pad version >/dev/null 2>&1 && echo 'OK npm registry read' || echo 'FAIL npm registry'"
RUN "pip download -q --no-deps -d /tmp/p six >/dev/null 2>&1 && echo 'OK PyPI read' || echo 'INFO PyPI read failed (pip may be missing)'"

echo "== claude"
RUN "claude -p 'Reply with exactly: ok' --model $MODEL < /dev/null | grep -qi ok && echo 'OK claude via proxy' || echo 'FAIL claude'"
RUN "claude -p 'Reply ok' --model $MODEL --output-format stream-json --verbose < /dev/null | grep -m1 '\"subtype\":\"init\"' | grep -q '\"mcp_servers\":\[\]' && echo 'OK no MCP servers loaded' || echo 'FAIL MCP servers loaded or init line changed'"
RUN "claude -p --dangerously-skip-permissions --max-turns 4 --model $MODEL 'Use the WebFetch tool on https://example.com and reply with only the text of its h1 heading.' < /dev/null | grep -qi 'example domain' && echo 'OK WebFetch through proxy' || echo 'FAIL WebFetch'"
RUN "claude -p --dangerously-skip-permissions --max-turns 3 --model $MODEL 'Run this exact bash command and reply with only its last output line: CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-sandbox-placeholder claude -p \"Reply ok\" < /dev/null >/dev/null 2>&1; echo nested_rc=\$?' < /dev/null | tail -1 | sed 's/^/INFO nested claude from agent shell (placeholder token): /'"

echo "== loop: the maker can't see the checker's inputs or state"
RUN "ls /eval /scratch /pred >/dev/null 2>&1 && echo 'FAIL eval, scratch or pred visible to the maker' || echo 'OK eval, scratch and pred hidden from the maker'"
SBX_NOSOCK=1 sandbox_exec --bind "$SB/work:/work:ro" -- bash -c "[ -e /sock/proxy.sock ] && echo 'FAIL offline checker sees the proxy socket' || echo 'OK offline checker has no proxy socket'"
if [ "${USE_GPU:-0}" = 1 ]; then
  SBX_GPU=1 RUN "nvidia-smi -L >/dev/null 2>&1 && echo \"OK GPU visible to the maker: \$(nvidia-smi -L | wc -l) device(s)\" || echo 'FAIL no GPU in the container (submit preflight with --gres=gpu:1)'"
  SBX_GPU=1 RUN "python3 -c 'import torch; print(\"INFO torch\", torch.__version__, \"cuda\", torch.cuda.is_available())' 2>/dev/null || echo 'INFO torch not importable in the image (fine if the project installs it)'"
  RUN "nvidia-smi >/dev/null 2>&1 && echo 'FAIL GPU visible without SBX_GPU' || echo 'OK GPU only where asked for'"
fi
need=$(( MIN_ROUND_SECONDS + $(eval_seconds) + 600 + 900 ))
t=$(grep -oE -- '--time=[0-9:-]+' <<<"$SBATCH_OPTS" | cut -d= -f2)
if [[ "$t" =~ ^(([0-9]+)-)?([0-9]+):([0-9]+):([0-9]+)$ ]]; then
  have=$(( ${BASH_REMATCH[2]:-0}*86400 + 10#${BASH_REMATCH[3]}*3600 + 10#${BASH_REMATCH[4]}*60 + 10#${BASH_REMATCH[5]} ))
  [ $have -ge $need ] && echo "OK a round fits one job: needs ${need}s of ${have}s" \
                      || echo "FAIL a round doesn't fit one job: needs ${need}s (maker + one check + margins), job has ${have}s"
else echo "FAIL can't read --time=D-HH:MM:SS from SBATCH_OPTS"; fi
[ -n "${TRAIN_CMD:-}" ] && [ "${STREAK_RETRAIN:-1}" = 1 ] && echo "INFO SUCCESS needs $(( ${SUCCESS_STREAK:-3} )) full trainings of up to ${TRAIN_SECONDS}s each"
case "${CRITERION:-}" in
  metric) [ -n "$SUCCESS_CMD" ] && [ -n "$THRESHOLD" ] && echo "OK criterion: metric, $METRIC_GOAL than $THRESHOLD (level 1)" || echo 'FAIL CRITERION=metric needs SUCCESS_CMD and THRESHOLD'
          [ -n "${SCORE_CMD:-}" ] && echo 'OK two-stage check: agent code never sees the labels' || echo 'INFO one-stage check: agent code runs next to all of $SB/eval (weaker)' ;;
  rubric) [ -s "$SB/ctl/RUBRIC.md" ] && [ -s "$SB/ctl/JUDGE_PROMPT.md" ] && echo "OK criterion: rubric, judge ${JUDGE_MODEL:-$MODEL} (level 4, model opinion)" || echo 'FAIL CRITERION=rubric needs ctl/RUBRIC.md and ctl/JUDGE_PROMPT.md' ;;
  *) echo 'FAIL CRITERION must be metric or rubric' ;;
esac

echo "== resources"
echo "INFO disk limit ${DISK_LIMIT_GB:-50} GB, now $(du -sm "$SB/work" "$SB/home" "$SB/logs" "$SB/state" | awk '{s+=$1} END {print s}') MB"
RUN "echo INFO nproc limit \$(ulimit -u); df -h /work | tail -1 | sed 's/^/INFO disk: /'"
echo "INFO proxy denials during preflight: $(grep -c ' DENY ' "$H/proxy.log")"
