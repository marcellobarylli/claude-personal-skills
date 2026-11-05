# Analyst notes — iteration 1 (written as runs land)

## Grader hardening (before any run was graded)
First mechanical grader searched for the WORD "progress-bar". The survey baseline named its
element `prog`, so it scored a false PASS on the assertion the skill cares most about.
Detector now keys on implementation: `(id|class)="prog*`, a scroll-driven width percentage,
or explicit time language. Both baselines graded so far FAIL it once hardened.
**Lesson: grade behaviour, not vocabulary.**

## Baselines are stronger than expected on CONTENT
`connected-corpus-with-grades / without_skill` independently produced:
  - all 4 specific mis-citation traps (4/4)
  - "Don't say" boxes for all 12 scope cautions — it found the do-not-cite value unaided
  - the Marchetti incomplete-read caveat, kept prominent
  - E0/E1/E2 preserved, §E's narrowed claim kept narrow
  - caught 3 real defects in its own build + an arithmetic error in the source
So the skill's advantage is NOT "notices the traps". Expect assertions 03/04/06 to be
non-discriminating. Say so rather than let them inflate the delta.

## Where the baselines diverge — all of it is the refusals list
| Refused by the skill | corpus baseline | survey baseline |
| --- | --- | --- |
| progress indicator | yes (bar + localStorage pos) | yes (bar + "Resume where you left off") |
| prompts/questions | yes — 3x "Quick check — N questions", COLLAPSED+OPTIONAL | no |
| keep the apparatus | yes — all 14 review-table rows reproduced | n/a (source has none) |

The collapsed-optional prompt is the exact form with no supporting evidence anywhere. Two
independent runs reached for a progress bar. This is the clearest signal so far that the
refusals list is the skill's real payload.

## Nuance to carry into grading, not to paper over
Assertion 08 (scope cut absent) is FAIL on a literal reading — "author affiliation
digression" appears. But it appears as row 12 of the corpus's own review table, labelled
"cut as out of scope", not as a constraint on a source card. The deeper failure is
criterion 2 (apparatus kept), not mis-citation. Grade FAIL, annotate why.

## survey case — with_skill vs without_skill
Assertions: 5/5 vs 4/5 (baseline fails only the progress indicator). But the assertion set
UNDER-MEASURES the difference. Two properties neither grader checks:

| | with_skill | baseline |
| --- | --- | --- |
| hedges attached to the number they constrain | 13 figure cards, each with a "does not support" note | 0 — hedges left in their original sections |
| artifact's OWN derived figures flagged | 9 marks; explicitly flags that counts summing to 61 is its inference, and that "the remaining 32" is subtraction | 0 — derived content added unmarked |

The second is an honesty property I did not think to assert. The with-skill run marked its
own inferences as unsourced; the baseline added derived numbers silently. Worth a new
assertion in iteration 2.

Both runs correctly avoided inventing a grading scheme, so assertion 02 is NON-DISCRIMINATING
on this case — the "don't invent" instruction did not have to fire, because the baseline
had no urge to invent either. The instruction may still matter on a corpus that *almost*
has a vocabulary; this one is too obviously descriptive to test it hard.

## cost
survey: with_skill 106,626 tok / 661s vs baseline 46,821 tok / 299s — 2.3x tokens, 2.2x time.
Real, and worth stating plainly: the skill buys fidelity and refusals, and it is not cheap.

## single-meta-analysis / with_skill — 6/6
Fit claim independently re-verified by me: 19/19 at 390x844, matching its report. Not just
asserted — reproducible.

Three things it did that the skill asked for and that I did not have to prompt:
  - Adapted per architecture.md §7: moderators became clusters, included studies became
    cards, the spine became scope -> pooled -> prediction interval -> what moves it.
  - Found a failure at 375x667 and PAGED the moderator table rather than trimming it. That
    is the instruction verbatim ("page down rather than trim").
  - Chose risk-of-bias as the anchor vocabulary. The source has no named grading scheme, but
    risk-of-bias IS a graded distinction in it with an effect size per level. Good judgement:
    it neither invented a vocabulary nor skipped the surface when a real one was available.
  - Refused to fabricate DOI links for synthetic sources. Not in the skill; correct anyway.

Grades 4 of 7 cards rated, 3 correctly unrated (source gives no rating for Petrova or the
Weller/Jaffar/Ruiz group). That is the "grade only where the source speaks to one" rule
firing on real data.

## cost so far
| case | arm | tokens | seconds |
| --- | --- | --- | --- |
| survey | with | 106,626 | 661 |
| survey | base | 46,821 | 299 |
| meta | with | 121,430 | 815 |
| corpus | base | 63,754 | 578 |
