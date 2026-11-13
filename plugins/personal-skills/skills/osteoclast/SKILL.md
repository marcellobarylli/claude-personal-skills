---
name: osteoclast
description: Find overengineered code, remove what carries no load, and prove with tests that behavior survived. Use when the user says code is overengineered, bloated, too layered, too abstract or too defensive, asks to simplify, slim down, strip or de-bloat code (especially code an agent wrote), asks "could this be simpler" or "what can go", or wants a deletion pass over a branch diff, a feature or a whole repo. Also offer it when an agentic build has landed far more code than the task needed. Not for style-only refactors, performance work or bug fixes.
---

# Osteoclast

**Goal:** remove code that carries no load, and show that behavior on reachable inputs did not change. (An
osteoclast is the cell that resorbs bone where no stress passes through it.)

Success is fewer lines and fewer concepts with the same behavior, shown by tests that existed before the first cut.
It is not a nicer style or a better abstraction.

A cut is a **deletion** or a **collapse**: replacing an indirection with the direct code it stood for (a one-method
class becomes a function, a registry becomes a dict, a strategy chain becomes three `if`s in order). A collapse
counts only when the result is shorter and reads more directly. Anything that adds a concept is not a cut.

Three phases: **Survey → Lock → Resorb.** Nothing is edited before the user has accepted findings.

## Scope

The user sets it; say which one you are using in the first line of the findings.

| Scope | What is in it | Use when |
| --- | --- | --- |
| **diff** | `git diff <base>...HEAD` plus uncommitted changes | a branch or a recent agent session; the default when the branch differs from its base |
| **feature** | the named paths, plus code only they use | "simplify the export module" |
| **repo** | everything tracked | "this whole thing is a mess"; survey largest directories first and cut in batches |

If the request does not settle it and there is no branch diff, ask. Scope limits what may be **cut**. Evidence is
gathered everywhere: a caller outside the scope still counts as a caller.

## 1. Survey (read-only)

1. **Find what the code is for.** Read the request it was built from: the user's words, the plan, the issue, the PR
   description, the README. That requirement defines "load". Code that serves nothing in it is a candidate.
2. **Run the existing gate** (tests, plus type check, lint or build if the project has them) and record the command
   and result. If it is red or cannot run, say so before anything else: without a green baseline nothing can be
   cut, only reported.
3. **Collect candidates** with `references/patterns.md`, which lists each pattern with the check that settles it.
4. **Run the check for each candidate.** Grep the callers, the implementers, who sets the option, who can reach the
   branch. A finding without evidence is an opinion: drop it or go get the evidence. Check side effects as well as
   purpose: what the code rejects, raises or reorders along the way can be load even when its purpose is not (a
   cache nobody needs may still be the only thing rejecting an unhashable input).
5. **Compare with the direct version.** Picture what someone would write from the request alone. The findings
   should close most of that gap. If a layer with one user would survive every finding, a collapse is missing.
6. **Tier each finding:**
   - **A, behavior-preserving.** No reachable input gets a different result: dead code, an option nobody sets, a
     single-use indirection, a check that an earlier check already guarantees.
   - **B, contract-narrowing.** Something a caller or user could rely on goes away: a guard on a state you believe
     is impossible, a fallback, a feature nobody asked for but that works, an environment or config override, a
     public symbol with no caller in this repo, a test whose subject is being deleted.
   - **Keep.** It looks like bloat and carries load. Name the non-obvious ones so the user sees they were checked.

**Reachable** means reachable from the entry points real users have: the CLI, the request handler, the documented
API. In an application, an internal function called with arguments no caller in the repo passes is not reachable.
In a library, every exported symbol is an entry point. Say which boundary you used when it decides a tier.

Treat these as load-bearing unless the evidence is strong, and never as tier A: validation where untrusted data
enters (user input, network, files, environment), error handling and retries around I/O, security checks,
concurrency control, a library's public API, and anything whose comment or commit message gives a reason (an
incident, a bug number).

Present the findings sorted by lines removed, then stop:

