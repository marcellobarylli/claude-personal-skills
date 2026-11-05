---
name: phone-learning-artifact
description: Turn the findings of a meta-analysis, systematic review, literature survey, or any connected body of research into a phone-readable learning artifact — one self-contained HTML file built only on the instructional-design evidence that actually replicates. Use whenever someone wants research, a literature review, a reading list, a survey, study findings, or a dense technical document made readable on a phone, turned into a revision aid, or "easier to absorb" — and especially when they ask which design choices genuinely improve comprehension, because most popular answers (segmenting, pre-training, progressive disclosure, optimal line length, pretesting prompts) do not survive meta-analysis and this skill carries the corrected list.
---

# Phone learning artifact

Turn a body of research into something a human can actually absorb on a phone.

The output is **one self-contained HTML file**: no build step, no framework, no external
subresource. It opens offline as a local file, and can be published for a phone URL.

Two things make this worth a skill rather than improvisation. First, the instructional-design
literature is **mostly wrong in the direction people expect** — the famous, intuitive design
moves largely fail independent meta-analysis, and a first attempt will confidently rebuild
them. Second, the one layout rule that *does* replicate has to be **measured**, not eyeballed,
and the measurement is fiddly enough to get wrong.

## What you are optimising

Comprehension per unit of reading effort, on a **single pass**. Not memorisation. If the user
asks for spaced repetition or flashcards, that is a different (and well-served) task — say so
rather than quietly blending them, because the design rules differ.

Be honest about the ceiling: instructional-design gains run **larger for system-paced than
self-paced settings**, and a phone read is self-paced. The gain is real but modest. The
durable value usually turns out to be the *evidence cards* (below), not the reading
ergonomics.

## The six criteria that survive

Full citations, effect sizes and the moderators are in `references/evidence.md` — read it
before you justify a design decision to the user, and quote the independent effect size
rather than the originating lab's.

| # | Criterion | What it forces |
| --- | --- | --- |
| 1 | **No reading unit requires scrolling or panning** | One conceptual unit per screen. This is the only layout rule with real evidence, and it is a **pass/fail gate you measure** — see *Fit check*. |
| 2 | **Cut extraneous material** | Strip the apparatus: project bookkeeping, "still to do", revision tables, decorative anything. Best-evidenced lever available, and subtractive. |
| 3 | **Signal structure** | Position in the argument always visible. |
| 4 | **Diagrams *alongside* prose, not instead of it** | Keep the connecting prose *and* show the structure. The evidence is for *adding* a graphic, never for replacing text with one. |
| 5 | **A compact table can beat informationally matched prose** | Render the corpus's core distinction as a table. |
| 6 | **Remove time pressure; never frame it as preliminary** | No reading-time estimate, no completion bar, no "quick summary" framing. **The largest lever, and not a layout decision at all.** |

## What to refuse, and why

These are not oversights. Each was tried, checked, and failed — so when a design instinct
pulls toward one, that instinct is the known failure mode, not a missing feature.

- **Segmenting into learner-paced chunks** — the evidence base is narrated animation; the
  mechanism (interrupting a stream that outruns the reader) does not exist in static text.
- **Pre-training (teach the vocabulary first, then the process)** — no meta-analysis exists,
  no static-text experiment, non-significant in its own originating corpus.
- **Split-attention as a reason to avoid cross-references** — the meta-analysis excludes
  text-only separation *by construction*. A self-contained table sits in its non-significant
  cell. You may still avoid "see §4" for ordinary usability; just don't claim evidence.
- **Pretesting / prediction prompts** — benefit is confined to the pretested items; for text
  the general effect is ≈ 0, and slightly negative.
- **Progressive disclosure / tap-to-reveal** — the one direct test found it *faster but less
  accurate*, and readers rated it *easier* while performing worse. Hover-for-definition
  lowered comprehension too.
- **Optimal line length (45–75 characters)** — craft convention, not a finding. On screens,
  longer lines read *faster*.
