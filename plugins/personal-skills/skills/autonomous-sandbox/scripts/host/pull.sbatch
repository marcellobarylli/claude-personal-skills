#!/bin/bash
#SBATCH -J sandbox-pull
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:30:00
# sbatch -p <partition> -o $SB/logs/pull-%j.log --export=ALL,SB=$SB $SB/host/pull.sbatch
set -u; : "${SB:?SB not set}"; source "$SB/ctl/sandbox.conf"
hostname
echo "internet from compute node (the host proxy needs it):"
curl -sS -o /dev/null -w "  anthropic %{http_code}\n" https://api.anthropic.com/ || echo "  anthropic UNREACHABLE"
curl -sS -o /dev/null -w "  github %{http_code}\n" https://github.com/ || echo "  github UNREACHABLE"
python3 -c 'import ssl, sys; print("  host python", sys.version.split()[0], ssl.OPENSSL_VERSION)'
export APPTAINER_CACHEDIR="$SB/image/cache"
apptainer pull --force "$SB/image/agent.sif" "$APPTAINER_IMAGE" && rm -rf "$SB/image/cache"
apptainer exec --containall "$SB/image/agent.sif" sh -c 'node -v; git --version; python3 --version'
