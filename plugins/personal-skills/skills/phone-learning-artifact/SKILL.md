---
name: phone-learning-artifact
description: Turn the findings of a meta-analysis, systematic review, literature survey, or any connected body of research into a phone-readable learning artifact. The output is one self-contained HTML file built only on the instructional-design evidence that replicates, written in plain prose to McCarthy's science-writing rules, and illustrated on every argument and domain screen with one figure whose form is chosen, from the evidence on visual learning, to show that screen's claim. Use whenever someone wants research, a literature review, a reading list, a survey, study findings, or a dense technical document made readable on a phone, turned into a revision aid, or "easier to absorb". Use it especially when they ask which design choices improve comprehension, because most popular answers (segmenting, pre-training, progressive disclosure, optimal line length, pretesting prompts) do not survive meta-analysis and this skill carries the corrected list.
---

# Phone learning artifact

This skill turns a body of research into something a person can absorb on a phone.

The output is one self-contained HTML file. There is no framework and no external subresource, and the figures
are embedded in the file. It opens offline as a local file and can be published for a phone URL.

Three things make this worth a skill:
- **The instructional-design literature misleads.** The famous, intuitive design moves mostly fail
  independent meta-analysis, and a first attempt will rebuild them with confidence.
- **The one layout rule that replicates has to be measured.** The measurement is easy to get wrong.
- **Generated prose tires the reader.** A dash in every sentence, bold in every paragraph and a reveal at the
  end of each claim wear the reader out by the third screen. The prose rules in `references/style.md` fix
  this, and gate 9 checks them.

## What you are optimising

The goal is comprehension per unit of reading effort on a single pass. Memorisation is a different task. If
the user asks for spaced repetition or flashcards, tell them so rather than blending the two, because the
design rules differ.

The gain has a ceiling. Instructional-design effects run larger in system-paced settings than self-paced ones,
and a phone read is self-paced. The gain is real but modest. The lasting value usually comes from the evidence
cards described below, not from the reading ergonomics.

## The six criteria that survive

`references/evidence.md` holds the citations, effect sizes and moderators. Read it before you justify a
design decision to the user, and quote the independent effect size rather than the originating lab's.

| # | Criterion | What it forces |
| --- | --- | --- |
| 1 | No reading unit requires scrolling or panning | One conceptual unit per screen. The text of a screen fits without scrolling, and its figures sit below the text. This is the only layout rule with real evidence. It is a pass/fail gate you measure (see *Fit check*). |
| 2 | Cut extraneous material | Strip the apparatus: project bookkeeping, "still to do", revision tables, decoration. This is the best-evidenced lever, and it only removes. Applied to sentences, it is McCarthy's first rule. |
| 3 | Signal structure | The reader can always see where they are in the argument. |
| 4 | Diagrams alongside prose, not instead of it | Keep the connecting prose and add the figure. Every argument and domain screen carries one figure that shows its claim, chosen against a brief written before any figure is retrieved (see step 5). The evidence is for adding a graphic, never for replacing text with one. |
| 5 | A compact table can beat informationally matched prose | Render the corpus's core distinction as a table. |
| 6 | Remove time pressure and never frame it as preliminary | No reading-time estimate, no completion bar, no "quick summary" framing. This is the largest lever, and it is not a layout decision. |

## What to refuse, and why

Each of these was tried, checked and found to fail. When a design instinct pulls toward one, the instinct is
the known failure mode.

- **Segmenting into learner-paced chunks.** The evidence base is narrated animation. Its mechanism, a stream
  that outruns the reader, does not exist in static text.
- **Pre-training (teach the vocabulary first, then the process).** No meta-analysis exists and no static-text
  experiment. It is non-significant in its own originating corpus.
- **Split-attention as a reason to avoid cross-references.** The meta-analysis excludes text-only separation
  by construction, and a self-contained table sits in its non-significant cell. You may still avoid "see §4"
  for ordinary usability. Just don't claim evidence for it.
- **Pretesting and prediction prompts.** The benefit is confined to the pretested items. For text the general
  effect is about zero and slightly negative.
- **Progressive disclosure and tap-to-reveal.** The one direct test found it faster and less accurate. Readers
  rated it easier while performing worse. Hover-for-definition lowered comprehension too.
