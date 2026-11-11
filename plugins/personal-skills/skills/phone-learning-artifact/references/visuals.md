# Choosing the visual form

SKILL.md step 5 writes a brief for each screen before any figure is retrieved. This file is what the brief is
written from. It maps the kind of claim on a screen to the visual form the evidence supports, and it marks how
strong that evidence is.

Evidence was checked on 2026-11-11 against primary sources where they could be reached. Each row says whether
its rule rests on independent replications, on one group, on a single study, or on nothing found. Quote that
strength when you justify a figure to the user.

## Contents

1. [The brief](#1-the-brief)
2. [Quantitative claims](#2-quantitative-claims)
3. [Qualitative claims](#3-qualitative-claims)
4. [Rules for every figure](#4-rules-for-every-figure)
5. [What not to claim](#5-what-not-to-claim)
6. [Sources](#6-sources)

## 1. The brief

A brief names the one relation a figure must make visible. It is written before anyone looks at a candidate
figure, so the choice is not anchored on whatever figures the sources happen to contain.

It has three fields, stored on the figure in the `DATA` block:
- `rel`: one sentence naming what the reader should see ("the effect shrinks from 0.45 to 0.26 when the diagram
  stands alone").
- `kind`: one of the kinds in §2 and §3.
- `form`: the form from that row's table, its encodings and what it leaves out.

**Who writes it.** A subagent with a fresh context, one per screen, run in parallel. Give it the screen's text,
the numbers its sources give and this file. Give it no candidate figure, no PDF and no search results. If no
subagent tool is available, write every brief yourself before retrieving anything.

**No persona.** Do not prompt the subagent as an "expert in visual learning". A persona adds the model's priors,
and those include the claims §5 refuses. The expertise is the tables below.

Prompt, with the bracketed parts filled in:

```text
You are writing a figure brief for one screen of a phone-readable learning artifact. The figure will sit
below the screen's text on a 390 px wide phone, static, and the text must read completely without it.

Read the attached visuals.md. Use only its tables and rules to choose the form. Where a row says its
evidence is weak, still follow it, but say so in your note.

Screen text:
[claim, because, caveats, or the cluster subsection text, verbatim]

Numbers the sources give for this screen:
[each number with its source, interval and unit; or "none"]

Return exactly:
rel:  one sentence naming the single relation the reader should see.
kind: one kind from visuals.md §2 or §3. If the claim is one or a few exact values, answer "value".
form: the form, its encodings (what goes on which axis or in which node), and what it leaves out.
note: one or two sentences on any judgement the tables did not settle.
second: "none", or a second relation the text states that the first figure cannot show, with its own
        rel, kind and form.
```

**A `value` brief gets no figure.** When the claim is one number or a few exact numbers, the text states them,
or a two- or three-row table does (criterion 5). The screen carries `figs:[]` and a `nofig` reason that begins
"value:".

**A second figure needs a second relation.** One figure per screen is the default. A second is allowed only
when the subagent names a relation the first cannot show, and it carries its own brief.

## 2. Quantitative claims

| `kind` | Form | Avoid | Evidence |
| --- | --- | --- | --- |
| `value` | No figure. The number goes in the text or a small table. | A chart whose only job is to show one value. | Theory and single experiments (Vessey 1991; Vessey & Galletta 1991). The one meta-analysis (Hwang & Wu 1990) reports a task-complexity moderator, and its k and effect sizes were not confirmed. |
| `comparison` | Dots or bars on one aligned axis from a common baseline, with the items compared placed next to each other. | Angle, area, bubbles, and stacked segments that do not share a baseline. | Replicated. Position, then length, then angle and slope, then area (Cleveland & McGill 1986). Heer & Bostock (2010) and Talbot et al. (2014) replicate it, and adjacency lowers error. Davis et al. (2024) find that it holds on average and that 20–25% of people do better with another chart. |
| `interval` | A dot with whiskers. The figure names the interval in words ("95% CI of the mean"), marks the no-effect line and labels the direction ("better", "worse"). | A filled bar for a mean, with or without error bars. | Replicated: the within-the-bar asymmetry (Newman & Scholl 2012) holds in at least four labs (Correll & Gleicher 2014; Pentoney & Berger 2016; Okan et al. 2018; Kerns & Wilmer 2021). Dot plots fixed it in Okan et al. That readers do not tell CIs from SE bars rests on one lab (Belia et al. 2005). |
| `pooled` | The summary point and its interval on a labelled axis. When studies are shown, encode weight by position or size and say in words that bigger means more weight. | Relying on square size alone to signal weight. | One group (Fitzgerald & Tipton 2022; Fitzgerald et al. 2025), and its 2025 plots were interactive. Treat the form as a default. |
| `trend` | A line over an ordered variable (time, dose, size). Categorical factors, including a 2 × 2 interaction, get dots or bars. | A line joining unordered categories. | Position ranking as above. Line graphs drew more misreadings of 2 × 2 interactions than bar graphs in Ali & Peebles (2013), three experiments by one group. |
| `distribution` | The data as dots, or a quantile dotplot. | A mean bar standing in for the spread. | Correll & Gleicher (2014). Fernandes et al. (2018) for quantile dotplots, one group. |
| `share` | One share of one whole: a labelled pie, donut or 100% bar. Shares compared across groups or slices: aligned bars. | Asking the reader to compare one slice with another. | Two independent labs found pie and bar equal for share-of-whole judgments and pie worse for comparisons (Simkin & Hastie 1987; Spence & Lewandowsky 1991). |
| `spread` | When the reader will judge what an effect means for individuals, show the spread of outcomes beside the interval. | An interval alone, read as the range of outcomes. | Two studies with shared authors (Hofman et al. 2020; Zhang et al. 2023). |

For every quantitative form:
- **Label the values directly.** The perceptual ranking holds for the average reader only (Davis et al. 2024).
- **Keep the value axis at least 80 px tall at 390 px wide, with gridlines at least 8 px apart.** Charts 40 px tall
  drew more error, and there was no gain above 80 px. This is a single experiment (Heer & Bostock 2010, Exp. 3).
- **Use only numbers the sources give.** A drawn figure plots the cited numbers and no others.

## 3. Qualitative claims

| `kind` | Form | Avoid | Evidence |
| --- | --- | --- | --- |
| `process` | A static flow diagram: numbered nodes, labelled arrows, top to bottom. | Animation, and arrows with no label. | Meta-analytic. Organisational pictures *g* = 0.39 (Banks et al. 2026, k = 10) and 0.52 [0.17, 0.86] (Hu et al. 2021). Flow diagrams 0.35 [0.10, 0.60] (Guo et al. 2020). With written text, animation's advantage over static pictures falls to *g* = 0.105 [−0.05, 0.26], n.s. (Berney & Bétrancourt 2016, k = 58). |
| `structure` | A node-link map with labelled links and the central ideas as nodes. | A map the reader expands by tapping. | Meta-analytic, same team. Studying a provided map beats text by *g* = 0.29 to 0.39 and lists or outlines by 0.28 to 0.43 (Nesbit & Adesope 2006; Schroeder et al. 2018). Static maps 0.39, hyperlinked maps 0.02 n.s. Central ideas 0.60, details 0.20 (k = 6). |
| `taxonomy` | A tree of the classes, with the classes the text names as nodes. | Leaves the text never mentions. | The concept-map evidence above. No taxonomy-specific test was found. |
| `contrast` | Usually the compact table of criterion 5. A figure only when the two things differ in structure or layout: two aligned panels with matched labels. | Two panels drawn at different scales or in different styles. | No meta-analysis of contrast visuals was found. The table rests on criterion 5. |
| `spatial` | A schematic labelled diagram that shows only the parts the text names. | Photographic or realistic detail. | Pictorial diagrams *g* = 0.63 [0.40, 0.85] (Guo et al. 2020, k = 13). Representational pictures 0.44 (Banks et al. 2026) and 0.24 [0.10, 0.37] (Hu et al. 2021). Schematic over realistic rests on single studies (Butcher 2006; Menendez et al. 2020). Guo et al. found no benefit from either realism or simplicity. |

## 4. Rules for every figure

**One relation, one graphic type.** Mixed-graphic displays gave *g* = 0.14, n.s. (Guo et al. 2020). More than two
representations beat two by only *g* = 0.118 [0.050, 0.185] and raised cognitive load (Rexigel et al. 2024).

**Match colours and labels to the text.** An element in the figure takes the same colour or label as its term in
the text above. Colour cues carry the most consistent support: retention 0.44 and transfer 0.39 (Schneider et
al. 2018). A verbal pointer alone ("see the figure") was n.s. (Richter et al. 2016). Never use a flashing or
blinking cue (Schneider et al. 2018: −0.56 for retention, k = 3).

**Design for the novice.** The signalling and map benefits are surest at low prior knowledge. For high prior
knowledge the signalling estimates conflict: *r* = −0.08 (k = 4) in Richter et al. (2016), and a positive effect in
Schneider et al. (2018). Provided maps gave −0.13 (k = 5) for high-ability learners (Nesbit & Adesope 2006). The figure sits below
the text, so an expert can skip it.

**A figure must represent, organise or interpret the claim.** Representational, organisational and
interpretational pictures each gain about *g* = 0.24 to 0.63 across three independent meta-analyses. Decorative
pictures gain nothing. That comes from Levin et al. (1987) as summarised by Mayer (2014), and the later
meta-analyses had too few decorative studies to estimate it. The seductive-details evidence in `evidence.md` covers
the same ground.

## 5. What not to claim

- **"Some readers are visual learners."** Pashler et al. (2008) found almost no evidence for matching instruction
  to a learning style.
- **"A picture adds a second memory code, so any picture helps."** Decorative pictures gain nothing. In school
  experiments, gains measured two weeks or more later were *g* = 0 (Banks et al. 2026, 7 studies), so claim no
  lasting effect.
- **"Animate a process."** Not when the words are written and the reader sets the pace (Berney & Bétrancourt
  2016).
- **"Realistic images teach better."** No meta-analysis supports it, and single studies favour schematic ones.
- **"Never use a pie chart."** Pies are adequate for one share of a whole and poor for comparing slices.
- **"Graphs beat tables."** Tables serve exact values and graphs serve patterns.
- **"Position beats angle for everyone."** It holds on average only (Davis et al. 2024).
- **"Concept maps give *g* ≈ 0.8."** That figure is for maps the learner constructs. A provided map gains 0.29 to
  0.43, and the North American estimate is 0.25 (Schroeder et al. 2018).
- **Mayer's own-lab signalling *d* = 0.52.** The independent estimates run from 0.27 to 0.38.
- **The per-function effect sizes in Levin et al. (1987).** They were not confirmed from the source. Use the
  later meta-analyses.

## 6. Sources

Quantitative:
- Cleveland, W. S., & McGill, R. (1984). Graphical perception. *JASA, 79*(387), 531–554. `10.1080/01621459.1984.10478080`. Only the abstract was read. The full ten-level ordering usually quoted from it was not confirmed.
- Cleveland, W. S., & McGill, R. (1986). An experiment in graphical perception. *IJMMS, 25*(5), 491–500. `10.1016/S0020-7373(86)80019-0`. 127 subjects, 210 judgments each.
- Heer, J., & Bostock, M. (2010). Crowdsourcing graphical perception. *CHI 2010*, 203–212. `10.1145/1753326.1753357`.
- Talbot, J., Setlur, V., & Anand, A. (2014). Four experiments on the perception of bar charts. *IEEE TVCG, 20*(12). `10.1109/TVCG.2014.2346320`.
- Davis, R., et al. (2024). The risks of ranking. *IEEE TVCG, 30*(3), 1756–1771. `10.1109/TVCG.2022.3226463`. Its abstract misstates the ranking as "position > area > angle". Do not copy it.
- Simkin, D., & Hastie, R. (1987). *JASA, 82*(398), 454–465. `10.1080/01621459.1987.10478448`.
- Spence, I., & Lewandowsky, S. (1991). Displaying proportions and percentages. *Applied Cognitive Psychology, 5*(1), 61–77. `10.1002/acp.2350050106`.
- Vessey, I. (1991). Cognitive fit. *Decision Sciences, 22*(2), 219–240. `10.1111/j.1540-5915.1991.tb00344.x`. A theory paper, not a meta-analysis.
- Hwang, M. I., & Wu, B. J. P. (1990). *ACM SIGMIS Database, 21*(2–3), 11–20. `10.1145/109022.109023`. Only the abstract was read.
- Ali, N., & Peebles, D. (2013). *Human Factors, 55*(1), 183–203. `10.1177/0018720812452592`.
- Newman, G. E., & Scholl, B. J. (2012). The within-the-bar bias. *Psychonomic Bulletin & Review, 19*(4), 601–607. `10.3758/s13423-012-0247-5`.
- Correll, M., & Gleicher, M. (2014). Error bars considered harmful. *IEEE TVCG, 20*(12), 2142–2151. `10.1109/TVCG.2014.2346298`.
- Pentoney, C. S., & Berger, D. E. (2016). *The American Statistician, 70*(2), 215–220. `10.1080/00031305.2016.1141706`.
- Okan, Y., et al. (2018). *QJEP, 71*(12), 2506–2519. `10.1177/1747021817744546`.
- Kerns, S. H., & Wilmer, J. B. (2021). *Journal of Vision, 21*(12):17. `10.1167/jov.21.12.17`. It finds that about one reader in five makes a categorical bar-tip error.
- Belia, S., et al. (2005). Researchers misunderstand confidence intervals and standard error bars. *Psychological Methods, 10*(4), 389–396. `10.1037/1082-989X.10.4.389`.
- Hofman, J. M., Goldstein, D. G., & Hullman, J. (2020). *CHI 2020*. `10.1145/3313831.3376454`.
- Zhang, S., et al. (2023). *PNAS, 120*(33), e2302491120. `10.1073/pnas.2302491120`.
- Fernandes, M., et al. (2018). Quantile dotplots. *CHI 2018*. `10.1145/3173574.3173718`.
- Fitzgerald, K. G., & Tipton, E. (2022). *JREE, 15*(4), 848–875. `10.1080/19345747.2022.2031366`.
- Fitzgerald, K. G., et al. (2025). *Research Synthesis Methods, 16*(2), 364–382. `10.1017/rsm.2025.4`.

Qualitative:
- Levin, J. R., Anglin, G. J., & Carney, R. N. (1987). On empirically validating functions of pictures in prose. In *The psychology of illustration, Vol. 1*, 51–85. `10.1007/978-1-4612-4674-9_2`. Not reached. The per-function numbers are not confirmed.
- Banks, B., Curran, J., Hall, R., Sims, S., & Meliss, S. (2026). *When and how to use visuals effectively: a meta-analysis of dual coding in the classroom.* Ambition Institute. Pre-registered (OSF cn6qf). k = 56 randomised school experiments. Overall *g* = 0.47 [0.26, 0.68], bias-adjusted 0.31. It is an institute report, and its peer review is not confirmed.
- Hu, L., Chen, G., Li, P., & Huang, J. (2021). Multimedia effect in problem solving. *Educational Psychology Review, 33*(4), 1717–1747. `10.1007/s10648-021-09610-z`.
- Guo, D., Zhang, S., Wright, K. L., & McTigue, E. M. (2020). Do you get the picture? *AERA Open, 6*(1). `10.1177/2332858420901696`. k = 39, overall *g* = 0.39 [0.26, 0.51].
- Richter, J., Scheiter, K., & Eitel, A. (2016). Signaling text-picture relations. *Educational Research Review, 17*, 19–36. `10.1016/j.edurev.2015.12.003`. *r* = .17 [.11, .22], about *d* = 0.35.
- Schneider, S., Beege, M., Nebel, S., & Rey, G. D. (2018). *Educational Research Review, 23*, 1–24. `10.1016/j.edurev.2017.11.001`. Read through a secondary review. The CIs are not confirmed.
- Alpizar, D., Adesope, O. O., & Wong, R. M. (2020). *ETR&D, 68*(5), 2095–2119. `10.1007/s11423-020-09748-7`. *d* = 0.38.
- Xie, H., et al. (2017). *PLoS ONE, 12*(8), e0183884. `10.1371/journal.pone.0183884`. Retention 0.27, transfer 0.34.
- Nesbit, J. C., & Adesope, O. O. (2006). Learning with concept and knowledge maps. *Review of Educational Research, 76*(3), 413–448. `10.3102/00346543076003413`.
- Schroeder, N. L., Nesbit, J. C., Anguiano, C. J., & Adesope, O. O. (2018). *Educational Psychology Review, 30*(2), 431–455. `10.1007/s10648-017-9403-9`. An update from the same team.
- Berney, S., & Bétrancourt, M. (2016). Does animation enhance learning? *Computers & Education, 101*, 150–167. `10.1016/j.compedu.2016.06.005`.
- Höffler, T. N., & Leutner, D. (2007). *Learning and Instruction, 17*(6), 722–738. `10.1016/j.learninstruc.2007.09.013`. Its large procedural-motor effect did not replicate in Berney & Bétrancourt.
- Rexigel, E., Kuhn, J., Becker, S., & Malone, S. (2024). *Educational Psychology Review, 36*(4). `10.1007/s10648-024-09958-y`.
- Butcher, K. R. (2006). *Journal of Educational Psychology, 98*(1), 182–197. `10.1037/0022-0663.98.1.182`. A single study.
- Menendez, D., Rosengren, K. S., & Alibali, M. W. (2020). *Applied Cognitive Psychology*. `10.1002/acp.3698`. A single study.
- Tetzlaff, L., et al. (2025). Expertise reversal meta-analysis. *Learning and Instruction, 98*, 102142. `10.1016/j.learninstruc.2025.102142`. Novices *d* = 0.505, experts −0.428. Visuals were not tested as a separate moderator.
- Pashler, H., McDaniel, M., Rohrer, D., & Bjork, R. (2008). Learning styles. *PSPI, 9*(3), 105–119. `10.1111/j.1539-6053.2009.01038.x`.
