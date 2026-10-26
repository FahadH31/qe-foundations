-- ============================================================================
-- Part E - The data-quality validation suite (time-box: 35 min)  /  Project 1 milestone
-- File format (the Python code in Part F reads exactly this format):
--   -- @CHECK <id> | <category> | <what must be true or what is wrong> | returns <table>.<pk column>
--   one SQL statement that returns the VIOLATING rows: first column = primary key of the offending row.
--   Zero rows returned = the check PASSES.  One or more rows = the check FAILS (those rows are the evidence).
-- Run:  python lab_runner.py --checks sql/part_e_checks.sql [--only E-05]
-- Three checks (E-14, E-16, E-20) are already written as worked examples. Write the other 17.
-- Placeholders look like:  SELECT NULL AS violating_id WHERE 1 = 0;   (they return 0 rows, so they "pass" silently:
-- a check you have not written is NOT a passing check. lab_runner.py reports them as TODO.)
-- Rules of the game:
--   * Return one row per OFFENDING ROW of the table named in "returns" (no duplicates, no extra columns needed).
--   * Return the primary key ONLY once per offending row (use DISTINCT or an OR condition, not a join that repeats rows).
--   * Every check must be a SELECT and must be safe to run any time.
-- ============================================================================

-- ---- Category: row counts and reconciliation -------------------------------

-- @CHECK E-01 | reconciliation | Build summary: reported_total equals the real number of runs | returns builds.build_id
-- (technique: Part D5)
SELECT b.build_id
FROM builds AS b
LEFT JOIN test_runs AS r ON b.build_id = r.build_id
GROUP BY b.build_id, b.reported_total
HAVING b.reported_total <> COUNT(r.run_id);

-- @CHECK E-02 | reconciliation | Build summary: reported_passed and reported_failed equal the real counts | returns builds.build_id
-- (technique: D5 + conditional aggregation from D1. Count results exactly 'pass' / 'fail'. A build with no runs has 0 of each.)
SELECT b.build_id
FROM builds AS b
LEFT JOIN test_runs AS r ON b.build_id = r.build_id
GROUP BY b.build_id, b.reported_passed, b.reported_failed
HAVING b.reported_passed <> COALESCE(SUM(CASE WHEN r.result = 'pass' THEN 1 ELSE 0 END), 0)
    OR b.reported_failed <> COALESCE(SUM(CASE WHEN r.result = 'fail' THEN 1 ELSE 0 END), 0);

-- @CHECK E-03 | missing rows | Every build has at least one test run | returns builds.build_id
-- (technique: B3)
SELECT b.build_id
FROM builds AS b
LEFT JOIN test_runs AS r ON b.build_id = r.build_id
WHERE r.run_id IS NULL;

-- @CHECK E-04 | missing rows | Every ACTIVE test case was executed at least once | returns test_cases.case_id
-- (technique: C3, plus a status filter. Retired cases are allowed to have no runs.)
SELECT c.case_id
FROM test_cases AS c
WHERE c.status = 'active'
  AND NOT EXISTS (
      SELECT 1
      FROM test_runs AS r
      WHERE r.case_id = c.case_id
  );

-- ---- Category: uniqueness ---------------------------------------------------

-- @CHECK E-05 | uniqueness | One run per (build, case): return the SURPLUS rows, keep the lowest run_id | returns test_runs.run_id
-- (technique: D2 as a subquery. Rows that are NOT the MIN(run_id) of their (build_id, case_id) group are surplus.)
SELECT r.run_id
FROM test_runs AS r
WHERE r.run_id NOT IN (
    SELECT MIN(run_id)
    FROM test_runs
    GROUP BY build_id, case_id
);

-- @CHECK E-06 | uniqueness | A test case title must be unique within its module: return surplus cases, keep the lowest case_id | returns test_cases.case_id
SELECT case_id
FROM test_cases
WHERE case_id NOT IN (
    SELECT MIN(case_id)
    FROM test_cases
    GROUP BY module, title
);

-- ---- Category: completeness -------------------------------------------------

-- @CHECK E-07 | completeness | Test case priority is present and one of P1, P2, P3 | returns test_cases.case_id
SELECT case_id
FROM test_cases
WHERE priority IS NULL OR priority NOT IN ('P1', 'P2', 'P3');

-- @CHECK E-08 | completeness | Every run has case_id, a non-blank tester, a result and a duration_sec | returns test_runs.run_id
-- (watch out: "missing" can be NULL or blank text. Four columns, one row per offending run.)
SELECT run_id
FROM test_runs
WHERE case_id IS NULL
   OR tester IS NULL OR TRIM(tester) = ''
   OR result IS NULL OR TRIM(result) = ''
   OR duration_sec IS NULL;