- **Optimal line length (45–75 characters).** This is craft convention, not a finding. On screens, longer
  lines read faster.
- **Pagination over scrolling.** It was null in the only powered phone replication. Criterion 1 is a
  different rule, about requiring scrolling at all.
- **Progress indicators and reading-time badges.** There is no comprehension evidence either way. Omit them
  under criterion 6, without claiming more.
- **Disfluency and hard-to-read fonts.** The effect does not replicate, and equivalence has been shown.

Two findings should be softened rather than dropped:
- **Expertise reversal** is real on average, but asymmetric and contested. Don't strip scaffolding on its
  authority.
- **Self-explanation** has a comprehension-specific cell that does not clear zero, and every study collected
  a response. An optional, uncollected prompt is the one form never shown to work.

## Building it

### 1. Read the corpus and find its spine

Identify these, in order:

- **The spine.** These are the claims in dependency order, where each creates the demand for the next. Count
  the actual nodes rather than inferring them from section headings. A pure survey has no argument. For one,
  use its strongest organising sequence, or drop this surface and open on the clusters.
- **The anchor vocabulary.** This is the small distinction the whole corpus hinges on, which readers and
  authors keep collapsing. Examples:
  - evidence grades;
  - study-design hierarchies;
  - effect-size tiers;
  - maturity levels;
  - a domain's own three-way split.

  Not every corpus has one. If it does, it is the most valuable thing to keep on screen. If it does not, omit
  the surface rather than invent one.
- **The clusters.** These are the distinct literatures or themes.
- **The sources.** List every work, with what it actually claims.
- **The gaps.** These are the open questions, plus the claims the corpus itself hedges.

### 2. Apply source precedence

A later document in the corpus sometimes narrows a claim that an earlier one still states broadly. When it
does, the later wording wins. Corrections often fail to travel backwards. An errata note, a revision log or a
critique response narrows something the main text still asserts in its original form. A faithful
transcription of the broad version then reinstates a claim the authors already retracted.

Before extracting, look for the corpus's record of corrections, such as revision notes, response letters,
critique tables and errata. Build a precedence list from them and treat each entry as a regression test.

### 3. Write the evidence cards

This surface usually justifies the artifact. Each source gets one card with these fields:
- name;
- venue and year;
- what it actually claims;
- what it must not be cited for;
- its grade or level, where one applies;
- a link.

The "do not cite for" field is the signature move. Dense corpora collect precise mis-citation traps:
- a study that measured X is cited for Y;
- an author order is wrong everywhere;
- a theoretical synthesis is cited for an effect size;
- nobody checks a bound's assumptions.

Spread across tens of thousands of words, these traps are hard to keep track of. Put in one field you can
filter, each one takes seconds to check.

Harvest them from errata, critique tables, limitations sections, and any place the corpus says "an earlier
draft wrongly…". Then check that each one reached a card (see *Gates*).

Two rules keep the cards honest:

- **Attach a grade or level only where the source speaks to one.** A methods survey or a standards document
  often speaks to no graded claim. Forcing a level onto it manufactures the category error the vocabulary
  exists to prevent. Expect many cards to carry none.
- **Use at most two annotations, and only where the corpus itself qualifies something.**
  - *Incomplete read*: the card rests on an abstract, a publisher record or secondhand coverage.
  - *Ours / unsourced*: the claim is the author's own inference and appears in no cited work.

  Do not add a "verified" or "solid" marker. Certifying every claim needs evidence the corpus does not
  contain, and a false certification is worse than no marker.

### 4. Write the prose

Read `references/style.md` before writing any sentence the reader will see. It holds:
- McCarthy's rules, from Savage and Yeh's *Nature* column;
- the two external texts the owner approved as the voice to imitate;
- the habits that made earlier artifacts tiring, each tied to the rule it breaks.

The short version:
- **One idea per sentence and one message per paragraph.**
- **The claim comes first, plainly.** No reveal, no "not the one you expect".
- **Dashes are rare.** A dash marks the one clause that matters most, never two sentences in a row. Asides go
  in parentheses, and a second idea gets a full stop.
