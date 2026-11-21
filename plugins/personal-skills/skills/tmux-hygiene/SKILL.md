---
name: tmux-hygiene
description: Free login-node memory by listing old idle tmux sessions, describing each in one sentence, and killing the ones the user picks. Only sessions older than 48 hours with nothing active in them are offered. Use when the user asks to clean up tmux, kill old sessions or Claude processes, free memory on the login node, or when the SessionStart memory warning fires.
---

# tmux hygiene

Each Claude left open in tmux holds 0.3 to 0.6 GiB, and the total grows with session length. The login node caps every user's processes together (`/etc/systemd/system/user-.slice.d/50-real-login-limits.conf`):

| Level | Value | Effect |
|---|---|---|
| Soft limit (this skill) | 4 GiB non-cache | SessionStart hook warns; time to clean up |
| `MemoryHigh` | 6 GiB | kernel reclaims and throttles every process of the user |
| `MemoryMax` | 8 GiB | OOM killer ends a process |

The script measures non-cache memory: the user slice's `memory.current` minus file cache, which the kernel drops first. Set `TMUX_HYGIENE_SOFT_GIB` to change the soft limit.

## Steps

1. Run the report and read it in full:
   ```
   python3 -I "${CLAUDE_SKILL_DIR}/scripts/tmux_hygiene.py" report
   ```
   It sorts sessions oldest first and tags each one `ELIGIBLE`, `ACTIVE` or `too young`.

2. Show the user the memory line, then a numbered table of the `ELIGIBLE` sessions only: number, name, age, memory, and one sentence on what the session was for. Write the sentence from the Claude title and prompts, the pane's directory and its last lines. Under the table, give one line with the count of sessions left out and why (for example "3 skipped: 2 younger than 48 h, 1 running a command"). If no session is eligible, say so and stop.

3. Ask which to kill. Accept numbers, names, "all" or "none". Wait for the answer. Never kill without it.

4. Kill the chosen sessions by name:
   ```
   python3 -I "${CLAUDE_SKILL_DIR}/scripts/tmux_hygiene.py" kill NAME [NAME...]
   ```
   The script re-checks each session first and skips any that has become active since the report. Report what it killed, what it skipped and the memory before and after.

## What counts as active

A session is active if any of these hold:
- a Claude in it has a status other than `idle` in `~/.claude/sessions/<pid>.json` (busy, or waiting on a permission prompt);
- a Claude in it has a running shell command, foreground or background;
- a pane runs anything other than a shell or Claude (an editor, a script, `srun`, `watch`);
- a process outside Claude is in state R or D;
- the session uses more than 20% of a core over a 3-second sample (idle Claude uses 1 to 10%);
- it contains the Claude running this skill.

Do not lower `--min-age-hours` below 48 unless the user asks for it in this conversation. A session the user wants gone but the script will not offer can be killed by the user with `tmux kill-session -t NAME`.

## Warning hook

The plugin's SessionStart hook runs `tmux_hygiene.py check`. It prints a warning when non-cache memory exceeds the soft limit, and only on machines whose user slice has a `MemoryHigh` limit. When it fires, tell the user and offer this skill.
