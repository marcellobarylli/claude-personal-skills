# Failure modes and their handling

Evidence comes from the ParaLLang run (jobs 3802 and 3808, 2026-11-05/06: 24h, 36 iterations) and from the
harness smoke tests of this skill (jobs 3853–3855). Each entry gives what happened, then what the scripts or the
procedure now do about it.

## Setup

| # | Failure | Evidence | Handling |
|---|---|---|---|
| S1 | Docker unusable | `permission denied ... docker.sock`; the user isn't in the docker group | Use Apptainer, which is rootless. Check `id` and `docker info` first |
| S2 | Compute nodes have no internet | Unknown until tested | `pull.sbatch` curls Anthropic and GitHub from the compute node before anything else |
| S3 | Apptainer refuses `--env HOME=` | `Overriding HOME environment variable ... is not permitted` | `--home $SB/home:/home/agent` sets HOME; don't also pass the env var |
| S4 | GitHub renames the mirror | `remote: This repository moved ... parallang-sandbox.git` (lowercase) | Obsolete: there is no mirror repo any more. The work leaves as a bundle (see Security) |
| S5 | Token pasted into the chat | The owner pasted the OAuth token as a message | The owner writes the token file with a `! echo ... > file` command. If the token was pasted anyway, list it first in the revocation step |
| S6 | The project's own LLM CLI can't sign in from the agent's shell | Preflight on 2026-11-06 measured `nested_rc=1`. Claude Code strips `CLAUDE_CODE_OAUTH_TOKEN` from the Bash tool's environment. The game's `claude-cli` preflight then saw `loggedIn: false`. The agent rightly refused to read it from `/proc/$PPID/environ` | The token is now a placeholder that the proxy swaps, so the project may set `CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-sandbox-placeholder` itself. Preflight's nested-call line checks it. Other providers stay unavailable unless the owner adds an injection rule to the proxy before launch |
| S8 | Unix socket path too long | `OSError: AF_UNIX path too long` with a scratch path of about 110 bytes | The proxy `chdir`s and binds a relative name. Inside the container the path is `/sock/proxy.sock` |
| S9 | curl ignores `-x` with `--unix-socket` | A test hung: curl spoke TLS straight to the socket | Test the proxy with a small CONNECT client, or from inside the container through the relay |
| S7 | `auth status` misreports env-token sign-in | `claude auth status` reports not signed in even though `claude -p` works | Project checks that rely on `auth status` need an env-token path, with a test. Say so in the loop prompt |

## Running

| # | Failure | Evidence | Handling |
|---|---|---|---|
| R1 | **False rate-limit back-off** | Iteration 1 ended `rc=0`, but the driver backed off 30 min. Ordinary failed tool results inside the stream contain `"is_error":true` and words like "limit" | Judge an iteration by its **last line** only (`"type":"result"`). Key order varies, so don't anchor on `^{"type"`. Fixed mid-run with a `mv` and a restart during the idle back-off |
| R2 | **Agent idles on long timers** | With Codex at its limit, the inner agent ran `sleep 3568` and said it was "waiting on the background timer". `claude -p` stays alive for its background tasks, so about an hour was lost | The inner rules forbid long timers and say to do offline work instead and queue the live runs. The driver's stall watchdog kills an iteration whose log hasn't grown for `STALL_SECONDS` |
| R3 | **Provider quota exhausted** | Codex hit its limit after about 100 game calls and 2 critiques in about 50 min. Later it was locked "until 2026-11-09", past the end of the run | The loop prompt names the fallback: a Claude subagent as critic, and offline backlog items. Live runs are queued in STATE.md. Live data is paced: single-location runs before tours |
| R4 | Real usage or rate limit on the loop's own model | Not hit in 24h. It's possible on long runs | Back off `BACKOFF_SECONDS`, matching only the final line and the stderr tail |
| R5 | **Supervisor blocked from handing credentials over** | The auto-mode classifier denied writing the token to a file for the agent ("Credential Materialization") | Don't work around it. Credentials never enter the container; a provider the proxy doesn't inject for is unavailable. Tell the agent so |
| R6 | **Owner asked mid-run** | The supervisor offered options. Owner: "I don't choose anything ... no input from me until the deadline" | During a run the supervisor decides, applies the decision through `LOOP_PROMPT.md` and reports it |
| R7 | **Last iteration cut off mid-task** | The tail iteration got 840 s, hit `timeout` (rc=124) and left round 112 open as a `wip:` commit | The driver states each iteration's time budget in the prompt and won't start one with less than `MIN_ITER_SECONDS` left. `rc=124` isn't counted as a failure. `finaltest.sbatch` checks the end state |
| R8 | **Spin on quick iterations** | Smoke test: 10 iterations of about 5 s each in 100 s. In a real run that would be an empty backlog or a broken prompt burning quota | Spin guard: a successful iteration shorter than `QUICK_SECONDS` gets a growing sleep, and `MAX_QUICK` of them in a row writes `STOP` |
| R9 | Push to a wrong remote | Never happened. The test sandbox's origin was a local path | No remote and no push credential. The proxy refuses `git-receive-pack`. Preflight checks that there are no remotes and that a push fails |
| R10 | Stray servers or background jobs after an iteration | Possible with live runs | The iteration runs in its own process group (`setsid`), and the driver kills the group after each iteration. The inner rules say to stop servers |
| R11 | Job time limit (24h partition) | `--time=23:55:00` | `--signal=B:USR1@900`. The wrapper sends TERM to the container, the driver kills the iteration, makes a local safety commit and exits. Runs longer than 24h chain jobs with `afterany`, and `DEADLINE` survives the chain |
| R12 | Repeated hard failures | Not hit | `MAX_CONSECUTIVE_FAILURES` writes `STOP`, with a linear back-off before that |
| R13 | A log check broken by a later round | Round 026 deleted a fixture that round 012's journal linked to | The agent recorded it in STATE.md. Run every log check in `finaltest.sbatch`'s `EXTRA_CHECK_CMD`, not only the latest round's |

