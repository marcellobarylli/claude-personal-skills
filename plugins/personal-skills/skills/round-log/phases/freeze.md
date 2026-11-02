# Freeze: move the buffer, write the pre-run record

Do this first after ExitPlanMode. Without plan mode, start at step 3.

1. **Move the buffer** from the plan file into `docs/rounds/NNN/trail/`:
   - journal rows → `journal.md` (create it with the header from SKILL.md; keep the rows' Occurred times);
   - Interview → `interview.md`;
   - each `plan-vK as sent` block → `plan-vK.md`. Check that its sha256 equals the one in the dispatch row; if not,
     add a row saying so;
   - each critique block → `critique-K.md`.

   Skip any file that already exists (an earlier move); add only rows whose `#` is not in the journal yet.
2. **Leave the plan file as it is.** It is outside the repo and is not the record.
3. **Write `architecture.md`.** Header, then the pre-run sections:

   ```
   # Round NNN architecture

   **Conversational round, recorded before the run.** Designed on <date> with the owner, not through the round
   pipeline. Sections marked *pre-run* must not be edited after the commit that holds them. Changes go into dated
   Amendments; results go into the dated Outcome section, added later. The full record (interview, drafts, raw
   critiques, timeline) is in `trail/`; it is not needed to implement this round.

   - **Design source:** <main-stream records this round depends on, with links>
   - **Findings:** to be written after the run (`findings.md`).
   - **Artifact:** <planned artifact directories>
   ```

   Pre-run sections, each heading ending in `(pre-run)`: Goal, Owner decisions (each with Offered / Chosen where
   options were offered, linking `trail/interview.md`), Claim boundary, Deferred, Design, Second opinion (from
   plan.md), Tests.
4. **Add the round index row** to the project's status report, marked as the pre-run record.
5. **Commit** the round folder and the index row: `round NNN: pre-run record`. This commit is the freeze.
6. **Add a `freeze` row** to the journal. It is committed with the next change.
