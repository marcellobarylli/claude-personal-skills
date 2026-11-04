---
name: codex-critique
description: Get an independent, adversarial critique of a proposed design or feature from Codex before implementing it. Use when the user asks for a Codex critique, second opinion, or adversarial check on a proposal, or after proposing a non-trivial design the user may want pressure-tested. Requires the codex plugin (openai/codex-plugin-cc).
---

# Codex critique

Pressure-test a proposal with Codex before any code is written. Review-only: nothing is implemented until the user has seen both critiques. The aim is to catch errors without growing the plan: the best plan is the smallest one that meets the goal correctly.

## Steps

1. **Write the proposal to a Markdown file** (scratchpad or `docs/`, e.g. `proposal-<topic>.md`). Start with **Goal:** one sentence, in the user's words, then **Decided with the owner:** the clarified ambiguities and their answers, one line each, from the interview (non-goals only if the owner stated any; empty is fine). Then cover: problem, proposed change, assumptions it depends on, risks, alternatives considered, out of scope, acceptance criteria. Codex needs concrete claims to attack.

2. **Delegate to Codex, read-only.** First, the goal gate: the proposal must state the goal and any clarified ambiguities. If an ambiguity that affects correctness or scope is still unresolved, ask the owner (AskUserQuestion) instead of dispatching; don't interview to fill empty fields. Then log a `critique-dispatched` event with the `round-log` skill: it saves the exact input Codex will read and its hash. Then run via Bash (add `run_in_background: true` for large proposals):

   ```bash
   node "$(ls -d ~/.claude/plugins/cache/openai-codex/codex/*/ | sort -V | tail -1)scripts/codex-companion.mjs" task --effort high "<prompt>"
   ```

   Always pass `--effort high` (use `xhigh` only if the user asks for maximum depth). Do NOT pass `--write`; `task` is read-only by default. Prompt template:

   > Read-only: do not edit, create or delete any files. Critique the plan in `<path>` against the code in this repo. Its goal: `<goal>`. The owner values simplicity: the best plan is the smallest one that meets the goal correctly.
   >
   > Report two kinds of finding:
   > 1. **Error** (uncapped): something that would make the plan fail or give a wrong result. That covers a required behavior the plan leaves out, a false claim about the code or data (check it and cite file:line), an internal contradiction, a step that does not serve the goal as written, or an unverified assumption the plan rests on. Report an omission only if the resulting behavior fails the goal, counting behavior that already works.
   > 2. **Cut** (uncapped, ranked by value): a step, component, check or output that can be removed while the goal is still met. A Cut needs only to show the removable complexity, not a failure.
   >
   > Simplicity limits the fixes, not the search: check every part of the plan, including its checks and acceptance criteria, and report every Error you find. Treat the owner's preferences and scope decisions in "Decided with the owner" as fixed, but still check any factual claim in them and any contradiction between them.
   >
   > For each finding give: type, severity, evidence, the concrete failure (what input leads to what wrong outcome; a Cut shows the removable complexity instead), and the smallest fix. Severity: critical = wrong result or goal not met; high = a stated acceptance criterion fails or cannot be verified; medium = works but depends on something fragile. A critical or high Error needs a failing input that the stated data or interface can actually produce; otherwise rate it medium or leave it out. Do not report anything weaker, and do not report nice-to-have additions.
   >
   > Report each plan step once: if removing a step resolves its error, report it as a Cut and put the failure in the evidence. The acceptance criteria and scope are the owner's: never propose deleting one; if one conflicts with the goal or the code, flag it as "Owner decision". End with the findings, with no summary or verdict.
   >
   > A fix, at every severity, removes, narrows or reuses existing content, and must not add a new file, component, flag, script or dependency. If the only correct fix would, report the finding and its failure and write "Owner decision: fix adds a component" instead of designing it. Mark each fix as making the plan larger (+), smaller (−) or neither (0).
   >
   > If the plan is sound, say so: no findings is a valid answer. Do not soften.

   Never include my own conclusion or recommendation in the prompt; it anchors Codex. State the goal and the proposal, not a verdict.

3. **Log a `critique-returned` event with `round-log` before anything else**: it saves the critique verbatim to the trail. Then **present the critique and your recommendations as one numbered list**, so the user reads each finding and your verdict together without scrolling. Do not also print the full critique in a `<details>` block or repeat the findings in a separate table. For each finding:

   ```markdown
   N. **Type · Severity: Codex's headline** (+/−/0)
      **Evidence:** … **Failure:** … **Smallest fix:** …   ← Codex's words, unedited
      → **Recommend: Accept / Defer / Reject.** One line why (a narrower fix, if you have one).
   ```

   Keep Codex's text faithful: don't summarize, merge or reword findings. You may shorten local file links to `file:line`. Show Errors first, then Cuts. Put anything outside the findings (Codex's overall verdict) after the list. End with one line pointing to the verbatim copy in the trail. Recommend by type:
   - **Error:** accept the Error, not necessarily the fix. If Codex's fix is +, look for a narrower fix first.
   - **Cut:** accept if the goal is still met.

   Run one critique per plan; a second round only if the user asks.

4. **Do not implement** until the user has seen the list and decided. Log their decisions as a `disposition` event with `round-log`: every finding keeps its row in the Second opinion table, rejected and deferred ones included.

## Plan mode

Mandatory once a plan is drafted, before calling ExitPlanMode.

1. Use the plan file as the proposal; don't write a separate one. Make sure it states the goal and the clarified ambiguities.
2. Run step 2 as above.
3. Show the combined findings and recommendations list as in step 3.
4. Stop and wait for the user to accept or reject each finding. Do not revise the plan or call ExitPlanMode before they reply.
5. Log the decisions as in step 4 (in plan mode `round-log` writes to the plan file's buffer). Revise the plan file with the accepted findings only, state the net change in one line (e.g. "+1 check, −2 steps"), then call ExitPlanMode with the revised plan.

## Notes

- Recording follows the `round-log` skill: the table goes in the design record, the input and the verbatim critique in the trail.
- For a branch that already has code, prefer `/codex:adversarial-review --base <ref> <focus>` instead (user-invoked slash command).
- If `codex-companion.mjs` is missing or Codex isn't logged in, tell the user to run `/codex:setup`.
- Check progress of background runs with `status <job-id>` / `result <job-id>` on the same script.
- If the user's CLAUDE.md says documents are Markdown, keep the proposal in Markdown; follow whatever output format rule applies.