## Supervision

| # | Failure | Evidence | Handling |
|---|---|---|---|
| M1 | Monitor expires every 30 min | Each `Monitor` call ends at 30 min | Re-arm on every expiry. Include how recently the iteration log was written, so a silent stall is visible |
| M2 | Editing a running `driver.sh` | Bash reads scripts as it goes | Write `driver.sh.new`, run `bash -n` on it, then `mv` it over. Restart only while the driver is idle |
| M3 | Supervisor session not in tmux | The SessionStart hook warned after a resume | The run doesn't depend on the supervisor. Tell the owner, and suggest tmux |
| M4 | Supervisor going beyond read-only | The driver fix needed an edit and a job restart | Allowed for harness fixes only. Record each one and tell the owner |

## Security (review of 2026-11-06)

A security review of the first version found that the agent could affect the outside world. Each finding and what
the scripts now enforce:

| # | Finding | Handling (enforced, not prompt-level) |
|---|---|---|
| X1 | **Host code execution.** `$SB/run` was bound read-write; it held `sandbox.conf`, which the host sources, and `job.sbatch`, which it resubmits. One appended line ran as the owner outside the container | Control files live in `$SB/ctl`, bound read-only. Host scripts live in `$SB/host`, never bound. The host only tests `state/STOP` for existence |
| X2 | **Write channel to GitHub.** A write deploy key to a mirror allowed force-push, branch deletion and `.github/workflows` that run on GitHub's runners | No key, no remote, no push. `finaltest.sbatch` writes a bundle; the owner fetches it. The proxy refuses `git-receive-pack` |
| X3 | **Credentials readable and sendable.** The OAuth token was in the environment (`/proc/<pid>/environ`), Codex auth and the deploy key were plain files, and egress was open. The first run's agent probed `/proc/$PPID/environ` for variable names | The token lives only in the host proxy; the container gets a placeholder. No Codex login, no key. Preflight searches every container-visible path for the real token |
| X4 | **Open egress.** POST anywhere, webhooks, cluster-internal services | `--net --network none` (loopback only; verified rootless on 2026-11-06). The only way out is the proxy: reads to public hosts, writes only for inference and git fetch, no private addresses |
| X5 | **Host git runs agent config.** `git log` on the host reads the agent's `.git/config` (`core.fsmonitor`, pager, diff drivers) | `inspect.sh` runs git in a fresh, offline container with the work tree read-only. The owner fetches from a bundle, which runs no repo config |
| X6 | **Endless job chain.** The agent could write a far-future `DEADLINE` | `DEADLINE` is in `ctl` (read-only); `JOBS` counts jobs in `host`, capped by `MAX_JOBS` |
| X7 | **Self-modified config.** Hooks or MCP servers added to `~/.claude` load next iteration | Managed settings and an empty `managed-mcp.json`, bound read-only at `/etc/claude-code`; the driver stops the run if an iteration's init line lists MCP servers. The network policy blocks remote MCP regardless |
| X8 | **Merge-back imports code that runs later** (hooks, `.mcp.json`, CLAUDE.md, package scripts, CI workflows, project tools) | `finaltest.sbatch` lists changes to those paths; the owner reviews them before merging or running anything |

| X9 | **CLI patchable.** The Claude CLI lived in the writable sandbox home, so the agent could patch it to ignore the managed settings | The CLI is installed into `$SB/cli`, mounted read-only at `/opt/claude`; the driver calls it by absolute path. Preflight checks both |
| X10 | **Shared disk unbounded.** The work tree is on the shared NFS volume; only a prompt rule limited it | Host-side watchdog in `job.sbatch`: over `DISK_LIMIT_GB` it kills the container with KILL (TERM would make the safety commit copy the files into `.git`) and writes `ctl/STOP` |

