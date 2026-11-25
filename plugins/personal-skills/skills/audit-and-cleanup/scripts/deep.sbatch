#!/bin/bash
#SBATCH --job-name=home-audit-deep
#SBATCH --partition=main
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:30:00
# Submit from the login node after the live scan:
#   sbatch --output=$HOME/data/home-audit/logs/%x-%j.log --export=ALL,OUT=$OUT,SKILL_DIR=<skill dir> <skill dir>/scripts/deep.sbatch
# Extra args (e.g. --candidate /abs/path) can follow the script name.
set -euo pipefail
: "${OUT:?set OUT to the audit folder that holds live.json}"
: "${SKILL_DIR:?set SKILL_DIR to the skill folder}"
python3 "$SKILL_DIR/scripts/scan.py" deep --out "$OUT" "$@"
