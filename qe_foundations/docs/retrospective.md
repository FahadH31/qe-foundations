# Retrospective -- Thursday pair exercise (SQL validation)

<!--
HOW TO USE: copy this file to  qe_foundations/docs/retrospective.md  and answer every
"##" section below (keep the headings). Write TOGETHER in the last 15 minutes; both
partners must agree with what is written. Aim for 2-4 specific sentences per section
(about 250-400 words in total). "It went well" is not an answer: name a rule, a
moment, a query, a commit.
Delete nothing except these comments.
-->

## Pair and branch

<!-- Names of both partners, the repo + branch you worked on, the final commit hash. -->


## What we built

<!-- In your own words: what is in the repo now (queries, runner, tests, docs)? How many rules did your suite end with, and what does one `python -m qe_foundations.validation` run print? -->



## How the pairing worked

<!-- Did the driver/navigator split and the 30-minute swaps work? Give one concrete moment where the navigator caught something the driver would have missed, and one moment the pairing felt awkward or slow. What did you change as a result? -->
The driver and navigator did split every 30 minutes. Sometimes the driver would write AND for the rules, but sincec we are finding the negation, the navigator told them to write OR.


## The hardest rule

<!-- Which rule (R-xx) took longest, and why? Quote the first wrong version of the query and what it returned (too many rows? none? an error?), then what fixed it. -->
The hardest rule we encountered was rule 11. The issue was we were not picking up the null values, the query also required a lot of brackets and a lot of conditions which made things more difficult. The issue was we had too few rows, due to not selectng the null values.

This was the initial query:
SELECT run_id
FROM test_runs
WHERE ((status like 'FAILED' 
or status like 'ERROR')
and TRIM(failure_message) = '') 
or status like 'PASSED' and failure_message NOT (is NUll or TRIM(failure_message) = '')

## A surprise in the data

<!-- Which defect did you NOT expect, or which "defect" turned out to be a legitimate row (a false alarm you avoided or briefly fell for)? What would you ask the product owner about it? -->


## SQLite and SQL pitfalls we hit

<!-- NULL behaviour, case sensitivity of = / IN versus LIKE, trailing spaces, inclusive BETWEEN, AND/OR precedence... Which of these bit you, and how will you spot it next time? -->


## Skills we connected from this week

<!-- Name one thing each from Monday (modules/venv/Git), Tuesday (exceptions/files), Wednesday (logging/unittest/merge conflicts) that you actually used today, and how. -->
Divyan: I used the logging.md module from Wednesday extensively while completeing the TODO's in runner.py. One thing in particular I looked at seeing how to setup logging.basicConfig()

Fahad: I found the introductio-to-unit-testing.md module from Tuesday to be very helpful when completeing the test_validation.py file. I looked at it a lot to understand the general structure of test-cases.


## What we would do differently

<!-- One process improvement for the next pair session, and one thing you need from Friday (joins, GROUP BY, constraints) to make this validation suite better. -->
For our pairing process, predicting the exact row IDs together on the checklist before executing the queries would help us catch false passes faster. From Friday's topics, using database constraints (like NOT NULL and CHECK constraints) would prevent bad records from being inserted in the first place, and GROUP BY will make finding duplicates like S-02 much easier than writing manual filters.
