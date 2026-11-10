#!/bin/bash
#SBATCH -J sandbox-finaltest
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=00:45:00
# After the run: sbatch -p <partition> -o $SB/logs/finaltest-%j.log --export=ALL,SB=$SB $SB/host/finaltest.sbatch
# Runs the tests on the final state, then writes the handoff bundle and the list of paths that need review.
set -u; : "${SB:?SB not set}"; source "$SB/host/common.sh"
BASE=$(cat "$H/BASE")
RUN(){ sandbox_exec --bind "$SB/work:/work" --bind "$SB/out:/out" -- bash -c "$1"; }
start_proxy || exit 1; trap stop_proxy EXIT
RUN "echo \"HEAD \$(git rev-parse --short HEAD) on \$(git rev-parse --abbrev-ref HEAD)\"; git status --short | head -5; git log --oneline -1"
RUN "$TEST_CMD"; echo "TEST rc=$?"
[ -n "$EXTRA_CHECK_CMD" ] && { RUN "$EXTRA_CHECK_CMD" 2>&1 | grep -v ': ok$' | tail -20; }
B=/out/$REPO-$BRANCH.bundle
RUN "rm -f $B; git bundle create -q $B $BRANCH --glob=refs/rejected && git bundle verify -q $B && echo \"BUNDLE $SB/out/$REPO-$BRANCH.bundle (\$(git rev-list --count $BASE..$BRANCH) commits since base $BASE)\""
echo "== OUTCOME (host-written): $(cat "$H/OUTCOME" 2>/dev/null || echo 'none: the run ended without a named state')"
grep -qs '^PENDING=[0-9a-f]' "$H/round.state" && echo "WARNING the branch tip is an UNVERIFIED candidate ($(sed -n 's/^PENDING=//p' "$H/round.state")): its check never finished. Treat it as rejected"
[ -f "$H/rounds.tsv" ] && awk -F'\t' 'NR>1{n++; d[$3]++; c=$7; a=$8} END{printf "ROUNDS %d:", n; for(k in d) printf " %s=%d", k, d[k];
  printf "\nCOST %s USD-equivalent, %d accepted changes, cost per accepted change %s\n", c, a, (a>0 ? sprintf("%.2f", c/a) : "n/a")}' "$H/rounds.tsv"
RUN "git for-each-ref --format='%(refname:short)' refs/rejected | wc -l | sed 's/^/REJECTED attempts parked at refs\/rejected\/*: /'"
echo "== REVIEW BEFORE MERGING: changes to paths that run code or steer an agent on the owner's machine"
RUN "git diff --stat $BASE $BRANCH -- .claude .mcp.json '*CLAUDE.md' '*AGENTS.md' .github .gitattributes .gitmodules \
  '*package.json' '*package-lock.json' .npmrc .husky .envrc .vscode .idea Makefile tools scripts '*.sh' '*.py' | tail -40"
echo done
