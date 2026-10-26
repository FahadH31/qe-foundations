# Week 2 reflection

## What I can do now that I could not do on Monday
On Monday I only knew the basics of structuring a Python package with a virtual environment and imports. Now I can build custom exception hierarchies for data ingestion, set up modular file and console logging with unittest suites, and write multi-table SQL queries using joins, correlated subqueries, and conditional aggregation to validate database integrity.

## The hardest moment this week and how I got through it
The hardest part was understanding why my NOT IN subquery returned zero rows in Part C even though the cases clearly had no runs. I spent a while checking my syntax before realizing that a single NULL value inside the subquery turns the whole NOT IN expression into UNKNOWN under three-valued logic. Switching to a NOT EXISTS query resolved the issue.

## Where each day showed up in the final command
Monday provided the package structure and venv that allows running python -m qe_foundations.report. Tuesday built the CSV/JSON ingestion and custom exceptions in ingestion/. Wednesday gave us logging and unit testing in tests/ and utils/. Thursday introduced SQL violation checks where zero rows mean PASS, and Friday tied everything together with 20 cross-table validation checks and the report CLI.

## One thing I would do differently
I would plan my database inspection better before jumping into writing queries. Previewing rows with a quick SELECT and writing down predictions first saved me a lot of debugging time during Part E, and I should've used that approach earlier in the week.

## A question I still have
How are automated SQL data validation suites like this typically scheduled and triggered inside modern CI/CD pipelines without slowing down build deployments