- **Pagination over scrolling** — null in the only powered phone replication. (Distinct from
  criterion 1, which is about *requiring* scrolling at all.)
- **Progress indicators and reading-time badges** — no comprehension evidence in either
  direction. Omit them under criterion 6, not as a claim of their own.
- **Disfluency / hard-to-read fonts** — does not replicate; equivalence established.

Two to soften rather than drop: **expertise reversal** (real on average, but asymmetric and
contested — don't strip scaffolding on its authority) and **self-explanation** (its
comprehension-specific cell does not clear zero, and every study collected a response, so an
*optional, uncollected* prompt is the one form never shown to work).

## Building it

### 1. Read the corpus and find its spine

Identify, in order:

- **The spine** — the claims in dependency order, where each creates the demand for the next.
  Count the actual nodes; do not infer the number from section headings. If the corpus is a
  pure survey with no argument, use the strongest organising sequence, or drop this surface
  and open on clusters instead.
- **The anchor vocabulary** — the small distinction the whole corpus hinges on, which readers
  and authors keep collapsing. Evidence grades, study-design hierarchies, effect-size tiers,
  maturity levels, a domain's own three-way split. Not every corpus has one; if it does, it
  is the single highest-value thing to keep permanently on screen. If it does not, omit the
  surface rather than invent one.
- **The clusters** — the distinct literatures or themes.
- **The sources** — every work, with what it *actually claims*.
- **The gaps** — open questions, and claims the corpus itself hedges.

### 2. Apply source precedence

**Where a later document in the corpus narrows a claim an earlier one still states broadly,
the later wording wins.** Corrections frequently fail to propagate backwards: an errata note,
a revision log, or a critique response will narrow something the main text still asserts in
its original form. A faithful transcription of the broad version silently reinstates a claim
the authors already retracted.

Before extracting, look for the corpus's own record of corrections — revision notes, response
letters, critique tables, errata — and build a precedence list. Treat each as a regression
test later.

### 3. Write the evidence cards

**This is the highest-value surface and usually the reason the artifact earns its keep.**
Per source: name · venue/year · **what it actually claims** · **what it must not be cited
for** · its grade or level *where one applies* · link.

The "do not cite for" field is the signature move. Dense corpora accumulate precise
mis-citation traps — a study that measured X being routinely cited for Y, an author order
that is wrong everywhere, a theoretical synthesis cited for an effect size, a bound whose
assumptions nobody checks. Spread across tens of thousands of words these are unholdable; as
a filterable field they are checkable in seconds.

Harvest them from errata, critique tables, "limitations" sections, and any place the corpus
says "an earlier draft wrongly…". Then verify each reached a card — see *Gates*.

Two rules keep this honest:

- **Attach a grade or level only where the source speaks to one.** A methods survey or a
  standards document often speaks to no graded claim at all; forcing a level on it
  manufactures the exact category error the vocabulary exists to prevent. Expect a large
  share of cards to carry none.
