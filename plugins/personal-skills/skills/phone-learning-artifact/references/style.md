# Prose style

Every sentence the reader sees follows this file. That covers claims, connecting prose, card fields, the
open-questions page and the report back to the user.

The rules come from one source: Van Savage and Pamela Yeh, "Novelist Cormac McCarthy's tips on how to write a
great science paper", *Nature* 574, 441–442 (2019), https://www.nature.com/articles/d41586-019-02918-5.
McCarthy edited papers at the Santa Fe Institute for two decades, and the column condenses his advice.

## Contents

1. [The models to imitate](#1-the-models-to-imitate)
2. [The rules](#2-the-rules)
3. [Habits that break them](#3-habits-that-break-them)
4. [Where the rules meet this skill](#4-where-the-rules-meet-this-skill)
5. [The prose audit](#5-the-prose-audit)

## 1. The models to imitate

The owner approved two external texts as the target voice. Only external, published prose counts as a
model. Do not treat your own rewrites as samples of the style, and do not add any here.

**A. The column itself.** It follows its own advice. Read it whole before writing a long artifact. Some
lines worth hearing:

> Limit each paragraph to a single message. A single sentence can be a paragraph.

> Impersonal, passive text doesn't fool anyone into thinking you're being objective.

> If you must talk about arbitrary colours of an abstract sphere, it's more gripping to speak of this sphere
> as a red balloon or a blue billiard ball.

Its 1,300 words use five dashes.

**B. Cormac McCarthy, "The Kekulé Problem"**, *Nautilus*, 17 April 2017,
https://nautil.us/the-kekul-problem-236574/. A long argument about the unconscious, made in plain sentences.
It states its claims flatly ("the unconscious is a machine for operating an animal") and grounds them in
concrete figures ("Habits of two million years duration are hard to break"). It closes on a run of short
questions that ends "Are you sure?"

What the two share is what to copy:
- The sentence makes the claim and stops.
- Each paragraph carries one idea.
- Emphasis is rare, so it lands when it comes.
- A question opens a thought rather than performing suspense.

## 2. The rules

Quoted lines are from the column.

**Cut.** "Is it possible to preserve my original message without that punctuation mark, that word, that
sentence, that paragraph or that section?" Apply this to every sentence before it ships.

**One thread.** Decide the theme and "two or three points you want every reader to remember". In this skill
that is the spine. A sentence that does not serve it goes.

**One message per paragraph.** A paragraph may open with a question and move to an idea, sometimes to an
answer. It may also leave the question open.

**Short, direct sentences.** "Minimize clauses, compound sentences and transition words — such as 'however'
or 'thus'." Two ideas get two sentences.

**Dashes mark the clause that matters most.** "Dashes should emphasize the clauses you consider most
important — without using bold or italics." A dash is a spotlight. If every sentence has one, nothing is lit.
- Parentheses "present clauses more quietly", so asides go there.
- A second idea gets a full stop.
- Semicolons are not "a crutch to join loosely linked ideas".

**Emphasis without markup.** The dash rule exists to replace bold and italics. Inside prose, stress comes
from word order and from putting the key word last. It does not come from `<b>` or `<em>`.

**Don't over-elaborate.** "Only use an adjective if it's relevant." "Your paper is not a dialogue with the
readers' potential questions, so don't go overboard anticipating them." "Don't say the same thing in three
different ways in any single section."

**Don't repeat ordinary words.** "Don't use the same word repeatedly — it's boring." This applies to ordinary
words only (see §4).

**Concrete language.** Use the number, the named method, the named failure. Avoid abstractions about
"the question", "the problem" or "what breaks".

**Tone.** Use a personal voice ("we"), the occasional contraction and a real question. Never use exclamation
marks. Words like "surprisingly" appear once or twice per artifact at most.

**Read it aloud.** "Commas denote a pause in speaking." A sentence you would not say aloud to a colleague is
not finished.

## 3. Habits that break them

These come from earlier artifacts the owner found tiring. Each one is common in generated prose. The fix is
named in words. There is no rewritten sentence to copy, because the models are in §1.

**The hinge dash.** "Agents already exchange artifacts — and nothing says whether an artifact can verify
itself."
- The dash joins two loosely linked ideas. That is the job the column forbids semicolons, and the dash only
  adds suspense to it.
- "Nothing says whether it can verify itself" is vaguer than the evidence under it. That evidence says the
  protocols record nothing about how well an artifact was checked.
- Fix: two sentences, and the concrete claim.

**The intensifier, the staged imperative and the tagalong clause.** "Those preconditions are the whole
question. Name them, and you can ask which domains satisfy them — and what breaks in the ones that do not."
- "The whole question" promotes the sentence without adding content.
- "Name them, and you can…" stages a move the previous paragraph already made.
- The dash clause answers a question nobody asked. That is the column's "dialogue with the readers' potential
  questions", and it fails the cut test.
- Fix: ask the next question plainly, or state the next claim.

**The stacked transitions and the withheld point.** "But the reason to borrow a domain is not the one
everybody expects — so it has to be stated precisely, or the comparison proves nothing."
- "But… so… or…" is three transition words in one compound sentence.
- The sentence talks about a statement instead of making it. It says the reason must be stated precisely
  and then never states it.
- "Everybody expects" is a straw man, and "not the one…" withholds the point to build suspense.
- Fix: state the reason.

**The reflexive contrast.** "Adapted, not inherited." "Deployed, not hypothetical." "The gap is not
narrower elsewhere. It is measured elsewhere."
- A contrast earns its place when it corrects a claim someone actually made, and the reader needs to know
  which one.
- As a rhythm it is a tic. Drop the "not" half unless the rejected reading is on the page or in the corpus.

**Emphasis everywhere.** Bold, italics and dashes in the same paragraph. Each device is a claim that this
part matters more than the rest. Three per paragraph cancel out.

**Saying it twice.** "The stated preconditions are explicit." "Stated" and "explicit" make the same claim.
Keep one.

**Talking about the text.** "It is worth noting", "importantly", "the key point is", "here is the thing",
"this matters because". Cut the frame and keep the point.

## 4. Where the rules meet this skill

**Defined terms repeat.** The anchor vocabulary (grades, levels, a domain's own labels) and every technical
term keep one name throughout. Renaming a term for variety breaks the distinction the artifact exists to
protect. The no-repetition rule covers ordinary words.

**Logical connectives stay. Decorative ones go.** The evidence in `evidence.md` favours high-cohesion text
for skilled readers. "Because", "so" and "therefore" carry an inference, so they stay when the inference is
real. "However", "indeed", "moreover", "crucially" and a sentence-initial "But" mostly carry tone. Minimise,
as the column says. This is not a ban.

**Questions are welcome in prose, not as prompts.** A rhetorical question that opens a paragraph or closes a
spine node is the column's advice. A question the reader is asked to answer is a pretesting or
self-explanation prompt, which the skill refuses.

**Labels are not prose.** Card field names, tab names, the ◐ and ○ markers and table headers may be bold.
The emphasis rule applies to sentences.

**The `forces` field is one plain sentence.** It names the next question or the next claim. It does not
dramatise, promise a reveal or comment on its own importance. Most of the habits in §3 were found in this
field.

## 5. The prose audit

`scripts/prose-audit.py <artifact.html>` counts what can be counted:
- dash rate;
- dashes in consecutive sentences;
- bold and italics inside sentences;
- reflexive "not X, Y" contrasts;
- stacked transitions;
- intensifiers and talk about the text;
- long sentences;
- semicolons and exclamation marks.

It is a floor, not a judge. A clean run means these patterns are rare. It does not mean the prose is good.
After it passes, read every screen aloud once and apply the cut test to each sentence.

Calibration, 2026-11-10:
- **The column.** It passes all three gates at 4.5 dash uses per 1000 words. Its warnings are one deliberate
  contrast and two sentences of 40 and 42 words. Warnings mark places to judge, and the column shows that
  good prose triggers some.
- **The earlier artifact that produced the §3 examples.** It fails all three gates:
  - 12.2 dash uses per 1000 words;
  - six consecutive-dash pairs;
  - 16.5 bold spans per 1000 words.
