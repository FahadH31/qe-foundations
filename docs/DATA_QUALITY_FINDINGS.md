# Data-quality findings (expected-findings template)

## 1. Prediction round (do this BEFORE you run Part E, 5 minutes)

Open `sql/seed.sql` (or run `SELECT * FROM builds;` and the other three tables with `python lab_runner.py`) and read the data like a tester.
List up to 8 problems you can already SEE, and which check category you expect to catch each one.

| # | What I see (table, row, column) | Category I expect (reconciliation / missing rows / uniqueness / completeness / referential / validity / business rule) |
|---|---|---|
| 1 | builds row 1: reported_total 8 but passed(5) + failed(1) = 6 | reconciliation |
| 2 | test_runs row 1: result 'PASSED' in uppercase | validity |
| 3 | test_runs row 2: duration_sec is -5 | validity |
| 4 | test_runs row 3: duration_sec is 86400 (24 hours) | validity |
| 5 | test_runs row 5: tester is NULL | completeness |
| 6 | test_runs row 6: tester is whitespace string | completeness |
| 7 | test_runs row 39: case_id 99 does not exist | referential |
| 8 | defects row 4: severity 'urgent' not in allowed list | validity |

After Part E: how many of your predictions did the suite confirm? Which defects did you NOT see by eye? All 8 predictions were confirmed by the suite. Defects not easily seen by eye included duplicate runs with identical build and case ids (runs 44 and 45), subtle defect dates where closed date came before opened date (defect 6), and defects pointing to passing test runs (defect 13).

## 2. Findings per check (fill in after `python lab_runner.py --checks sql/part_e_checks.sql --show`)

Severity: High = wrong results or lost data reach users, Medium = reports are wrong in places, Low = cosmetic / hygiene.
Draft bug title: one line a developer could act on (what is wrong, where, how many).

| Check | Category | Violations | Offending ids | Severity | Suspected root cause | Draft bug title |
|---|---|---|---|---|---|---|
| E-01 | reconciliation | 2 | 4, 6 | High | Manual summary entry or dropped CI webhook | Builds 4 and 6 reported totals do not match real run counts |
| E-02 | reconciliation | 2 | 1, 6 | High | Math mismatch or untested builds | Builds 1 and 6 report incorrect pass/fail numbers |
| E-03 | missing rows | 1 | 6 | Medium | CI job triggered build record but ran no tests | Build 6 has 0 test executions recorded |
| E-04 | missing rows | 2 | 13, 14 | Medium | Profile module tests never scheduled in any run | Active test cases 13 and 14 were never executed |
| E-05 | uniqueness | 2 | 44, 45 | High | Test retry logic inserted duplicate execution records | Duplicate test runs 44 and 45 recorded for existing build/case pairs |
| E-06 | uniqueness | 1 | 15 | Low | Copy-paste error when authoring tests | Duplicate test case title 'Add item to cart' created as case 15 |
| E-07 | completeness | 2 | 10, 11 | Low | Missing validation on case creation form | Test cases 10 and 11 have missing or invalid priority values |
| E-08 | completeness | 5 | 4, 5, 6, 8, 41 | High | Test runner crashed or omitted telemetry fields | Test runs 4, 5, 6, 8, 41 are missing required execution data |
| E-09 | completeness + validity | 2 | 3, 4 | Medium | Defect tracker allowed custom text or NULL severity | Defects 3 and 4 have missing or unrecognised severity ratings |
| E-10 | referential | 2 | 39, 40 | High | Test case deleted while runs still reference it | Test runs 39 and 40 reference nonexistent test cases 99 and 98 |
| E-11 | referential | 1 | 42 | High | Test run logged against deleted or nonexistent build 9 | Test run 42 references nonexistent build 9 |
| E-12 | referential | 1 | 14 | High | Defect references deleted run 500 | Defect 14 references nonexistent test run 500 |
| E-13 | referential | 1 | 15 | High | Defect references nonexistent test case 77 | Defect 15 references nonexistent test case 77 |
| E-14 | validity | 1 | 1 | Low | Case-sensitivity bug in test harness reporting | Test run 1 has invalid result 'PASSED' instead of 'pass' |
| E-15 | validity | 2 | 2, 3 | Medium | Clock skew and unhandled timeout in test harness | Test runs 2 and 3 contain out-of-bounds duration values (-5s and 86400s) |
| E-16 | business rule | 1 | 5 | Medium | System clock desync between build agent and tester | Test run 5 recorded before build creation date |
| E-17 | business rule | 2 | 7, 11 | High | Tester did not file bug after test failure | Failed test runs 7 and 11 have no defects logged |
| E-18 | business rule | 1 | 13 | Medium | Defect mistakenly linked to passing verification run | Defect 13 logged against a passing test run |
| E-19 | cross-table consistency | 1 | 5 | Medium | Mismatched foreign keys during manual bug filing | Defect 5 case_id does not match the case_id of referenced run |
| E-20 | business rule | 3 | 6, 7, 8 | Medium | Workflow transition allowed invalid state combinations | Defects 6, 7, 8 have conflicting status and opened/closed dates |

## 3. Questions the data asked you (one or two sentences each)

1. **A1:** PRAGMA foreign_key_check listed 5 violations. Which of E-10 .. E-13 are they, and why did the database accept those rows in the first place? They correspond to E-10 (2 orphan case_ids in test_runs), E-11 (1 orphan build_id in test_runs), E-12 (1 orphan run_id in defects), and E-13 (1 orphan case_id in defects). The database accepted them because SQLite disables foreign key enforcement by default unless enabled via PRAGMA foreign_keys = ON.
2. **B4 vs E-10:** B4 returned 3 runs, E-10 only 2. Which run is the difference and in which check does it belong? Why? Run 41 is the difference (its case_id is NULL). It belongs in completeness check E-08 because missing data is a completeness defect, whereas E-10 specifically tests referential integrity for non-null keys pointing to nonexistent parents.
3. **C2:** Why did the NOT IN query return zero rows? Because test_runs contains a row with case_id IS NULL; under SQL three-valued logic, x NOT IN (..., NULL) evaluates to UNKNOWN rather than TRUE, so no rows satisfy the condition.
4. **B2 vs E-04:** B2 returned 3 cases, E-04 only 2. Which case is excluded and why is that correct? Case 12 is excluded because its status is 'retired'; retired test cases are intentionally no longer executed, so missing runs for them is expected.
5. **C4a vs C4b:** why does one out-of-range duration change which runs look "slow"? Run 3 has an extreme duration of 86,400s (24 hours), which heavily distorts the unfiltered average up to ~2,400s so only run 3 appears slow; filtering to valid durations (1-3600s) restores a realistic baseline (~400s), identifying 23 slow runs.

## 4. Top 3 risks for the release (the message you would give the team lead)

1. Unreliable release metrics: Build summaries report numbers that differ from actual test runs, and multiple failed runs have no defects logged, giving release managers a false sense of quality.
2. Data integrity and referential breaks: Test runs and defects point to nonexistent builds and test cases because foreign key enforcement was disabled, leaving orphaned records that compromise tracking.
3. Outlier and invalid execution data: Out-of-bounds durations heavily distort performance averages, and inconsistent defect statuses make it impossible to tell whether known bugs are genuinely open or resolved.
