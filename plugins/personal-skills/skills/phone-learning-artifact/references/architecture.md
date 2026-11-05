# The surfaces, and how to adapt them

The artifact has four surfaces plus one pinned element. Most corpora want all of them, but
**a surface with nothing real to put in it should be removed, not padded** — that is criterion
2 (cut extraneous material), which is the best-evidenced lever available and the only one that
is purely subtractive.

## Contents

1. [The pinned anchor vocabulary](#1-the-pinned-anchor-vocabulary)
2. [Surface 1 — the spine](#2-surface-1--the-spine)
3. [Surface 2 — the clusters](#3-surface-2--the-clusters)
4. [Surface 3 — the evidence cards](#4-surface-3--the-evidence-cards)
5. [Surface 4 — what is open](#5-surface-4--what-is-open)
6. [Interaction rules](#6-interaction-rules)
7. [Adapting to an awkward corpus](#7-adapting-to-an-awkward-corpus)

---

## 1. The pinned anchor vocabulary

**What it is.** The small distinction the whole corpus hinges on and that readers — including
the corpus's own authors — keep collapsing. Three levels is the common shape, but two or four
are fine.

Candidates across domains: evidence grades (GRADE, Oxford CEBM), study-design hierarchies,
effect-size tiers, technology-readiness levels, diagnostic certainty, replication status, a
domain's own three-way split between *measured* / *modelled* / *assumed*.

**Why pinned rather than explained once.** Every graded claim in the corpus is a claim *at a
level*. If the reader has to recall which level a claim sits at, every card costs working
memory it did not need to. Keeping it on screen is also a structural guard against the
collapse: the error reappears the moment the distinction is out of sight.

**The closed state must carry the content.** Show every level and a short gloss at all times.
Tapping *adds* detail — the full table and the "X is not a weak Y" statement. It must never be
the thing that reveals the levels exist. This follows the one positive finding in the
progressive-disclosure literature: labelled previews helped, unlabelled expanders did not,
because an unlabelled control "tells merely that more information is available, but not how the
linked text is related."

**If the corpus has no such distinction, delete the control.** Inventing one imposes a
taxonomy the sources do not have, and the artifact then teaches a framework rather than the
research. The template removes the element cleanly when `DATA.anchor` is `null`.

## 2. Surface 1 — the spine

The claims in dependency order, one per screen, where each **creates the demand for the next**.
That relation is what makes it a spine rather than a list, and it is what a reader needs in
order to see why no part can be dropped.

Each screen carries: the claim, the connecting prose **in full**, the sources behind it, and
its caveats **inline**.

Two failure modes:

- **Counting nodes from section headings.** A paper's §1–§11 is not its argument's shape. Read
  the argument and count the actual links — in the worked case the scaffold had eleven sections
  and the chain had five nodes and four transitions. Getting this wrong is not cosmetic: it
  invents screens that must then be padded.
- **Compressing the prose into the diagram.** The evidence supports Text+Diagrams (*g* = 0.45),
  which tests *adding* a graphic. Replacing connecting prose with a figure inverts the finding.
  Keep the sentences, and keep explicit connectives — for a skilled, high-knowledge reader,
  high-cohesion text measured *better*.

## 3. Surface 2 — the clusters

The distinct literatures or themes, so the reader can see the shape of the field.

**Page by the smallest conceptual unit, not by cluster.** A whole cluster reliably overflows
one screen — measured at ~300px in the worked case. The choice is between paging down and
trimming, and trimming loses substance, not apparatus. Show the cluster's lead only on its
first subsection so it does not cost height on every screen.

## 4. Surface 3 — the evidence cards

One card per source: name · venue/year · **what it actually claims** · **what it must not be
cited for** · grade *where one applies* · link. Filterable by cluster.

**This is usually the surface that justifies the artifact.** Reading ergonomics buy a modest,
self-paced gain; a navigable mis-citation index is content work that did not exist before.

### The "do not cite for" field

Dense corpora accumulate precise traps. Typical shapes:

| Trap | Example shape |
| --- | --- |
| Measured X, cited for Y | a ranking analysis cited as a false-positive-rate procedure |
| Scope silently dropped | a null that holds only for one task type, cited as general |
| Theory cited for an effect size | a synthesis paper given a *d* it never reported |
| Unchecked assumptions | a bound whose proof assumes conditions the domain violates |
| Direction reversed | which component was frozen, which model probed which |
| Metadata wrong everywhere | author order, venue, the name of an effect |

Harvest them from errata, response letters, critique tables, limitations sections, and any
sentence beginning "an earlier draft wrongly". Then check each reached a card — a constraint
that exists in the corpus but not in the artifact is the one failure that makes the artifact
actively worse than the sources.

**Scope cuts must not travel.** An item removed as *out of scope* is not a citation
constraint; putting it in a card implies the source says something it does not.

### Grades go only where a source speaks to one

A standards document, a protocol survey, or a taxonomy often speaks to no graded claim at all.
Forcing a grade onto it manufactures the exact category error the vocabulary exists to
prevent. In the worked case 15 of 40 cards carried a level and 25 correctly carried none.

### Cards are exempt from the fit gate

They are browsed, not read. Let them be taller than a screen. Truncating a trap note to fit is
the one place where the layout rule would destroy the content it is meant to serve.

## 5. Surface 4 — what is open

Open questions, plus the two annotations, in one place rather than scattered.

**Use exactly two annotations**, and only where the sources themselves qualify something:

- **◐ incomplete read** — rests on an abstract, a publisher record, or secondhand coverage.
- **○ ours / unsourced** — the author's own inference, in no cited work.

**Do not add a third meaning "verified".** Certifying every claim needs evidence the corpus
does not contain, and in the worked case a draft "solid" marker would have positively
mislabelled reading that was still outstanding. A missing marker is honest; a false
certification is not. This matters most when the corpus was compiled by someone — or
something — other than the reader, who then cannot fall back on their own memory of having
checked a claim.

## 6. Interaction rules

**Nothing load-bearing behind a tap.** Caveats render with their claim. With every expander
shut, the artifact must read as a complete and coherent text; if closing one loses a
proposition, that content was in the wrong place.

**Overlay, never push.** A pinned panel that expands into the layout shrank every content
screen by 160–430px in the worked case and failed the gate. Overlay it, dim the content with a
scrim, dismiss on tap and on Escape.

**Set colour explicitly on every control.** A control that inherits the UA's `buttontext`
renders invisible wherever the palette and the browser's colour scheme desynchronise. That bug
hit the one element required to be always readable.

**No prompts, no time estimate, no completion bar.** See the skill's refusals list.

**Self-contained.** No stylesheet, font, image, script, `@import`, `fetch` or XHR. Only
outbound `<a>` links. Say plainly that a *hosted* copy still needs the network for the first
load unless a service worker is added — the local file is the one that is genuinely offline.

**Keep the fit contract in step.** `window.__fitScreens` is what the harness iterates. Add a
screen without adding it there and the gate silently stops covering it.

## 7. Adapting to an awkward corpus

| The corpus… | Do this |
| --- | --- |
| has no argument, only a survey | Drop the spine; open on clusters. Do not manufacture a thesis the authors did not advance. |
| has no graded vocabulary | Remove the pinned control entirely. |
| is a single meta-analysis, not a connected set | Clusters become moderators or outcome families; the spine becomes the causal/inferential chain from question to pooled estimate to boundary conditions. The cards become the included studies — and "do not cite for" becomes the per-study caveats the forest plot flattens away. |
| has hundreds of sources | Keep every card; filtering carries the load. Do not sample — an index with silent gaps is worse than none, because the reader cannot tell absence from exclusion. |
| disagrees with itself | That *is* the spine. Make the disagreement the structure, with each side's cards carrying what the other says it cannot support. |
| is a single long document | Clusters become its parts; the cards become its own citations, which is usually where the mis-citation traps are hiding. |
