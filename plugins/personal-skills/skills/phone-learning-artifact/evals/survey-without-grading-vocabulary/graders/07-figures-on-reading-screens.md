---
type: llm
focus: trace
weight: 1
---

Every argument (spine) screen and every domain (cluster) screen carries one figure below its text, and at most two, the second showing a different relation. Each figure carries a brief (`rel`, `kind`, `form`) from `references/visuals.md`, alt text, a caption that says where to look, a credit, and a `from` label (evidence, drawn or illustration). The trace shows every brief written before any figure was retrieved, by a subagent or step that saw no candidate figure and was not prompted with an expert persona. Each figure shows its brief's relation in a form `visuals.md` supports: no mean drawn as a filled bar, no animation, no decoration. A screen without a figure carries a `nofig` reason (beginning "value:" when the claim is an exact number), and the run reports that reason to the user. No public illustration is presented as the cited evidence, a redrawn cited figure credits the original, and the figures are embedded so the file stays offline.
