# Expected-defect checklist (fill in as you go)

<!--
PURPOSE: this is your "answer sheet" for the data. Writing the PREDICTION before you run a
query is the single best habit for catching false passes.
HOW: for each rule, (1) write what you EXPECT in the "Predicted" column BEFORE running the
query, (2) run it, (3) write the run_ids it actually returned in "Defects found (run_ids)"
(comma-separated, 4-digit ids), (4) note anything surprising. Do not delete rows.
check_exercise.py compares this table with what your queries return.
-->

| Rule | Defects found (run_ids) | Predicted (before running) | Notes / surprises |
|---|---|---|---|
| R-01 | 5006, 5019, 5025 | 3 rows | Catches NULL (5006), empty string '' (5019), and spaces-only '   ' (5025) |
| R-02 | 5011, 5022 | 2 rows | Catches missing '@' (5011) and missing domain dot (5022); ignores blanks caught by R-01 |
| R-03 | 5008, 5014, 5027, 5029 | 4 rows | Catches title case 'Passed' (5008), trailing space 'FAILED ' (5014), NULL (5027), and 'PASS' (5029) |
| R-04 | 5009, 5016 | 2 rows | Catches negative duration (5009) and NULL (5016); 0 ms is legal for SKIPPED runs |
| R-05 | 5030, 5023 | 2 |  |
| R-06 | 5013, 5020 | 2 | |
| R-07 | 5017, 5024, 5026 | 3 | |
| R-08 | 5014, 5018, 5028| 3 | |
| R-09 | 5010, 5015, 5035 | 3 | |
| R-10 | 5005, 5032 | 2 | |
| R-11 | 5003, 5012, 5033 | 3 | |
| R-12 | 5031, 5034, 5036, 5037 | 4 | |

## Decoys: rows that look odd but are LEGAL (we must not flag them)

<!-- List at least two run_ids and say why they are fine, e.g. "run 5xxx: SKIPPED with 0 ms -- skipped tests take no time." -->
* **Run 5040:** `retries = 3` -- `retries` between 0 and 3 inclusive is legal; 3 is just the exact permitted upper bound.
* **Run 5041:** `duration_ms = 600000` -- exactly 10 minutes (600,000 ms) is legal; R-05 only flags outliers strictly greater than 600,000 ms.


## Rows reported by more than one rule

<!-- Which run_ids appear in two or more rules? Is that OK? (Each rule must be testable on its own.) -->
* **Run 5014:** Reported by both **R-03** (invalid status value because `'FAILED '` has a trailing space) and **R-08** (untrimmed whitespace in `status` column).
* **Is that OK?** Yes. Each rule evaluates a separate validation dimension (Validity vs. Consistency / Formatting). Rules must remain independent so that defects are detected regardless of query order.


## Open questions for the product owner

<!-- Rules that are really business decisions (like "is a price of 0 allowed?" in the lesson). -->
1. is any email domain allowed?

