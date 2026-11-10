---
type: llm
focus: trace
weight: 1
---

Running `scripts/prose-audit.py` on the final artifact passes all three gates: at most 6 dash uses per 1000 words, no two consecutive sentences with dashes, and at most 2 bold spans per 1000 words inside sentences. The run reports these numbers to the user.
