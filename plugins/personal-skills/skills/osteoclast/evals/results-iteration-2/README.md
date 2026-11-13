# Results: iteration 2

The revised skill on the two cutting cases, plus a new case, `feature-plain-ask-waits`. Only with-skill runs were
repeated for `diff-safe-cuts-only` and `feature-thin-coverage`; their baseline rows are copied from iteration 1,
since a baseline does not depend on the skill. `repo-survey-waits` was not repeated.

| Case | With skill | Without | Source removed, with / without |
| --- | --- | --- | --- |
| diff-safe-cuts-only | 9/9 | 7/9 | 79% / 79% (iteration 1: 56% with) |
| feature-thin-coverage | 9/9 | 6/9 | 71% / 70% (iteration 1: 57% with) |
| feature-plain-ask-waits | 6/6 | 3/6 | nothing cut / whole module rewritten |

## The honest reading

The collapse rule closed the size gap, and the pins and one-commit-per-cut history are still there. On size and on
preserved behavior the skill now matches the baseline; it does not beat it.

What the skill adds is on the new case. Asked only to "simplify it", the baseline rewrote 16 files in the working
tree and removed the cache, which changes what a malformed request returns, then reported that as a decision for
the user afterwards. The skill run surveyed, tiered the cache as a contract change and waited.

Across both iterations the differences are: a survey that waits, contract changes held back and listed, pins left
in the repo, one revertible commit per cut, and no bug fixes or redesign smuggled in.

## Known gaps

- **One run per configuration.** No variance estimate.
- **Pins are large**: 153 and 177 test lines for 86 and 113 source lines. "A few cases per behavior" did not
  shrink them.
- **Cost**: about +30% tokens; 10 to 16 minutes against 8 to 9 on the cutting cases.
- **No case where a cut goes red** and has to be reverted, and none in a language without a test runner.
- Three assertions (`report-has-lines-and-gate` twice, `findings-carry-evidence`) check the reply's form. They
  discriminate, but a reader may not care that the test command is named.
