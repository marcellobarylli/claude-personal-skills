# Close: outcome, findings, status

1. **`findings.md`** in the round folder, with the sections Question, Finding, Method, Results, Decision, Evidence,
   Claim boundary, Open items. Results that ran on a GPU name the GPU model, node(s) and driver. Evidence links
   receipts, snapshots and the trail items a claim rests on. Add an `outcome` row.
2. **`architecture.md`:** a dated `## Outcome (<YYYY-MM-DD>)` section (add "written <date>" if it differs) with what
   happened against the pre-run plan, linking `findings.md`.
3. **Status report:** a dated addendum, and the round index row completed (findings, artifacts, commits).
4. **Paper registration**, only if a result is registered: the ledgers the project's logging table names.
5. **`closed` row** in the journal.
6. **Run the project's check** (assembly: `python3 tools/round_log_check.py NNN`). Fix what it reports with new
   records, not by editing frozen sections or old rows. It is structural: it shows that links and dispositions exist,
   not that summaries are faithful.
7. **Commit:** `round NNN: findings, Outcome and status addendum`.
