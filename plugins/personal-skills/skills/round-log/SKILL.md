---
name: round-log
description: Record a research round's events as they happen, split into a main stream (what the next agent reads) and a trail (interview, drafts, raw critiques, timeline). Use at each round event - an interview answer, a plan draft, a Codex critique being sent or returned, an owner disposition, ExitPlanMode, the freeze commit, a build milestone, a run, an amendment, an intermediate result, the outcome, the close - and whenever codex-critique or the project's log protocol says to log one.
---

# Round log

**Goal:** record everything in the order and at the time it is created, while the next agent reads only the main
stream.

## Where things go

Find the project's logging table through its AGENTS.md (assembly repo: AGENTS.md → `W1-STATUS-REPORT.md`, "How the
project is logged"). It names the round folder, the findings location and the check command. Without a table, use
the defaults below and tell the user.

```
docs/rounds/NNN/
├── architecture.md     MAIN: decisions, design, Second opinion table, amendments, status, outcome
├── findings.md         MAIN: Question, Finding, Method, Results, Decision, Evidence, Claim boundary, Open items
└── trail/              SIDE: for tracing back only
    ├── journal.md      append-only timeline, one row per event
    ├── interview.md    questions, options offered, answers verbatim
    ├── plan-vK.md      each draft exactly as Codex saw it
    ├── critique-K.md   Codex output verbatim, with a provenance header
    └── review-K.md     post-build Codex review, if any
```

Work that is not a round (a standalone proposal): the trail is `<proposal-basename>-trail/` next to the proposal, and
the proposal itself holds the Second opinion table.

## Rules

1. **Record when created.** Each event gets its journal row when it happens, not at a phase boundary. Phase
   boundaries only move records.
2. **Append only.** Never rewrite a journal row or a trail file; a correction is a new row. Never edit a section
   marked `(pre-run)` after its commit; a change is a dated Amendment. Never overwrite an existing trail file.
3. **Times and identities.** `Occurred` and `Recorded` are UTC, from `date -u +%H:%M:%S` or file timestamps
   (`TZ=UTC stat -f '%SB' -t '%H:%M:%S'` on macOS). Write "unknown" when neither exists; never reconstruct. The same
   goes for model and effort.
4. **Plan mode.** Only the plan file may be edited, so records go into its `## Round log (pending)` buffer. After
   ExitPlanMode, move the buffer into the round folder before doing anything else.
5. **Summary rule.** Every trail item except `journal.md` leaves a short trace in the main stream, with a link. A main
   record never defers to the trail for anything needed to implement.
6. **Reading rule.** When starting work, read the main stream only: the status report's current state, the round's
   `architecture.md`, its `findings.md`, the `handoff.md` of artifacts used. Open `trail/` only to trace a decision
   back (a disputed decision, a provenance audit, backfilling, a main record that is wrong or contradicts itself).

## Journal

```
# Journal: round NNN

Append only. Times are UTC. Occurred is when the event happened; Recorded is when the row was written.

| # | Occurred | Recorded | Event | Actor | What | Record |
|---|---|---|---|---|---|---|
```

- **Order** is the row number. A date goes in front of the time when it differs from the previous row's.
- **Actor:** `Owner`, `Claude (<model>)`, `Codex, effort <e>`, or a cluster job.
- **Record:** backticked paths relative to the journal, or `—`. No commit hashes: `git log -- <path>` gives them.
- **Events:** `round-opened`, `answer`, `plan-drafted`, `critique-dispatched`, `critique-returned`, `disposition`,
  `plan-revised`, `freeze`, `built`, `run`, `result`, `amended`, `review-dispatched`, `review-returned`, `outcome`,
  `closed`.

## Phases

Load only the file for the current phase.

| Events | Phase file |
|---|---|
| `round-opened` to `plan-revised` (plan mode or not) | [phases/plan.md](phases/plan.md) |
| moving the buffer after ExitPlanMode, `freeze` | [phases/freeze.md](phases/freeze.md) |
| `built`, `run`, `result`, `amended`, `review-*` | [phases/build.md](phases/build.md) |
| `outcome`, `closed` | [phases/close.md](phases/close.md) |
