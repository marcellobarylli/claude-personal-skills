# Build: implementation, runs, results, amendments, reviews

Add a row when each of these happens.

- **`built`:** a milestone commit. What: the commit subject. Record: the artifact directory. The artifact holds the
  builder, tests, `handoff.md` and `receipt.json`, as the project's logging table says.
- **`run`:** a job submitted or finished. What: job id, cluster, then `GPU <model>, node <node>, driver <version>`, or
  `CPU` for a CPU job. Record: the receipt once it exists. If the run creates, changes or first uses an environment,
  update the environment registry in the same commit.
- **`result`:** an intermediate result worth keeping (a count, a table, a snapshot). Record: its path. A result that
  will be replaced later still gets its row now.
- **`amended`:** a design change. Add a dated section to `architecture.md`:
  `## Amendment <YYYY-MM-DD>: <topic> (owner, <before or after> <what>)`. Say what it changes and why, and quote the
  owner's approval. Never edit a `(pre-run)` section.
- **`review-dispatched` / `review-returned`:** a post-build Codex review. Use the capture steps of
  [plan.md](plan.md) with `trail/review-K.md`, numbering findings `RK.n`. Its disposition table goes into the
  Amendment that records the resulting changes.

Add a dated `## Status <YYYY-MM-DD>: <state>` section to `architecture.md` only when the round stops in a state the
next agent must know about (built but not scored, blocked on compute).