- **No bold or italics for emphasis inside sentences.** Labels and field names may be bold.
- **Cut intensifiers, tagalong clauses and talk about the text.**
- **Cut "X, not Y" unless the rejected X is a claim someone actually made.**
- **Keep defined terms exact.** The anchor vocabulary and technical terms repeat. Vary only ordinary words.

The `forces` field on a spine node attracts the worst habits. Keep it to one plain sentence that names the
next question or the next claim.

### 5. Brief, then find or draw the figures

Every spine node and every cluster subsection gets one figure. A second figure is allowed only when it shows
a different relation, with its own brief. The figures sit below the text on their screen. The text must still
fit one screen (gate 5), so the reader scrolls only to reach the figures.

The evidence supports this with one condition. Adding a graphic to text is the largest media effect in the
multimedia corpus (Text+Diagrams *g* = 0.45). An image that is only on topic is a seductive detail, and
seductive details cost *g* ≈ −0.33 to −0.41. So a figure earns its place only by showing what the text claims.
A third representation adds little (*g* ≈ 0.12), which is why the default is one.

**Write the brief before looking at any figure.** The brief names the one relation the figure must make
visible, the kind of claim and the form. `references/visuals.md` maps each kind of claim to the form the
evidence supports, quantitative (comparison, interval, trend, share) and qualitative (process, structure,
spatial layout). Writing the brief first keeps the choice from being anchored on whatever figures the sources
happen to contain.
- Give each screen to a subagent with a fresh context, and run the screens in parallel. It gets the screen's
  text, the numbers its sources give and `visuals.md`, and no candidate figure. The prompt is in `visuals.md`
  §1. Without a subagent tool, write every brief yourself before retrieving anything.
- Do not prompt the subagent as an expert in visual learning. A persona brings the model's priors, and those
  include the claims the skill refuses (learning styles, "visual learners", any picture helps). The expertise
  is the table in `visuals.md`.
- A claim that is one or a few exact numbers gets the brief `kind:'value'` and no figure. The text states the
  numbers, or a small table does (criterion 5).

**Retrieve against the brief.** A candidate meets the brief when it shows the brief's relation in the brief's
form, its labels can be read at 390 px, and it uses no form `visuals.md` refuses (a mean drawn as a filled bar,
slices compared across a pie). A paper's first figure is often a teaser rather than its evidence, so read the
captions before choosing (`figures.py find`). Crop to the panel that carries the relation, because the other
five panels of a six-panel figure are extraneous material (criterion 2). Then look at the 390 px preview.

Three sources can supply the figure. Use the first one that meets the brief.
1. **From the evidence on that screen** (`from:'evidence'`). Take the figure from a source the screen cites.
   It wins any tie, because it is the evidence itself.
   - arXiv serves the PDF at `arxiv.org/pdf/<id>`. Its HTML version at `arxiv.org/html/<id>` serves each
     figure as a separate image.
   - PubMed Central and Europe PMC serve the figures of open-access articles as separate images.
   - For a DOI, Semantic Scholar returns an open-access PDF link and any arXiv or PMC id:
     `api.semanticscholar.org/graph/v1/paper/DOI:<doi>?fields=openAccessPdf,externalIds`.
   - Evidence that is not a paper (a report, a dataset, documentation, a repository) usually has its own
     charts and diagrams. Use those.
2. **Drawn for this artifact** (`from:'drawn'`). Write an SVG of the brief's form to `figures/<id>.svg`. Use
   only numbers the sources give. When a cited figure exists but fails the brief (a forest plot unreadable at
   390 px, a mean drawn as a bar), redraw its numbers. The credit then reads "Redrawn from Smith et al. 2020,
   Fig. 3" and links to the original.
3. **A public figure from outside the cited evidence** (`from:'illustration'`). Search for an openly licensed
   figure that meets the brief: Wikimedia Commons, an open-access review of the topic, Our World in Data, an
   agency report. The template labels it as an illustration, so the reader never takes it for the cited
   evidence. That label does the job of the "do not cite for" field.

For a quantitative brief, drawing comes before searching, because an outside chart plots other data. For a
qualitative brief, take whichever of tiers 2 and 3 meets the brief better.

If nothing meets the brief, give the screen `figs:[]` and a `nofig` reason that names the brief's relation, and
tell the user. A `value` brief's reason begins "value:". Never fill the slot with a decorative image.

