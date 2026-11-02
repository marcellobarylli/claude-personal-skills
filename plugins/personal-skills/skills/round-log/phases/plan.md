# Plan phase: interview, drafts, critiques, dispositions

Outside plan mode, write straight to `docs/rounds/NNN/trail/`. In plan mode, write the same content into the buffer
at the end of the plan file:

```
## Round log (pending)

Round NNN. Moved into docs/rounds/NNN/trail/ after ExitPlanMode.

### Journal
| # | Occurred | Recorded | Event | Actor | What | Record |
|---|---|---|---|---|---|---|

### Interview

### Captures
```

Everything above the `## Round log (pending)` heading is the plan; the buffer is not part of it.

## Interview

At each answer, add an `answer` row and append to `interview.md` (or the buffer's Interview section):

```
### Q<n> (<occurred>): <question as asked>
- **Options offered:** <each option, with the recommended one marked>
- **Answer:** <verbatim, including any notes>
```

A changed answer is a new entry that names the one it replaces. When the draft is written, add a `plan-drafted` row.

## Before a critique is sent

1. Decide K (the next critique number) and the exact input Codex will read.
2. Save that input unchanged:
   - Outside plan mode: copy the proposal to `trail/plan-vK.md`.
   - In plan mode: append `<details><summary>plan-vK as sent</summary>` with the plan (everything above the buffer)
     under Captures.
3. Hash it and note the repository state:
   ```bash
   date -u +%Y-%m-%dT%H:%M:%SZ
   shasum -a 256 <trail>/plan-vK.md            # plan mode: sed '/^## Round log (pending)/,$d' <plan> | shasum -a 256
   git rev-parse --short HEAD && git status --short
   ```
4. Add a `critique-dispatched` row with the hash and HEAD. In plan mode, tell Codex to ignore the
   `## Round log (pending)` section.

## When a critique returns

Before showing or discussing it, save it verbatim to `trail/critique-K.md` (plan mode: a `<details>` block under
Captures):

```
# Codex critique K: <topic>

- **Dispatched:** <UTC>
- **Returned:** <UTC>
- **Model:** <companion version, command, effort, read-only; thread id if printed>
- **Prompt:** <verbatim, or "the codex-critique template" plus whatever was added>
- **Reviewed input:** `plan-vK.md`, sha256 <hash>, HEAD <short>, working tree <clean | changed paths>
- **Findings:** <number of numbered findings; Optional items are not counted>

## Raw output (verbatim)

<the output, in a text fence>
```

Add a `critique-returned` row. A job id is a reference only; the companion keeps just its last 50 jobs.

## Dispositions

Add a `disposition` row when the owner decides, quoting any override. The decisions go into the Second opinion
table, which becomes a pre-run section of `architecture.md` (plan mode: drafted in the plan):

```
## Second opinion (pre-run)

Critiqued draft: `trail/plan-vK.md`, sha256 <first 8>…; Codex, effort <e>; raw text in `trail/critique-K.md`.

| # | Type | Finding | +/−/0 | My recommendation | Owner disposition | Where it landed |
|---|---|---|---|---|---|---|
| K.1 | Error | … | 0 | Accept: … | **Accepted** | Decision 3 |
```

Every numbered finding gets a row `K.n`, including rejected and deferred ones, each with its reason. Codex's Optional
items go under **Deferred** as one line each. Then revise the plan with the accepted findings, state the net change
in one line, and add a `plan-revised` row. A further critique repeats from "Before a critique is sent" with K+1.
