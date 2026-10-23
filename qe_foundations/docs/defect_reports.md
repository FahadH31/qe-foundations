# Defect reports (top 2 findings)

<!--
HOW TO USE: copy this file to  qe_foundations/docs/defect_reports.md.
Choose the TWO most serious defect groups your suite found (think: money, customers,
automation reliability). Write each as a real bug report using the structure from the
lesson "Using SQL for QA Data Validation", section "Reporting what you find".
Keep the "Title:" labels (the check script counts them) and paste the exact SQL.
-->

## Defect report 1

**Title: Run 5003**

**Rule:** R-11 | Consistency | FAILED/ERROR runs need a failure_message; PASSED runs must not have one <!-- id + wording, e.g. R-xx ... -->

**Environment / when:** SQLite test_runs.db on 2026-10-22<!-- database, seed file, date you ran it -->

**Query:**

```sql
SELECT run_id
FROM test_runs
WHERE ((status like 'FAILED' 
or status like 'ERROR')
and (failure_message is NULL or TRIM(failure_message) = '')) 
or status like 'PASSED' and (failure_message is NOT NUll or NOT TRIM(failure_message) = '')
```

**Evidence:** <!-- paste the result rows (run_ids and the offending values) -->
Run 5003: status is 'FAILED' with failure_message NULL.

**Impact:** <!-- why does it matter to a team that trusts these test results? -->
This test fails without any error message - this means QA cannot clearly identify the root cause of the error, which could lead to delays, the bug not being corrected, and in turn more business/costly issues. 

**Severity (suggested) and why:** HIGH - the database itself did not crash but the test failure cannot be identified which is an issue both with the existing code/documentation and the code causing the issue itself as well.

**Question or false-alarm check:** <!-- what could make this NOT a defect? who confirms? -->
Perhaps the status was mistakenly recorded as failed instead of as passed, which could be causing the lack of a failure message. Member of QA team maybe along with a developer would have to investigate and confirm.


## Defect report 2

**Title: Run 5017**

**Rule:** R-07 | Validity | environment must be exactly DEV, QA or STAGING <!-- id + wording, e.g. R-xx ... -->

**Environment / when:** SQLite test_runs.db on 2026-10-22<!-- database, seed file, date you ran it -->

**Query:**

```sql
SELECT run_id
FROM test_runs
WHERE not environment in ('DEV', 'QA', 'STAGING') or environment is null;
```

**Evidence:**
Run 5017: test_name is 'test_payment_card' and environment is 'PROD' (query also flagged 5024 with lowercase 'qa' and 5026 with NULL)

**Impact:** <!-- why does it matter to a team that trusts these test results? -->
An automated test for credit card payments was recorded running in the PROD environment. If automated test suites are hitting production, mock payments or test cards could mess with real production data or potentially charge actual customers, which is a major financial and compliance risk.

**Severity (suggested) and why:** CRITICAL - Running automated payment tests in production can directly impact real users and live money transactions, rather than being contained in test environments.

**Question or false-alarm check:** <!-- what could make this NOT a defect? who confirms? -->
It could just be a config typo where someone entered PROD instead of DEV or QA, or maybe it was an intentional post-deployment sanity check. The DevOps lead or test runner owner would have to confirm if tests are ever supposed to run in prod.
