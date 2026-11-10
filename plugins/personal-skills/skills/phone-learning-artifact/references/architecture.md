# The surfaces, and how to adapt them

The artifact has four surfaces plus one pinned element. Most corpora want all of them. A surface with nothing
real to put in it should be removed rather than padded. That is criterion 2 (cut extraneous material), the
best-evidenced lever available and the only one that works purely by removal.

All prose on every surface follows `style.md`.

## Contents

1. [The pinned anchor vocabulary](#1-the-pinned-anchor-vocabulary)
2. [Surface 1: the spine](#2-surface-1-the-spine)
3. [Surface 2: the clusters](#3-surface-2-the-clusters)
4. [Surface 3: the evidence cards](#4-surface-3-the-evidence-cards)
5. [Surface 4: what is open](#5-surface-4-what-is-open)
6. [Interaction rules](#6-interaction-rules)
7. [Adapting to an awkward corpus](#7-adapting-to-an-awkward-corpus)

---

## 1. The pinned anchor vocabulary

**What it is.** It is the small distinction the whole corpus hinges on. Readers keep collapsing it, and so do
the corpus's own authors. Three levels is the common shape, but two or four are fine.

Candidates across domains:
- evidence grades (GRADE, Oxford CEBM);
- study-design hierarchies;
- effect-size tiers;
- technology-readiness levels;
- diagnostic certainty;
- replication status;
- a domain's own split between *measured*, *modelled* and *assumed*.

**Why it is pinned rather than explained once.** Every graded claim in the corpus is a claim at some level. If
the reader has to recall which level a claim sits at, every card costs working memory it did not need to.
Keeping the vocabulary on screen also guards against the collapse, which comes back the moment the
distinction is out of sight.

**The closed state carries the content.** Show every level and a short gloss at all times. A tap adds the full
table and a plain statement of how the levels differ. It must never be the thing that reveals the levels
exist.

This follows the one positive finding in the progressive-disclosure literature. Labelled previews helped and
unlabelled expanders did not, because an unlabelled control "tells merely that more information is available,
but not how the linked text is related."

**If the corpus has no such distinction, delete the control.** Inventing one imposes a taxonomy the sources do
not have, and the artifact then teaches a framework instead of the research. The template removes the element
when `DATA.anchor` is `null`.

## 2. Surface 1: the spine

The spine shows the claims in dependency order, one per screen, where each creates the demand for the next.
That relation makes it a spine rather than a list. It also shows the reader why no part can be dropped.

Each screen carries four things:
- the claim;
- the connecting prose, in full;
- the sources behind it;
- its caveats, inline.

The claim is one flat sentence. The `forces` line is one plain sentence naming the next question or claim,
and it is where most of the habits in `style.md` §3 were found.

Two failure modes:

- **Counting nodes from section headings.** A paper's §1–§11 is not the shape of its argument. Read the
  argument and count the actual links. In the worked case the scaffold had eleven sections, and the chain had
  five nodes and four transitions. A wrong count invents screens that must then be padded.
- **Compressing the prose into the diagram.** The evidence supports Text+Diagrams (*g* = 0.45), which tests
  adding a graphic. Replacing connecting prose with a figure inverts the finding.
  - Keep the sentences and the logical connectives ("because", "so", "therefore"). For a skilled,
    high-knowledge reader, high-cohesion text measured better.
  - That is no licence for decorative transitions. `style.md` §4 draws the line.

## 3. Surface 2: the clusters

The clusters are the distinct literatures or themes. They show the reader the shape of the field.

**Page by the smallest conceptual unit, not by cluster.** A whole cluster overflows one screen. In the worked
case it overflowed by about 300px. The choice is between paging down and trimming, and trimming loses
substance. Show the cluster's lead only on its first subsection, so it does not cost height on every screen.

## 4. Surface 3: the evidence cards

Each source gets one card, filterable by cluster, with these fields:
- name;
- venue and year;
- what it actually claims;
- what it must not be cited for;
- its grade, where one applies;
- a link.

**This surface usually justifies the artifact.** Reading ergonomics buy a modest, self-paced gain. A navigable
index of mis-citations is new work that did not exist before.

### The "do not cite for" field

Dense corpora collect precise traps. Their typical shapes:

| Trap | Example shape |
| --- | --- |
| Measured X, cited for Y | a ranking analysis cited as a false-positive-rate procedure |
| Scope silently dropped | a null that holds only for one task type, cited as general |
| Theory cited for an effect size | a synthesis paper given a *d* it never reported |
| Unchecked assumptions | a bound whose proof assumes conditions the domain violates |
| Direction reversed | which component was frozen, which model probed which |
| Metadata wrong everywhere | author order, venue, the name of an effect |

Harvest them from errata, response letters, critique tables, limitations sections, and any sentence that
begins "an earlier draft wrongly". Then check that each one reached a card. A constraint that exists in the
corpus but not in the artifact is the one failure that makes the artifact worse than the sources.

**Scope cuts must not travel.** An item removed as out of scope is not a citation constraint. Putting it on a
card implies the source says something it does not.

Write each field as a plain statement of the trap. Don't add bold for warning or italics for stress. The field
name already tells the reader this is a constraint.

### Grades go only where a source speaks to one

A standards document, a protocol survey or a taxonomy often speaks to no graded claim. Forcing a grade onto it
manufactures the category error the vocabulary exists to prevent. In the worked case 15 of 40 cards carried a
level and 25 rightly carried none.

### Cards are exempt from the fit gate

Readers browse cards rather than read them, so a card may be taller than a screen. Cutting a trap note to fit
is the one place where the layout rule would destroy the content it is meant to serve.

## 5. Surface 4: what is open

This surface gathers the open questions and the two annotations in one place.

**Use exactly two annotations, and only where the sources themselves qualify something:**

- **◐ incomplete read**: the claim rests on an abstract, a publisher record or secondhand coverage.
- **○ ours / unsourced**: the claim is the author's own inference and appears in no cited work.

**Do not add a third marker meaning "verified".** Certifying every claim needs evidence the corpus does not
contain. In the worked case a draft "solid" marker would have mislabelled reading that was still outstanding.

A missing marker is honest, and a false certification is not. A false one does the most harm when someone or
something other than the reader compiled the corpus, because the reader cannot then rely on remembering having
checked a claim.

## 6. Interaction rules

**Nothing load-bearing goes behind a tap.** Caveats render with their claim. With every expander shut, the
artifact must read as a complete text. If closing one loses a proposition, that content was in the wrong
place.

**Overlay, never push.** In the worked case, a pinned panel that expanded into the layout shrank every content
screen by 160–430px and failed the gate. Overlay it instead:
- dim the content with a scrim;
- dismiss it on tap and on Escape.

**Set colour explicitly on every control.** A control that inherits the browser's `buttontext` colour turns
invisible wherever the palette and the browser's colour scheme fall out of step. That bug hit the one element
that had to be readable at all times.

**No prompts, no time estimate, no completion bar.** See the refusals list in the skill.

**Keep it self-contained.**
- No stylesheet, font, image, script, `@import`, `fetch` or XHR.
- Only outbound `<a>` links.
- Tell the user that a hosted copy still needs the network for the first load unless a service worker is
  added. The local file is the one that works offline.

**Keep the fit contract in step.** `window.__fitScreens` is the list the harness iterates. If you add a screen
without adding it there, the gate stops covering it and says nothing.

## 7. Adapting to an awkward corpus

| The corpus… | Do this |
| --- | --- |
| has no argument, only a survey | Drop the spine and open on clusters. Do not manufacture a thesis the authors did not advance. |
| has no graded vocabulary | Remove the pinned control entirely. |
| is a single meta-analysis, not a connected set | Clusters become moderators or outcome families. The spine becomes the chain from question to pooled estimate to boundary conditions. The cards become the included studies, and "do not cite for" holds the per-study caveats the forest plot flattens. |
| has hundreds of sources | Keep every card and let filtering carry the load. Do not sample. An index with silent gaps is worse than none, because the reader cannot tell absence from exclusion. |
| disagrees with itself | The disagreement is the spine. Build the structure around it, and give each side's cards what the other side says it cannot support. |
| is a single long document | Clusters become its parts and the cards become its own citations. Those citations are usually where the mis-citation traps hide. |
