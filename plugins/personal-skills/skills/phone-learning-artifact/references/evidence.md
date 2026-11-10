# The instructional-design evidence, verified

Scope: comprehension, transfer and cognitive load on a single pass. Findings whose only established outcome
is delayed free recall are out of scope. They belong to the memorisation literature, which is a different task
with different rules.

Every claim below was checked against primary sources and meta-analyses. The first draft of this list was
mostly wrong, which is why the file exists. The intuitive, widely repeated design principles are largely the
ones that fail. Sometimes an independent meta-analysis disagrees with the originating lab's own figure. When
it does, quote the independent one.

Labels used below:
- **Caveat** marks a limit on how a finding may be cited.
- **What survives** marks the usable signal inside a refuted principle.

## Contents

1. [Use these six](#1-use-these-six)
2. [Refuse these nine](#2-refuse-these-nine)
3. [Soften these two](#3-soften-these-two)
4. [Framing corrections](#4-framing-corrections)
5. [Do not cite](#5-do-not-cite)
6. [The honest bound](#6-the-honest-bound)

---

## 1. Use these six

### 1. No reading unit requires scrolling or panning

**Clinton-Lisell, V., & Litzinger, C. (2026).** Decoding digital reading: a network meta-analysis of
comprehension across devices. *Education and Information Technologies, 31*(6), 1611–1643.
`10.1007/s10639-025-13843-8`. It covers 56 samples, 79 effects and five conditions.

> Scrolling necessary: paper better by *g* = 0.35–0.48. No scrolling: no reliable difference,
> *g* = 0.03–0.12.

This result turns the whole paper-versus-screen literature into one variable a designer can act on.

**Context.** Delgado, Vargas, Ackerman & Salmerón (2018), *Educational Research Review, 25*, 23–38,
`10.1016/j.edurev.2018.09.003`. It pools 54 studies and 171,055 participants, with *g* = −0.21
[−0.28, −0.14]. Its moderators:
- time frame: limited −0.26, self-paced −0.09;
- genre: informational −0.27, narrative +0.01;
- publication year: the gap grows by 0.01 per year.

**Caveat.** Device type was not a significant moderator.
- Smartphones rank last in the 2026 network meta-analysis, but on three studies only. Both scrolling subgroups
  there are non-significant, and the small-screen explanation is the authors' own conjecture.
- Salmerón et al. (2024), `10.1037/edu0000830`, found handhelds at about half the computer effect. That study
  explicitly excluded mobile phones.

Claim the scrolling result and give no phone-specific number.

### 2. Cut extraneous material

**Sundararajan, N., & Adesope, O. (2020).** *Educational Psychology Review, 32*(3), 707–734.
`10.1007/s10648-020-09522-4`. Seductive details: *g* ≈ −0.33 to −0.41.

This is the best-evidenced lever, and it works by removal, which makes it the cheapest. Mayer's own coherence
figure (*d* = 0.86) is a median over his lab. Use the independent number.

### 3. Signal structure

**Alpizar, D., Adesope, O., & Wong, R. (2020).** *ETR&D, 68*(5), 2095–2119. `10.1007/s11423-020-09748-7`.
*d* = 0.38.

The effect is modest and real. It covers headings, position indicators and explicit structure cues.

### 4. Diagrams alongside prose, not instead of it

**Cromley, J. G., & Chen, R. (2025).** A meta-analysis of Richard Mayer's multimedia learning research.
*Educational Research Review, 49*, 100730. `10.1016/j.edurev.2025.100730`.
- It covers 92 articles, 181 studies and 591 effects.
- The overall *g* is 0.37 and declines per year.
- Eight principles are non-significant.
- Text+Diagrams reaches *g* = 0.45 [0.32, 0.57], the largest and most consistent media type.

The multimedia principle tests adding a graphic to text. It never tests replacing text with one, so an
instinct to "turn the prose into a diagram" inverts the finding.

**Applied to retrieved figures.** This finding is why every argument and domain screen carries one to three
figures. Two limits come with it.
- The graphics in the multimedia corpus depict the content of the text. A figure that is only on topic (a
  photo of the lab, a logo, a stock image) is a seductive detail, which costs *g* ≈ −0.33 to −0.41 (criterion
  2). Relevance is the condition, so a screen without a representative figure gets none.
- The redundancy moderator in Schroeder & Cenkci (2018) puts a diagram intelligible alone in a
  non-significant cell (*g* = 0.26). No study here tests a figure placed below the text on a phone, one
  scroll away. Placing it there keeps criterion 1 intact for the text. That trade is a design judgement, so
  claim no effect size for the placement.

### 5. A compact table can beat informationally matched prose

**Brick, C., McDowell, M., & Freeman, A. L. J. (2020).** Risk communication in tables versus text: a
registered report randomized trial on "fact boxes". *Royal Society Open Science, 7*(3), 190876.
`10.1098/rsos.190876`.
- It was pre-registered, with *N* = 2,305 census-matched UK adults.
- The control was informationally matched prose.
- Comprehension was 79.6% against 69.7%, *d* = 0.39 [0.31, 0.47].
- The effect was consistent across numeracy and education.

**Caveat.** The paper does not identify which items required comparing options. Claim *"a compact table
improved comprehension over matched prose"*. Do not claim *"tables beat prose for relational reasoning."*

### 6. Remove time pressure and never frame it as preliminary

**Ackerman, R., & Goldsmith, M. (2011).** *JEP: Applied, 17*(1), 18–32. `10.1037/a0022086`.
- With time imposed, there was no media difference.
- With time free, screen scored 63.2% against paper's 72.3%, *d* = 0.79.
- Overconfidence was +10.4 on screen against +2.3 on paper, and stopping was erratic, *d* = 0.95.

Delgado et al.'s largest significant moderator supports it, and so do two further studies.
- **Sidi, Shpigelman, Zalmanov & Ackerman (2017)**, *Learning and Instruction, 51*, 61–73. Screen inferiority
  appeared when the task was framed as preliminary or less important, even under a loose time frame.
- **Lauterman & Ackerman (2014)**, `10.1016/j.chb.2014.02.046`. In-depth processing eliminated it.

This is the largest available lever, and it is not a layout decision. It is why the artifact carries no time
estimate and no completion bar, and why it presents itself as the real reading.

**Caveat.** Ackerman & Goldsmith had a subgroup self-assess every 3 minutes. That added so much variance that
the subgroup was excluded from the study-time analyses. It is the only datum on mid-reading prompts, and it
counts as a cost.

---

## 2. Refuse these nine

### 1. Segmenting into learner-paced chunks

**Rey et al. (2019)**, *EPR, 31*(2), 389–419, `10.1007/s10648-018-9456-4`.
- Retention *d* = 0.32 and transfer *d* = 0.36.
- Learner-paced retention is *d* = 0.19, *p* = .10, which is non-significant.
- Learner-paced cognitive load is *d* = 0.08, *p* = .43, also non-significant.
- Allowing the learner to reorder segments extinguished the effect.

The corpus is narrated animation:
- the average segment is 75.49 s long;
- 54 of 88 comparisons use mixed audio-visual material;
- the authors concede they never coded material type.

In Mayer's own corpus it is *g* = 0.19, non-significant.

The mechanism is interrupting a stream that outruns the reader. Static text is already learner-paced, so the
mechanism does not exist there.

### 2. Pre-training

No meta-analysis exists. In Mayer's own corpus it is *g* = 0.28, non-significant. No experiment testing it on
static technical text was found. It is an evidence gap, not a principle.

### 3. Split attention as a reason to avoid prose cross-references

**Schroeder, N. L., & Cenkci, A. T. (2018)**, *EPR, 30*(3), 679–701, `10.1007/s10648-018-9435-9`. Overall
*g* = 0.63, transfer *g* = 0.65, *k* = 37.

Its inclusion criterion, verbatim: *"We did not consider moving relevant text closer to other on-screen text
to be an integrated design when there were no relevant images involved."* So it contains zero text-only
comparisons.

Its redundancy moderator is significant (*Q*b = 11.18, *p* = .01):
- not-redundant material: *g* = 0.72;
- a diagram intelligible alone: *g* = 0.26 [−0.34, 0.85], non-significant.

A self-contained table sits in that second cell.

Schroeder & Cenkci (2020), `10.1037/edu0000372`, reviewed 41 comparisons. They found that the load measures
largely do not support the extraneous-load account.

**Caveat.** The circulating *d* = 0.85 pools spatial and temporal contiguity, so never cite it as spatial.
Avoiding "see §4" is fine on usability grounds. Just don't claim evidence for it.

### 4. Pretesting and prediction prompts

**St. Hilaire, K. J., Chan, J. C. K., & Ahn, D. (2024).** *Psychonomic Bulletin & Review, 31*, 411–441.
`10.3758/s13423-023-02353-8`.
- On pretested items the effect is *g* = 0.54 [0.42, 0.66], *k* = 97.
- On general items it is *g* = 0.04 [−0.04, 0.11], *k* = 91, *p* = .349.
- By material, audiovisual is 0.17 and text is −0.005, *p* = .017.

King-Shepard et al. (2025), `10.1007/s10648-025-10075-7`, replicated it: repeated items *g* = 0.66, new items
*g* = 0.01.

Richland, Kornell & Kao (2009), `10.1037/a0016496`, verbatim: *"The benefit of testing did not spread to
untested items, but neither did it hurt."* Brod (2021), `10.3758/s13423-021-01904-1`, is a theoretical review
explicitly limited to simple declarative learning.

### 5. Progressive disclosure and tap-to-reveal

**McDonald, A. M., Reeder, R. W., Kelley, P. G., & Cranor, L. F. (2009).** *PETS 2009*, LNCS 37–55.
`10.1007/978-3-642-03168-7_3`. *N* = 749. Verbatim:
- *"participants were faster with standardized formats but at the expense of accuracy for layered
  policies"*;
- *"the layered notice effectively hides information and reduces transparency."*
- *"Participants found layered easier to understand even though they were less accurate."*

Krenca, Taylor & Deacon (2024), `10.1111/1467-9817.12468`, found that hover-for-definition hyperlinks lowered
comprehension. Scrolling did not.

**What survives.** DeStefano & LeFevre (2007), `10.1016/j.chb.2005.08.012`, report that labelled previews
helped. Their reason is that an unlabelled link *"tells merely that more information is available, but not
how the linked text is related."* This is the one positive signal, and the overlay pattern rests on it.

An expander's closed state must therefore already carry the proposition and its relation to the argument. A
reader who never expands anything still gets a coherent text.

**Caveat.** DeStefano & LeFevre is a narrative review of 38 studies, not a meta-analysis. Its claim of
"more links → worse learning" is overstated: Madrid et al. (2009), `10.1016/j.chb.2008.06.005`,
tested 3 against 8 links and found no effect.

### 6. Optimal line length (45–75 characters)

This is craft convention, and the record is worse than "weakly evidenced":

| Figure | Actual source | Type |
|---|---|---|
| 66 / 45–75 | Bringhurst, *Elements of Typographic Style* | craft, asserted not derived |
| ≤70 cpl | Spencer, *The Visible Word* (1968) | craft book |
| 52 cpl | Rayner & Pollatsek (1989) textbook | re-reading of Tinker; nobody ran a study producing 52 |
| ~57 cpl | Tinker & Paterson (1929) | measured speed in print |
| ≤80 chars | WCAG 2.2 SC 1.4.8 | "Studies have shown", no citation |

Dyson (2004), `10.1080/01449290410001715714`, is the standard synthesis. Verbatim: *"Few studies specifically
address the effect of line length on comprehension"* and *"Most of the studies on line length report faster
reading with longer lines."*

The individual studies agree:
- **Duchnicky & Kolers (1983):** no comprehension difference.
- **Dyson & Kipping (1998):** 100 cpl read faster than 25, with no comprehension difference. Readers rated 55
  easiest.
- **Shaikh & Chaparro (2005):** 95 cpl was fastest, with no main effect on comprehension.
- **Atilgan, Xiong & Legge (2020)**, `10.1073/pnas.2007514117`: about 13 characters per line already buys 80%
  of maximum reading speed. That result is about speed, not comprehension.

Say that line length has never been shown to matter. Do not say it has been shown not to matter.

**What survives.** The robust generalisation here is about users, not layout. Across six independent studies,
preference does not predict performance. Muter & Maurutto (1991) bundled nine recommended settings and tested
them against plain text. They found no difference in rate or comprehension, yet 13 of 18 readers preferred
the enhanced format.

### 7. Pagination over scrolling

**Joshi, N., Casiez, G., & Vogel, D. (2025).** Is pagination better than scrolling when reading on a phone?
*CHI EA '25*. `10.1145/3706599.3720178`. *N* = 100 participants read on their own phones.
- Comprehension was 14.8 against 14.7 out of 20, non-significant.
- Duration and mental demand were also non-significant.

Sanchez & Wiley (2009), `10.1177/0018720809352788`, is the usual citation.

**Caveat.** That effect rests on Experiment 1 alone (*N* = 40):
- Experiment 2 did not replicate the main effect.
- Its paginated condition confounds pagination with segmentation at meaning boundaries.

This refusal is separate from criterion 1, which asks whether scrolling is required at all.

### 8. Progress indicators and reading-time estimates

No peer-reviewed comprehension evidence exists in either direction. The large rigorous literature measures
dropout instead.

- **Villar, Callegaro & Yang (2013)**, `10.1177/0894439313497468`, ran 32 randomised experiments. The ordinary
  constant-speed bar does not even reduce drop-off.
- **Conrad, Couper, Tourangeau & Peytchev (2010)**, `10.1016/j.intcom.2010.03.001`, ran two studies of about
  3,000 each.
  - **Caveat.** Both depth-of-processing proxies were null in both studies.
  - Only 37.4% of the on-demand group ever clicked "Show Progress".

Omit progress indicators under criterion 6, without making an evidence claim of their own.

**Caveat, a citation to avoid.** Mangen, Walgermo & Brønnick (2013) is routinely cited for the "sense of the
whole text" argument. It manipulated, measured and displayed no progress cue of any kind.

### 9. Disfluency and hard-to-read fonts

It does not replicate.
- **Xie, Zhou & Liu (2018)**, `10.1007/s10648-018-9442-x`: 39 experiments and 3,135 participants. Recall
  *d* = −0.01, transfer *d* = 0.03.
- **Meyer et al. (2015)**, `10.1037/xge0000049`: *N* = 7,367, CI [−0.06, +0.05].
- **Taylor et al. (2020)**, `10.1080/09658211.2020.1758726`: *N* = 882, with statistical equivalence
  established.

Bjork & Yue (2016) write: *"the remarkable and intriguing benefits … do not replicate, at least not in any
general way."* Sans Forgetica's original claims were never peer-reviewed.

---

## 3. Soften these two

### Expertise reversal

**Tetzlaff, L., Simonsmeier, B., Peters, T., & Brod, G. (2025).** *Learning and Instruction, 98*, 102142.
`10.1016/j.learninstruc.2025.102142`. It covers 60 studies, 176 effects and *N* = 5,924.
- low prior knowledge: *d* = 0.505;
- high prior knowledge: *d* = −0.428 [−0.647, −0.209];
- the interaction: *d* = 0.971.

Three qualifiers apply.
- **It is asymmetric.** The authors advise *"rather provide assistance than withhold it when in doubt."*
- **True crossover is concentrated in between-cohort designs.** It is about −0.21 in the most common design,
  a median split.
- **A larger synthesis found no moderation.** Noetel et al. (2022), `10.3102/00346543211052329`, covered 29
  reviews, 1,189 studies and 78,177 participants. They found that prior knowledge did not moderate the effect:
  *"the expertise-reversal hypothesis … was not supported by our analyses."*

**Caveat.** Never cite Kalyuga et al. (2003) for an effect size. It is a theoretical synthesis.

**What survives.** For a skilled, high-knowledge reader the direction may flip.
- **O'Reilly & McNamara (2007)**, `10.1080/01638530709336895`, *n* = 143: the benefit of low-cohesion text was
  confined to less skilled high-knowledge readers.
- Skilled high-knowledge readers benefited from high cohesion.

So keep the logical connectives rather than compressing them out. `style.md` §4 separates these from the
decorative transitions the style rules cut.

### Self-explanation

**Bisra, K., Liu, Q., Nesbit, J. C., Salimi, F., & Winne, P. H. (2018).** *EPR, 30*(3), 703–725.
`10.1007/s10648-018-9434-x`. *g* = .552 [.454, .650], *k* = 69, *N* = 5,917.

The headline figure needs four qualifications.
- **Inflated controls.** 41 of 69 effects use do-nothing controls (*g* = .673, confirmed inflated). Against a
  provided explanation the effect is *g* = .354, *k* = 6.
- **Comprehension does not clear zero.** By outcome, comprehension is *g* = .282, *k* = 3,
  CI [−.014, .579].
- **The uncollected form was never tested.** Every included study elicited a response. None tested a prompt
  embedded without collecting an answer, which is the optional, skippable form an artifact would use.
- **Caveat.** Publication bias was assessed by fail-safe *N* only.

---

## 4. Framing corrections

**Germane load was redefined, not dropped.** Sweller, van Merriënboer & Paas (2019),
`10.1007/s10648-019-09465-5`, verbatim:

> rather than contributing to the total load, germane cognitive load redistributes working memory resources
> from extraneous activities to activities directly relevant to learning … rather than imposing a load in its
> own right.

So total load is intrinsic plus extraneous. Sweller (2010), `10.1007/s10648-010-9128-5`, extended element
interactivity from intrinsic load to extraneous load as well.

**There is no single "Mayer's effect size."** His figures are medians over his own lab, and they move by up to
about 70% between his own publications.
- Cromley & Chen (2025) re-analysed his corpus. Eight principles were non-significant, and the overall
  *g* = 0.37 declines per year.
- Personalization is often quoted at *d* = 1.00. Ginns, Martin & Marsh (2013) put it at *d* = 0.30 for
  retention and 0.54 for transfer.
- Almeida, Münzer & Kühl (2024), `10.1111/jcal.13026`, found non-personalized materials better on transfer.

**Common authorship errors.** Getting these wrong undermines the rigour the artifact claims.
- Schroeder & Cenkci (not Cepeda).
- Bisra, Liu, Nesbit, Salimi, Winne (not Adesope).
- Schroeder, Nesbit, Anguiano, Adesope.
- McNamara et al. (1996) is in *Cognition and Instruction*, 14(1), 1–43, not *Discourse Processes*. It never
  uses "reverse cohesion". That term is from O'Reilly & McNamara (2007).

---

## 5. Do not cite

**Unobtainable.** Nothing should rest on these:
- Dyson & Haselgrove (2001), the only study supporting a line-length comprehension optimum;
- Ginns (2006);
- Kalyuga et al. (2003);
- Bringhurst's primary text.

**Not peer-reviewed:**
- *Usability News*, the in-house newsletter of Wichita State's SURL and the source of much line-length lore;
- Youngman & Scharff (1998);
- Bringhurst and Spencer, craft books that are the actual origin of "66" and "70";
- WCAG 2.2 SC 1.4.8's uncited "80 characters";
- Colin Wheildon's *Type and Layout*;
- Nielsen Norman Group on progressive disclosure, the sole basis for the pattern;
- "8 min read" labels and Kindle "time left", product features never evaluated for comprehension;
- Sans Forgetica's original claims.

**Theory, not evidence.**
- **Larkin & Simon (1987)**, `10.1111/j.1551-6708.1987.tb00863.x`. It has no participants and no effect
  sizes, and the "(sometimes)" in its title matters.
- **Nesbit & Adesope (2006)**, on concept maps. It tests no tables, so do not cite it to justify a table. Use
  Brick et al. (2020) instead.
  - Its own headline *g* = .604 is inflated.
  - The representational-choice branch is *g* = .388.
  - **Caveat.** Hyperlinked maps show *g* = .017, *k* = 6, which is no benefit.

---

## 6. The honest bound

Noetel et al. (2022) found that good design mattered more for complex material and for system-paced settings
than for self-paced ones. A self-paced phone read is where these gains are smallest.

Say so. The artifact is still worth building. Its lasting value is usually the evidence cards and the
mis-citation field. Those are content work, and they matter more than the reading ergonomics.
