# Results: iteration 1

One run of three cases, with and without the first draft of the skill. The test definitions are in `../` and are
what you re-run; these are a snapshot. The run outputs (repos, diffs, replies) are not kept.

| File | What |
| --- | --- |
| `benchmark.json` / `.md` | the aggregate, plus analyst notes |
| `per-run-grades.json` | every assertion per run with its evidence, tokens, seconds and source diffstat |

## The honest reading

100% with the skill, 77% without, but **behavior was preserved in all six runs**: every hidden test passes either
way. The six assertions the baseline failed are about process and reporting: cuts not committed separately, pins not
committed, test command not named, two findings without evidence, the env override never offered for removal.

**The baseline removed more code**: 79% vs 56% of the export feature, 70% vs 57% of pricing. The draft said "delete;
do not rewrite", and the skill run left three one-method classes standing for that reason. This led to the collapse
rule in iteration 2.

Both cutting prompts say "apply the safe cuts, list the rest", which hands the baseline the skill's main idea.
Iteration 2 adds a case without that hint.

## Two grader bugs, fixed before scoring

1. A hidden test required `export_tasks(tasks, "yaml")` to raise `ValueError`. The CLI cannot produce that input
   (argparse rejects it), and both runs changed it. The test was removed and the skill now defines "reachable".
2. An assertion required the quote cache to be gone. Both runs found that it carries load: an unhashable `sku` gets
   `bad request` only because the cache key cannot be hashed. The assertion now names the rounding policies instead,
   and the skill tells the survey to check side effects.

## What the skill took from the runs

- Collapse counts as a cut (one-method class to function, registry to dict).
- "Reachable" is defined by the entry points real users have.
- Old-against-new comparison is named: all four cutting runs did it unprompted.