**Write the caption to `references/style.md`.** The caption says where to look and what that part shows
about the claim. It adds no proposition the text lacks, because the text must read completely without the
figure (gate 6). The credit names the source, the figure number and the licence. The alt text describes what
the figure depicts.

**Handle the files with the script.** Downloads are untrusted. Keep them in their own directory, keep the
script outside it, and run it with `python3 -I`.

```bash
python3 -I scripts/figures.py find  dl/paper.pdf                  # captions, by page
python3 -I scripts/figures.py page  dl/paper.pdf 4 pages/         # render a page to look at
python3 -I scripts/figures.py prep  dl/paper.pdf figures/ smith20-fig3 --page 4 --crop 0.1,0.12,0.9,0.5
python3 -I scripts/figures.py prep  dl/fig2.png figures/ jones21-fig2
python3 -I scripts/figures.py inline artifact.html figures/       # embed every img: id
```

`prep` writes a WebP under 180 KB and a preview at 390 px wide. `inline` embeds every figure the `DATA` block
names as a data URI between the `FIGS` markers, so the file stays self-contained. Rerun it after every change
to `figures/`. Never paste base64 by hand, because one figure runs to tens of thousands of tokens.

**Licences and privacy.**
- Record each figure's licence in its credit and in the provenance comment. Prefer CC BY, CC0 and public-domain
  figures. Before the artifact gets a shareable URL, tell the user which figures are not openly licensed.
- Search with a cited work's public metadata (title, DOI, arXiv id) and general topic terms. Do not put an
  unpublished corpus's claims into a search engine.

### 6. Build from the template

`assets/template.html` is a working skeleton. It carries the structural fixes that took several iterations to
find. Copy it, replace the `DATA` block, and keep the CSS and the interaction code.
`references/architecture.md` explains each surface and what to do when a corpus lacks one.

Content lives in a single `DATA` block separate from presentation, so a re-sync to the sources is a data edit.
Put the provenance in an HTML comment at the head of the file:
- which version of the corpus the artifact was built from;
- the sync rule;
- the precedence list;
- the gate results.

A second file would drift out of step.

### 7. Run the gates

Content fidelity matters more than rendering. Run every gate and report the numbers.

1. **Precedence audit.** Every narrowed claim appears in its narrow form. The precedence list from step 2
   supplies the regression tests.
2. **Grade audit.** Every grade matches the corpus's own wording. Cards with no graded claim carry none.
3. **Mis-citation coverage.** Walk the corpus's errata and critique records item by item. Each constraint on
   how a source may be cited reaches that source's card. Scope cuts must not appear: those are items removed
   as out of scope rather than corrected.
4. **Annotation audit.** Every annotation traces to a specific qualification in the sources. Nothing the
   corpus hedges appears without its hedge.
5. **Fit check** (criterion 1). See below. It is pass/fail. The text above each screen's figures must fit.
6. **Tap-independence.** With every expander shut, the artifact reads as a complete text. If closing one
   loses a proposition, that content was in the wrong place.
7. **Offline.** No remote stylesheet, font, image, script, `@import`, `fetch` or XHR. Figures are embedded
   as data URIs by `figures.py inline`. Only outbound `<a>` links are allowed. Tell the user that a hosted copy still needs the network for the first load unless a service
   worker is added.
8. **Condensation audit.** Run `scripts/condensation-audit.py <artifact> <source>...`.
   - **What it checks.** Gates 1 to 4 check fidelity to the corpus. This one checks fidelity to each sentence:
     whether shortening a source sentence dropped something that changes its claim. The artifact is a
     compression step, so this error is introduced by you, and a faithful corpus can still be misreported.
   - **What it detects.** It catches one high-precision pattern. A comparative survives while its noun is
     dropped ("preserves far more per step": more of what?). A reader asked exactly that of a published
     artifact.
   - **Limits.** Its recall is low by design. Read the prose too, especially wherever you compressed a
     sentence that carries a number, a scope condition or a negation.