- **Use at most two annotations, and only where the corpus itself qualifies something**:
  *incomplete read* (rests on an abstract, a publisher record, secondhand coverage) and
  *ours / unsourced* (the author's own inference, in no cited work). **Do not add a
  "verified" or "solid" marker** — certifying every claim needs evidence the corpus does not
  contain, and a false certification is worse than no marker.

### 4. Build from the template

`assets/template.html` is a working skeleton carrying the structural fixes that cost
iterations to find. Copy it, replace the `DATA` block, keep the CSS and the interaction code.
`references/architecture.md` explains each surface and what to do when a corpus lacks one.

Content lives in a single `DATA` block separate from presentation, so re-syncing to the
sources is a data edit. Put provenance — which version of the corpus this was built from, the
sync rule, the precedence list, the test results — in an HTML comment at the head of the file
rather than a second file nobody will keep aligned.

### 5. Run the gates

Content fidelity matters more than rendering. Run all of these and report the numbers.

1. **Precedence audit.** Every narrowed claim appears in its narrow form. Use the precedence
   list from step 2 as regression tests.
2. **Grade audit.** Every grade asserted matches the corpus's own wording; cards with no
   graded claim carry none.
3. **Mis-citation coverage.** Walk the corpus's errata and critique records item by item.
   Each constraint on how a source may be cited reaches that source's card. Scope cuts — items
   removed as out of scope rather than corrected — must *not* appear.
4. **Annotation audit.** Every annotation traces to a specific qualification in the sources.
   Nothing the corpus hedges renders unhedged.
5. **Fit check** (criterion 1) — see below. Pass/fail, not preference.
6. **Tap-independence.** With every expander shut, the artifact reads as a complete text. If
   closing one loses a proposition, that content was in the wrong place.
7. **Offline.** No stylesheet, font, image, script, `@import`, `fetch` or XHR. Only outbound
   `<a>` links. Say plainly that a *hosted* copy still needs the network for the first load
   unless a service worker is added.
8. **Condensation audit.** `scripts/condensation-audit.py <artifact> <source>...` Gates 1–4
   check fidelity to the **corpus**. This checks fidelity to the **sentence** — whether
   shortening a source sentence dropped something that changes what it claims. It is a
   distinct failure mode with a distinct origin: the traps in gate 3 come from the corpus,
   but this one is introduced *by you*, because the artifact is a compression step. A
   perfectly faithful corpus can still be misreported here.

   It detects one high-precision pattern — a comparative or quantity word surviving while
   the noun it governed is dropped ("preserves far more per step" — more *what*?) — found in
   real review when a reader asked that exact question of a published artifact. Low recall
   by design: a clean run means this mechanically-checkable error is absent, not that the
   prose is faithful. **Read the prose too**, especially anywhere you compressed a sentence
   carrying a number, a scope condition, or a negation.

### Fit check — measure, don't eyeball

`scripts/fit-check.sh` measures overflow with the viewport geometry **and** the `clamp()`
font size pinned to a target phone. Both matter: headless Chrome silently ignores
`--window-size` for the viewport (it reported 756px when asked for 390px), and a narrower
screen can paradoxically *fit more* because a `vw`-based font shrinks with it. Measuring at
the wrong width gives confident, wrong answers in both directions.

```bash
scripts/fit-check.sh path/to/artifact.html 390 844
scripts/fit-check.sh path/to/artifact.html 360 800
```

It reports per-screen overflow and flags horizontal overflow and tap targets under 44pt.

Three failures to expect, all found this way:

- **A cluster is too big to be one screen.** Page by the *smallest* conceptual unit — the
  subsection, not the cluster. Whole clusters overflowed by ~300px. Page down rather than
  trim, because the summaries are substance, not apparatus.
- **A pinned panel that pushes layout.** An expanding header shrank every content screen by
  160–430px. Make it an **overlay** with a tap-dismiss scrim and Escape; the screen beneath
  must not reflow.
- **A control that inherits the UA's `buttontext`.** Wherever a palette and the browser's
  colour scheme desynchronise, such a control renders invisible. Set colour explicitly on
  anything that must always read.

Reference cards are **exempt** from the gate: they are browsed, not read, and truncating a
mis-citation note to fit a screen cuts the nuance that justifies it.

## Reporting back

Give the user the six criteria you built against, the gate numbers, and — importantly — the
design moves you *refused* and why. That list is often the most useful output, because it is
what they would otherwise have asked you to add.

Tell them the honest bound (modest, self-paced) rather than overselling. If any check failed,
say which and what it would take.

## Bundled files

- `references/evidence.md` — the verified instructional-design findings: citations, DOIs,
  effect sizes, moderators, what each study actually measured, and what must not be claimed.
  Read before justifying a design choice.
- `references/architecture.md` — the surfaces in detail, how to adapt them to a corpus that
  lacks a spine or an anchor vocabulary, and the interaction rules.
- `scripts/fit-check.sh` — the viewport-accurate overflow harness.
- `scripts/condensation-audit.py` — gate 8; finds comparatives whose object was dropped.
- `assets/template.html` — working skeleton; replace the `DATA` block.