-- @CHECK E-09 | completeness + validity | Defect severity is present and one of low, medium, high, critical | returns defects.defect_id
SELECT defect_id
FROM defects
WHERE severity IS NULL OR severity NOT IN ('low', 'medium', 'high', 'critical');

-- ---- Category: referential integrity (what PRAGMA foreign_key_check would find, but readable) -------

-- @CHECK E-10 | referential | test_runs.case_id (when given) exists in test_cases | returns test_runs.run_id
-- (a NULL case_id is a COMPLETENESS problem (E-08), not an orphan. Do not report it here.)
SELECT r.run_id
FROM test_runs AS r
LEFT JOIN test_cases AS c ON c.case_id = r.case_id
WHERE r.case_id IS NOT NULL AND c.case_id IS NULL;

-- @CHECK E-11 | referential | test_runs.build_id exists in builds | returns test_runs.run_id
SELECT r.run_id
FROM test_runs AS r
LEFT JOIN builds AS b ON b.build_id = r.build_id
WHERE r.build_id IS NOT NULL AND b.build_id IS NULL;

-- @CHECK E-12 | referential | defects.run_id (when given) exists in test_runs | returns defects.defect_id
SELECT d.defect_id
FROM defects AS d
LEFT JOIN test_runs AS r ON r.run_id = d.run_id
WHERE d.run_id IS NOT NULL AND r.run_id IS NULL;

-- @CHECK E-13 | referential | defects.case_id (when given) exists in test_cases | returns defects.defect_id
SELECT d.defect_id
FROM defects AS d
LEFT JOIN test_cases AS c ON c.case_id = d.case_id
WHERE d.case_id IS NOT NULL AND c.case_id IS NULL;

-- ---- Category: validity (domains and ranges) --------------------------------

-- @CHECK E-14 | validity | Run result is one of pass, fail, skip (NULL is reported by E-08, not here) | returns test_runs.run_id
-- (WORKED EXAMPLE: already complete)
SELECT run_id
FROM test_runs
WHERE result IS NOT NULL AND result NOT IN ('pass', 'fail', 'skip');

-- @CHECK E-15 | validity | Run duration_sec is between 1 and 3600 (NULL is reported by E-08, not here) | returns test_runs.run_id
SELECT run_id
FROM test_runs
WHERE duration_sec IS NOT NULL
  AND (duration_sec < 1 OR duration_sec > 3600);

-- ---- Category: cross-table consistency and business rules -------------------

-- @CHECK E-16 | business rule | A run cannot happen before its build was created (run_date >= built_date) | returns test_runs.run_id
-- (WORKED EXAMPLE: already complete. ISO dates compare correctly as text.)
SELECT r.run_id
FROM test_runs AS r
INNER JOIN builds AS b ON b.build_id = r.build_id
WHERE r.run_date < b.built_date;

-- @CHECK E-17 | business rule | Every FAILED run has at least one defect | returns test_runs.run_id
SELECT r.run_id
FROM test_runs AS r
WHERE r.result = 'fail'
  AND NOT EXISTS (
      SELECT 1
      FROM defects AS d
      WHERE d.run_id = r.run_id
  );

-- @CHECK E-18 | business rule | A defect that references a run must reference a FAILED run | returns defects.defect_id
-- (technique: C5. Defects whose run does not exist are E-12, not this check.)
SELECT d.defect_id
FROM defects AS d
INNER JOIN test_runs AS r ON r.run_id = d.run_id
WHERE r.result <> 'fail';

-- @CHECK E-19 | cross-table consistency | defects.case_id equals the case_id of the run it references | returns defects.defect_id
-- (only for defects whose run exists and where both case ids are present)
SELECT d.defect_id
FROM defects AS d
INNER JOIN test_runs AS r ON r.run_id = d.run_id
WHERE d.case_id IS NOT NULL
  AND r.case_id IS NOT NULL
  AND d.case_id <> r.case_id;

-- @CHECK E-20 | business rule | Defect dates and status agree: closed_date >= opened_date; status fixed/closed needs a closed_date; status open must have none | returns defects.defect_id
-- (WORKED EXAMPLE: already complete)
SELECT defect_id
FROM defects
WHERE (closed_date IS NOT NULL AND closed_date < opened_date)
   OR (status IN ('fixed', 'closed') AND closed_date IS NULL)
   OR (status = 'open' AND closed_date IS NOT NULL);
