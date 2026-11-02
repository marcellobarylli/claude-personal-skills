---
name: codex-critique
description: Get an independent, adversarial critique of a proposed design or feature from Codex before implementing it. Use when the user asks for a Codex critique, second opinion, or adversarial check on a proposal, or after proposing a non-trivial design the user may want pressure-tested. Requires the codex plugin (openai/codex-plugin-cc).
---

# Codex critique

Pressure-test a proposal with Codex before any code is written. Review-only: nothing is implemented until the user has seen both critiques. The aim is to catch errors without growing the plan: the best plan is the smallest one that meets the goal correctly.

## Steps

1. **Write the proposal to a Markdown file** (scratchpad or `docs/`, e.g. `proposal-<topic>.md`). Start with **Goal:** one sentence, in the user's words. Then cover: problem, proposed change, assumptions it depends on, risks, alternatives considered, out of scope, acceptance criteria. Codex needs concrete claims to attack.

2. **Delegate to Codex, read-only.** First log a `critique-dispatched` event with the `round-log` skill: it saves the exact input Codex will read and its hash. Then run via Bash (add `run_in_background: true` for large proposals):

   ```bash
   node "$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/ | sort -V | tail -1)scripts/codex-companion.mjs" task --effort high "<prompt>"
   ```

   Always pass `--effort high` (use `xhigh` only if the user asks for maximum depth). Do NOT pass `--write`; `task` is read-only by default. Prompt template:

   > Read-only: do not edit, create or delete any files. Critique the plan in `<path>` against the code in this repo. Its goal: `<goal>`. The owner values simplicity: the best plan is the smallest one that meets the goal correctly.
   >
   > Report three kinds of finding:
   > 1. **Error:** something that would make the plan fail or give a wrong result. That covers a false claim about the code or data (check it and cite file:line), an internal contradiction, a step that does not serve the goal as written, or an unverified assumption the plan rests on.
   > 2. **Gap:** something the goal needs that the plan lacks.
   > 3. **Cut:** a step, component, check or output the goal does not need.
   >
   > Simplicity limits the fixes, not the search: check every part of the plan, including its checks and acceptance criteria, and report every Error you find.
   >
   > For each finding give: type, severity (critical/high/medium), evidence, the concrete failure (what input leads to what wrong outcome), and the smallest fix. Prefer fixes that remove, narrow or reuse existing code over fixes that add. Mark each fix as making the plan larger (+), smaller (−) or neither (0).
   >
   > Leave out hardening, extra controls, extra reporting and style unless leaving them out causes a concrete failure. If you still want to suggest any, list at most three, one line each, under "Optional" at the end. If the plan is sound, say so: no findings is a valid answer. Do not soften.

   Never include my own conclusion or recommendation in the prompt; it anchors Codex. State the goal and the proposal, not a verdict.

3. **Log a `critique-returned` event with `round-log` before anything else**: it saves the critique verbatim to the trail. Then **return Codex's critique faithfully**, unedited in a `<details>` block, then a numbered table: `# | type | finding | +/−/0 | my recommendation (one line why)`. Recommend by type:
   - **Error:** accept. If Codex's fix is +, look for a narrower fix first.
   - **Gap:** accept only if the goal needs it; otherwise defer.
   - **Cut:** accept if the goal is still met.
   - **Optional:** defer by default, one line under Deferred.

4. **Do not implement** until the user has seen both and decided. Log their decisions as a `disposition` event with `round-log`: every finding keeps its row in the Second opinion table, rejected and deferred ones included.

## Plan mode

Mandatory once a plan is drafted, before calling ExitPlanMode.

1. Use the plan file as the proposal; don't write a separate one. Make sure it states the goal.
2. Run step 2 as above.
3. Show Codex's critique and the table as in step 3.
4. Stop and wait for the user to accept or reject each finding. Do not revise the plan or call ExitPlanMode before they reply.
5. Log the decisions as in step 4 (in plan mode `round-log` writes to the plan file's buffer). Revise the plan file with the accepted findings only, state the net change in one line (e.g. "+1 check, −2 steps"), then call ExitPlanMode with the revised plan.

## Notes

- Recording follows the `round-log` skill: the table goes in the design record, the input and the verbatim critique in the trail.
- For a branch that already has code, prefer `/codex:adversarial-review --base <ref> <focus>` instead (user-invoked slash command).
- If `codex-companion.mjs` is missing or Codex isn't logged in, tell the user to run `/codex:setup`.
- Check progress of background runs with `status <job-id>` / `result <job-id>` on the same script.
- If the user's CLAUDE.md says documents are Markdown, keep the proposal in Markdown; follow whatever output format rule applies.
