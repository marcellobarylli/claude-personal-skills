---
name: audit-and-cleanup
description: Audit the home directory on the real cluster against the storage layout in ~/.claude/CLAUDE.md, report every deviation, propose where each item belongs, and show what a move would break (scripts, sbatch files, environments, running jobs, tmux sessions, worktrees, symlink shims). Use when the user asks to audit, tidy, clean up or reorganise ~, ~/workspace or ~/data, or asks where something belongs. Reports first; moves nothing without approval.
---

# Audit and cleanup

The layout and the best-use rules in `~/.claude/CLAUDE.md` are the standard. Re-read its "Storage layout" section
before classifying, because it may have changed since this skill was written. `~/data/README.md` records earlier moves.

The skill has three phases. Phases 1 and 2 are read-only. Phase 3 runs only on items the user approves.

## Phase 1: scan

The audit folder is `~/data/home-audit/<YYYY-MM-DD>/`. Logs go to `~/data/home-audit/logs/`.

```bash
OUT=$HOME/data/home-audit/$(date +%F); mkdir -p "$OUT" $HOME/data/home-audit/logs
python3 "${CLAUDE_SKILL_DIR}"/scripts/scan.py live --out "$OUT"     # login node, about 1 s
sbatch --parsable --output=$HOME/data/home-audit/logs/%x-%j.log --export=ALL,OUT=$OUT,SKILL_DIR="${CLAUDE_SKILL_DIR}" \
  "${CLAUDE_SKILL_DIR}"/scripts/deep.sbatch                          # sizes and references
```

The live part must run on the login node: tmux panes and process working directories are not visible from a compute
node. The deep part walks every file under `~/workspace`, `~/data` and `~/sandboxes`, so it runs as a job. Report the
job ID, then wait with `squeue --me` / `sacct -j <id>`. To recheck one item later, pass `--candidate /abs/path`
after the script name.

`live.json` holds the layout, git state of each workspace entry (linked worktree or not, worktree list, uncommitted
and unpushed changes, untracked and ignored top-level paths), tmux panes, process cwds, Slurm jobs and the crontab.
`deep.json` holds the size of each candidate, the Python and conda environments inside it, and up to 200 files that
reference it. A reference with `"inside": true` lives inside the candidate itself.

## Phase 2: classify and report

Check each item against these rules. The rule names are the deviation labels used in the report.

| Label | Rule | Usual destination |
|---|---|---|
| `top-of-home` | Anything at the top of `~` other than `workspace`, `data`, `sandboxes`, `bin` and dotfiles | `~/data/<project>/...` or `~/workspace/<project>/` |
| `shim` | A symlink in `~` listed in `~/data/README.md`. Allowed, but report whether anything still uses the old path | Remove once nothing references it |
| `broken-link` | A symlink whose target is gone | Remove (ask) |
| `sibling-checkout` | A folder in `~/workspace` that is a linked worktree or a second clone of another project (`<project>-r024`) | `~/workspace/<project>/.worktrees/<name>/` |
| `worktree-outside` | A registered worktree whose path is not under `<repo>/.worktrees/` | same as above |
| `gitignore` | A repo without `.worktrees/` in `.gitignore` | add the line |
| `loose-file` | A file at the top of `~/workspace` or `~/data` other than `~/data/README.md` | its project's folder |
| `data-in-repo` | Large untracked or ignored output in a repo (`runs/`, `logs/`, `outputs/`, `wandb/`, checkpoints, datasets). `.venv/` is fine | `~/data/<project>/<round-or-run>/` |
| `orphan-data` | A folder in `~/data` with no matching `~/workspace/<project>` (lower-case match) | ask the user which project it belongs to |
| `name-case` | A `~/data` folder whose name is not the lower-case workspace name | rename |
| `slurm-log` | Slurm logs outside `~/data/<project>/logs/` | there |
| `stale-backup` | Backup copies such as `.bashrc.bak-*`, `.claude.json.bak` | remove (ask) |
| `closed-worktree` | A worktree whose branch is merged or pushed and has no uncommitted work, no tmux pane and no job | `git worktree remove` |
| `quota` | `du` of `~` near 300, 400 or 500 GB | name the largest folders |

Infer where an item belongs from, in order: the project named in its path or contents (a README, `pyproject.toml`,
a sbatch `--job-name`, a round number such as `r024`), the files that reference it, the tmux session whose cwd is in
it, and the job whose WorkDir or StdOut is in it. State the evidence for each proposal. When the evidence is weak,
say so and ask.

For every proposed move, report the impact:

- **References.** List each file from `deep.json` with its line. Sort them into: scripts and sbatch files to update,
  docs and round logs (historical, usually left alone and covered by a shim), and Claude memory or skills.
- **Environments.** A venv or conda env hardcodes its prefix in `pyvenv.cfg`, `conda-meta` and every `bin/` shebang. It
  breaks when moved. Options: rebuild it at the new path (in a job), or move it and keep a symlink shim.
- **Live use.** A running or pending job with WorkDir, StdOut or Command inside the item blocks the move until the
  job ends. A tmux pane or process with its cwd inside it keeps the old inode; the user should close or `cd` it first.
- **Git.** A linked worktree moves only with `git worktree move` (a plain `mv` breaks the `.git` link). A sibling clone
  with unpushed commits or uncommitted changes must not be removed.
- **Cost.** `mv` within `/home` is a rename and is instant. A copy across filesystems (to `/scratch` or ITU HPC) is
  heavy and runs in a job.

Write the report to `$OUT/report.md` and summarise it in chat. Structure:

1. Summary: number of deviations per label, total size of misplaced data, home usage against the 300/400/500 GB marks.
2. One section per proposed action, safest first: item, label, size, proposed destination with evidence, impact
   (references, environments, live use, git), and the exact commands. Mark each action `safe`, `needs-update`
   (references to edit) or `blocked` (live job, unpushed work, env rebuild).
3. Open questions for items whose destination is unclear.

Then ask the user which actions to apply. Do not apply any in the same turn as the report.

## Phase 3: apply approved actions

- Apply only the actions the user approved, one at a time, and stop at the first error.
- Re-run the live scan first. Skip any action that a new job, tmux pane or process now blocks, and say so.
- Use `git worktree move` for worktrees, `git worktree remove` for closed ones, plain `mv` within `/home` for the rest.
- After a move, update the scripts and sbatch files listed as `needs-update`. Show the diff. Do not commit in a
  project repo unless the user asks.
- Leave a symlink shim at the old path when docs, round logs or an environment still use it. Add a row to the table in
  `~/data/README.md` for every move ("Moved on <date>" section).
- Ask before deleting anything, and always before deleting under `~/data` or `~/sandboxes`. Removing a shim, a broken
  link or a stale backup is a delete.
- Rebuilding an environment, or copying data off `/home`, runs as an sbatch job with a tight `--time`.
- Finish by re-running both scans and reporting what is left.