9. **Prose audit.** Run `scripts/prose-audit.py <artifact>`. It fails the artifact on three counts:
   - more than six dash uses per 1000 words (the *Nature* column runs at 4.5);
   - two consecutive sentences with dashes;
   - more than two bold spans per 1000 words inside sentences.

   It also lists warnings: reflexive contrasts, stacked transitions, intensifiers, long sentences and
   semicolons. Judge each warning, because good prose triggers some. Then read every screen aloud once and
   apply the cut test from `references/style.md`. The script is a floor, and passing it does not make the
   prose good.
10. **Figure audit.** `scripts/fit-check.sh` counts the figures on every argument and domain screen.
    - It fails a screen with no figure and no `nofig` reason, and a screen with more than two.
    - It fails a figure without an image, alt text, caption or credit, and an image over 300 KB.
    - It fails a figure without a brief: an empty `rel` or `form`, or a `kind` that `visuals.md` does not list.
      A `value` brief on a figure fails too, because a value gets no figure.
    - It lists each `nofig` screen without failing, because that reason goes to the user.

    Then look at every figure beside its brief and caption. Check four things: the figure shows the brief's
    relation, it shows nothing the brief leaves out, its `from` label matches where it came from, and its
    labels can be read at 390 px.

### Fit check: measure, don't eyeball

`scripts/fit-check.sh` measures overflow with two things pinned to a target phone: the viewport geometry and
the `clamp()` font size. Both matter.
- Headless Chrome silently ignores `--window-size` for the viewport. It reported 756px when asked for 390px.
- A narrower screen can fit more, because a `vw`-based font shrinks with it.

Measuring at the wrong width gives confident, wrong answers in both directions.

```bash
scripts/fit-check.sh path/to/artifact.html 390 844
scripts/fit-check.sh path/to/artifact.html 360 800
```

It reports overflow per screen and flags horizontal overflow and tap targets under 44pt. On a screen with
figures it measures the text down to the `[data-fit-exempt]` figure region. It also runs gate 10.

Three failures to expect, all found this way:

- **A cluster is too big for one screen.** Page by the smallest conceptual unit, which is the subsection, not
  the cluster. Whole clusters overflowed by about 300px. Page down rather than trim, because the summaries are
  substance.
- **A pinned panel pushes the layout.** An expanding header shrank every content screen by 160–430px. Make it
  an overlay with a tap-dismiss scrim and Escape, so the screen beneath does not reflow.
- **A control inherits the browser's `buttontext` colour.** Wherever the palette and the browser's colour
  scheme fall out of step, that control turns invisible. Set colour explicitly on anything that must always
  read.

Reference cards are exempt from this gate. Readers browse them rather than read them, and cutting a
mis-citation note to fit a screen loses the nuance that justifies it.

## Reporting back

Give the user:
- the six criteria you built against;
- the gate numbers, including the prose audit's three rates;
- the figure count, which screens have no figure and why, and which figures are not openly licensed;
- each cited figure that failed its brief and was redrawn, and why it failed;
- the design moves you refused, and why.

The refusals are often the most useful part, because they are what the user would otherwise ask you to add.

State the bound honestly: the gain is modest and self-paced. If a check failed, say which one and what fixing
it would take. Write the report to `references/style.md` as well.

## Bundled files

- `references/evidence.md` holds the instructional-design findings: citations, DOIs, effect sizes, moderators,
  what each study measured, and what must not be claimed. Read it before justifying a design choice.
- `references/architecture.md` describes the surfaces in detail. It covers adapting them to a corpus without a
  spine or an anchor vocabulary, and the interaction rules.
- `references/visuals.md` maps each kind of claim to its visual form, with the evidence strength of each rule.
  It also holds the brief prompt. Read it before writing a brief.
- `references/style.md` holds the prose rules, the approved models and the habits to avoid. Read it before
  writing.
- `scripts/fit-check.sh` is the viewport-accurate overflow harness. It also runs the figure audit (gate 10).
- `scripts/condensation-audit.py` is gate 8. It finds comparatives whose object was dropped.
- `scripts/figures.py` finds figure captions in a PDF, renders pages, crops and compresses a figure, and embeds
  every figure into the artifact.
- `scripts/prose-audit.py` is gate 9. It counts dash rate, dash runs and bold in prose, and lists the softer
  habits.
- `assets/template.html` is the working skeleton. Replace its `DATA` block.
