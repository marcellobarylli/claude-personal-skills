# Background reading: automated claim verification

*SYNTHETIC TEST MATERIAL. Authors, venues, identifiers and findings below are invented for
evaluating a skill. Nothing here should be cited.*

*Compiled 2026-03-02. Revised 2026-03-19 after an internal review (14 findings, all accepted —
see Review table).*

---

## 0.5 The axis this reading is organised around

Everything below is read against one distinction, and the rest of the document depends on
keeping its levels apart.

| Level | What it establishes | Determinism | Cost |
| --- | --- | --- | --- |
| **E0 — surface check** | the claim is well-formed and has a locatable subject | deterministic, binary | ~free |
| **E1 — corpus-attested** | the claim matches a retrievable source passage | deterministic as a retrieval, but a **proxy** for truth | seconds |
| **E2 — adjudicated** | a qualified human assessed the claim against the world | slow, contested, partial | days–weeks |

**The load-bearing point: E1 is not a weak E2.** A retrieval can be perfectly reproducible and
still match a passage that is itself wrong, outdated, or quoting someone else. Reproducibility
is a property of the retrieval; truth is a property of the world. Conflating the two was the
most common error in the first draft of this document.

Where E0, E1 and E2 coincide — as they roughly do for arithmetic claims — the whole
retrieve-then-verify apparatus works. The open question is what verification looks like when
they come apart.

---

## A. Retrieval architectures

### A1. Dense retrieval and its ceiling

**Okonkwo & Vásquez (2024), "Dense passage retrieval under distribution shift."**
*Proceedings of SIGIR 2024.* Reports that dense retrievers lose 18–24 points of recall@20 when
the claim distribution shifts away from the training corpus, and that the loss is concentrated
in claims containing named entities absent from training.

*Do not cite this for a general claim that dense retrieval is brittle.* The result is specific
to entity-bearing claims under distribution shift; on in-distribution claims the same systems
were at parity with sparse baselines.

### A2. Sparse and hybrid

**Lindqvist, Abara & Moreau (2025), "Hybrid retrieval for verification pipelines."**
*TACL 13, 221–240.* Hybrid sparse-dense retrieval recovers most of the A1 gap. The paper's own
caution: the gain is measured at recall@20, and downstream verification accuracy improved by
only 3 points, because the verifier could not exploit the additional recall.

*An earlier draft of this document reported the 3-point figure as the retrieval gain. It is the
downstream gain; the retrieval gain was 16 points.*

### A3. Retrieval-free approaches

**Sato (2025), "Parametric verification without retrieval."** *arXiv (synthetic) 2502.11109.*
Argues model parameters already encode enough to adjudicate common claims. Reports 71% accuracy
on a closed-world benchmark.

*Do not cite for open-world performance.* The benchmark is closed-world by construction, and
the authors say so in §5.

---

## B. Verifier design

### B1. Natural-language inference verifiers

**Brandt & Oyelaran (2023), "NLI models as claim verifiers."** *EMNLP 2023.* The standard
approach: treat claim and retrieved passage as hypothesis and premise. Clean E1 instrument.

**Important:** the frequently-quoted "92% accuracy" is on the *entailment* subtask with gold
passages supplied. End-to-end, with retrieved passages, the same system reaches 64%.

### B2. Decomposition

**Ferreira, Naidoo & Kaur (2026), "Atomic decomposition for verification."** *ACL 2026.*
Decomposes a compound claim into atomic sub-claims and verifies each. Reports a 9-point gain on
compound claims, and explicitly **no** gain on atomic ones.

*The author order was given as Naidoo, Ferreira, Kaur in an earlier draft. It is Ferreira,
Naidoo, Kaur.*

### B3. Calibration

**Whitfield (2025), "Calibrated abstention in claim verification."** *NeurIPS 2025.* Shows a
verifier that abstains below a confidence threshold raises precision substantially. The
abstention rate at the recommended threshold is 38%, which the paper reports but which
secondary coverage routinely omits.

---

## C. Evaluation

### C1. Benchmarks

**The VERITAS benchmark (2024).** 40k claims with E2 adjudication. The dominant benchmark.
Known limitation stated by its authors: claims were sampled from already-fact-checked corpora,
so the distribution over-represents claims someone thought worth checking.

**Durand & Pham (2026), "What VERITAS measures."** *Synthetic preprint.* Audits the benchmark
and finds 11% of gold labels are contested on re-adjudication. *This is a result about label
reliability, not about system performance — do not use it to discount reported accuracies
directly.*

### C2. Agreement is not accuracy

**Osei, Lindqvist & Tanaka (2025), "Concordance among verification systems."** Finds high
inter-system agreement, and shows agreement does not predict correctness: concordant systems
share retrieval failures. *Cite for the agreement-accuracy distinction only; the paper proposes
no readiness test, and an earlier draft of this document claimed it did.*

---

## D. Deployment and oversight

### D1. Where the loop closed

**Marchetti et al. (2026), "A deployed verification pipeline at scale."** *Synthetic industry
report.* Describes 14 months of operation with human adjudication on a sampled 5%. Reports
end-to-end precision of 0.81 at 22% coverage.

*This document has not consulted the full report.* The figures come from the executive summary
and a conference talk. Pull the full text before any of this becomes load-bearing.

### D2. Failure modes in deployment

**Nakamura & Weiss (2026).** Catalogues deployment failures, dominated by stale corpora rather
than model error — the retrieval index ages and E1 silently stops tracking E2.

---

## E. Synthesis

The transport problem is solved: verification verdicts already travel as structured annotations
in every pipeline surveyed. What no pipeline specifies is **what the verdict should contain**
when evidence is graded, proxied and expensive — which level reached it, under what retrieval,
with what confidence, and what remains unadjudicated.

An earlier draft claimed this was an unoccupied position. It is not: Marchetti et al. already
emit a structured verdict with a confidence field. The narrower and better claim is that no
pipeline carries the *level* distinction of §0.5.

**Open questions.** (1) Can a verdict schema express the E0/E1/E2 distinction? (2) Can a
downstream consumer act on a graded verdict, including by declining? (3) How would anyone
estimate verifier quality without complete E2 labels? (4) Does stale-corpus drift have a
detectable signature before precision degrades?

---

## Review table

| # | Finding | Where it landed |
| --- | --- | --- |
| 1 | E1/E2 conflated throughout | §0.5 rewritten |
| 2 | A1 brittleness overgeneralised | §A1 caution added |
| 3 | A2's 3-point figure misreported as retrieval gain | §A2 |
| 4 | Sato closed-world scope dropped | §A3 |
| 5 | B1's 92% quoted without the gold-passage condition | §B1 |
| 6 | Ferreira author order wrong | §B2 |
| 7 | B3 abstention rate omitted | §B3 |
| 8 | Durand & Pham used to discount accuracies | §C1 |
| 9 | Osei readiness-test claim unsupported | §C2 |
| 10 | D1 cited as if full text read | §D1 caveat |
| 11 | "Unoccupied position" unsupported | §E |
| 12 | Author affiliation digression | cut as out of scope |
| 13 | B2 decomposition gain stated without the atomic-claim null | §B2 |
| 14 | VERITAS sampling bias unstated | §C1 |