```
Scope: diff main...HEAD (14 files, 1,240 source lines)
Gate: pytest -q → 212 passed (38 s)

| # | Tier | Where | What | Evidence | Lines | Tests |
|---|------|-------|------|----------|-------|-------|
| 1 | A | cache.py:10-88 | CacheBackend ABC with one implementer | grep: only MemoryCache subclasses it; no plugin hook | −64 | covered |
| 2 | B | client.py:40-61 | fallback to v1 endpoint | request never mentions v1; no test; reachable if v2 returns 404 | −22 | needs pin |

Kept: retry in fetch_page (network I/O), path check in serve_file (untrusted input)
If all accepted: −N source lines, −K files
```

"Tests" says whether the behavior around the cut is already exercised: `covered`, `needs pin` or `cannot pin`.

Ask which findings to apply. Tier B needs an explicit yes per finding. **If the user approved in advance or is not
there to ask, apply tier A only and leave tier B listed in the report.**

## 2. Lock

For each accepted finding marked `needs pin`, write characterization tests before touching the code:

- Pin what the code does now, through an entry point that will survive the cut. A test that imports the wrapper
  pins the wrapper.
- Pin what the accepted cuts can disturb, a few cases per behavior. The pins are a gate, not a new test suite.
- Get expected values by running the code, not by reasoning about it. A pin records current behavior, quirks
  included; a suspected bug goes in the report, not in the pin.
- Check that each pin can fail: break the behavior it covers, see it go red, restore.
- Commit the pins on their own (`osteoclast: pin behavior before cuts`).

From this commit on the tests are frozen. The only test changes allowed are removing tests for an accepted tier B
cut, and before removing a test, make sure the behavior it checked is still exercised through a surviving entry
point (move the cases if it is not).

A finding marked `cannot pin` (code that cannot be run here, a dependency that is missing) is reported, not cut.

## 3. Resorb

Work in git so every cut can be undone; if the directory is not a repository, ask before creating one. Take one
finding at a time, largest first unless one depends on another.

1. **Cut.** Delete or collapse, nothing else. Follow the dependents out: imports, config keys, docs, a dependency
   nothing uses any more.
2. **Run the full gate.** Where it is cheap, also run old against new: check the starting commit out into a
   temporary worktree, feed both versions a spread of inputs through the entry point (malformed ones included) and
   compare outputs, errors and exit codes. It catches what the pins miss. The script is throwaway; do not commit it.
3. **Green:** commit it alone (`osteoclast: remove <what> (−N)`).
   **Red:** if the cut was incomplete (a leftover import or reference), finish it. If a behavior test fails,
   revert the cut and record the finding as reverted with the failing test's name. Do not fix forward: a failing
   test is evidence the code carried load, and a repair adds code.

Never edit a frozen test to make it pass. Do not push or open a pull request unless asked.

## Staying small

This skill's own failure mode is the one it treats: a refactoring agent that grows the code.

- Each cut must reduce source lines. No new abstractions, helpers or files; the pins are the only additions.
- Do not stop at deletion when a layer with one user is left standing: collapse it. Do not go past collapse into
  redesign.
- Leave lines that are not being cut alone: no renames, reformatting or reordering.
- A bug noticed on the way is reported, not fixed. Fixing it changes behavior and the gate would hide that.
- Stop when the accepted findings are done. Do not start a second survey unless the user asks.

## Report

```
Osteoclast: <scope>
Source: 1,240 → 870 lines (−370, −30%), 14 → 11 files. Tests: +9 pins.
Gate: pytest -q → 221 passed before the first cut and after the last
Cut:        #1 CacheBackend ABC (−64), #3 …
Reverted:   #4 retry wrapper: test_fetch_retries_on_503 failed
Not applied: #2 fallback to v1 endpoint (tier B, needs your yes), #6 declined
Tests removed: none
Left for you: suspected off-by-one in paginate() (pinned as is)
```

Count source and test lines separately so the pins do not hide the deletion
(`git diff --shortstat <start>..HEAD -- <source paths>`).

## Notes

- If the project logs rounds with `round-log`, record the findings table and the user's decisions as events.
- For a plan that has not been built yet, `codex-critique` already asks for Cuts; this skill is for code that
  exists.