Residual, accepted: data can leave inside the URL of a GET; the agent spends the owner's inference quota; disk can
overshoot by one check interval; agent-forgeable `logs/`; GET requests that a badly designed site treats as actions.

## Loop design (paper review of 2026-11-06)

The loop-engineering position paper (a corpus study of 50 loops, plus the literature on self-correction, reward
hacking and model-as-judge) was reviewed with the owner. The first version ran on a clock: its only stop was the
deadline, it told the agent "don't end with nothing done", and the agent graded its own work. Each risk below is
argued from the paper's cited literature, not measured in a run of this skill. That run is still to come.

| # | Risk | Source | Handling (enforced unless marked) |
|---|---|---|---|
| L1 | **Self-approval.** The maker writes the code, the tests and the verdict, so the score drifts up while quality doesn't | Reward hacking when generator and judge share context [paper ref 27] | The host runs the check in separate containers and alone decides keep, revert and SUCCESS. The maker's words can end a run only as NO-OP or BLOCKED |
| L2 | **Gaming the check.** The maker edits the eval, reads the hold-out, or hard-codes outputs | Specification gaming [6] | The criterion and thresholds live in `ctl/` (read-only); the hold-out and scorer in `$SB/eval`, never mounted for the maker. With `SCORE_CMD`, the agent's code never runs next to the labels. Residual, accepted: without `SCORE_CMD` it does, and preflight says so |
| L3 | **Forged counters.** Streak, stall count, best metric or accepted commit rewritten by the agent | `/state` and `/logs` are agent-writable | All loop state is in `$SB/host` (never mounted): `round.state`, `rounds.tsv`, `OUTCOME` |
| L4 | **Judge steered by the maker.** Prompt injection via the repo's CLAUDE.md, planted rules in the home, notes addressed to the grader, or a judge with write access | Model-as-judge fragility [12] | The judge gets a fresh empty home and starts outside the repo, with the snapshot read-only, `docs/autonomy` masked and no web tools. Residual, accepted: same model as the maker (owner decision 2026-11-06), and code comments can still try to persuade it. The judge prompt treats them as red flags. Report as level 4 |
| L5 | **Running past "done", or "done" from one lucky pass** | Stop on a frozen yardstick with a streak, not an invented count (Family A) | SUCCESS needs the criterion on a kept commit and on `SUCCESS_STREAK` consecutive checks (`CHECK_SEED` 1..n) |
| L6 | **Unattended runaway.** No stop except the clock; "don't end with nothing done" invents work | Anti-pattern "unattended runaway" | Named end states, with a STALLED detector (`STALL_ROUNDS` rounds without improvement) and a clean NO-OP. `RUN_HOURS` stays the hard maximum. This supersedes the quick-iteration spin guard (R8): barren rounds count towards STALLED |
| L7 | **Many changes per check.** The verdict can't say which change helped or hurt; one bad change sinks good ones | One change per turn, keep only if nothing regressed (Family B) | One round = one change = one session. A failing round is reverted in full and parked at `refs/rejected/round-N`. The host's verdict is committed to `docs/autonomy/rounds.md` so the next fresh context learns from it |
| L8 | **Volume mistaken for progress** | Cost per accepted change | `rounds.tsv` records the cost (CLI `total_cost_usd`, maker plus judge, API-equivalent) and the accepted count. finaltest and the report lead with cost per accepted change, not commits |
| L9 | **Round cut off by the job's time limit** | R7 | Never kept unverified. A cut-off maker session is parked and reverted; a cut-off check stays pending and the next job re-checks it (see G2). An owner STOP waits for the open round's verdict |
| G1 | **Full training inside the maker's session.** Hours exceed the Bash tool's timeout, invite polling and long waits (R2), trip the stall watchdog, and let the maker report a result it chose | Owner decision 2026-11-06 | The host trains, in the checker, with the frozen `TRAIN_CMD` and the `TRAIN_SECONDS` cap. The maker only smoke-tests (inner rules) and reads the training log next round |
| G2 | **Training cut off by the 24h job limit** wastes the whole run, and a re-check would repeat it | Slurm `main` is limited to 1 day | The host plans to the job's end (from `squeue %e`) and the step caps. It yields before a training that can't fit, keeps a cut-off candidate pending, and resumes streaks at the next check. Preflight fails if one round doesn't fit a job. Not handled: a single training longer than about 20 h (no checkpoint resume across jobs) |
| G3 | **GPUs invisible in the container** | `--cleanenv` drops `CUDA_VISIBLE_DEVICES` | `--nv` plus `APPTAINERENV_CUDA_VISIBLE_DEVICES`. `--env` would split the comma list. Preflight checks with `nvidia-smi -L` |
| G4 | **Noisy training passes once by luck** | Family A: a streak, not one pass | `STREAK_RETRAIN=1` retrains from scratch with a new `CHECK_SEED` for each streak check. It's costly, and the cost is stated in Phase 1 |

