# Results — iteration 1

Scores and analysis from one run of the three eval cases, with and without the skill.
The **test definitions** are in `../` (prompts, corpora, graders) and are what you re-run.
These are **results**: a snapshot, not source.

The six HTML artifacts the runs produced are deliberately NOT here. They are ~240K and go
stale the moment the skill changes. What is kept is the part that would be expensive to
recover: the per-assertion grades with their evidence, the timings, and the analysis.

| File | What |
| --- | --- |
| `analyst-notes.md` | findings recorded as each run landed, including two grader bugs worth not repeating |
| `benchmark.json` / `.md` | the aggregate, plus five analyst notes |
| `per-run-grades.json` | every assertion, per run, with its evidence sentence and the run's tokens/seconds |
| `mechanical-grade.sh` | the grep-based grader, hardened mid-run |

## The honest reading

100% with the skill, 79.4% without — but **only 4 of 19 assertions discriminate**, and three
of those are the same assertion (no time/progress indicator) repeated across cases.

Baselines matched the skill on content. Unaided runs independently found all four
mis-citation traps, produced 12 caution boxes across 11 sources, kept the incomplete-read
caveat, and declined to invent a grading scheme for a descriptive survey. **The skill's
advantage is not "notices the traps."**

The difference is the refusals. All three baselines added a scroll-progress indicator; two
added collapsed, optional self-check questions — precisely the prompt form with no
supporting evidence in any study. None of the three with-skill runs did either.

Cost: roughly 2x tokens and wall-clock.

## Known gaps in this iteration

Two large qualitative differences were never asserted, so they are invisible in the score:

1. **Prompts.** Not an assertion. 2 of 3 baselines added them; 0 of 3 with-skill runs did.
2. **Self-flagging.** With-skill runs marked their own derived figures as unsourced; the
   baselines added derived content silently.

Both should be assertions in iteration 2.
