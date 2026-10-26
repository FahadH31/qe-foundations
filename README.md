<h2>Week 2 Project - QE Foundations</h2>
Legacy Code Migration

<h2>Setup</h2>
<ol>
    <li>Clone this repository.</li>
    <li>Create virtual environment with python -m venv .venv</li>
    <li>Activate it with .venv/Scripts/Activate.ps1 for Powershell, source .venv/bin/activate for bash.</li>
    <li>Install dependencies with python -m pip install -r requirements.txt</li>
    <li>Verify success by running python smoke_utils.py</li>
</ol>

<h2>How to Run the Report</h2>
<p>Run the Friday release validation report command:</p>

### Run on dirty data (exit code 1, DATA QUALITY: FAIL)
python -m qe_foundations.report

### Run on clean test data (exit code 0, DATA QUALITY: PASS)
python -m qe_foundations.report --data data/clean

### Run with malformed data (exit code 2, error logged)
python -m qe_foundations.report --data data/malformed

### Show offending violation IDs
python -m qe_foundations.report --show

<h2>Running Tests</h2>
<p>Execute the test suite with Python unittest:</p>
<pre>
python -m unittest discover -s tests -t . -v
</pre>

<h2>Day Logs</h2>
<h3>Project 1 Milestone - Week 2, Day 1 (Monday)</h3>
What already exists:
<ul>
    <li>qe_foundations package</li>
    <li>qe_foundations/utils sub-package</li>
    <li>/docs/structure.md</li>
    <li>/data and /test placeholders.</li>
</ul>

<h3>Project 1 Milestone - Week 2, Day 5 (Friday)</h3>
<ul>
    <li>Cross-table SQL checks in sql/part_e_checks.sql</li>
    <li>Data ingestion pipeline in qe_foundations/ingestion/sqlite_loader.py</li>
    <li>SQL checks execution engine in qe_foundations/validation/sql_checks.py</li>
    <li>Full report runner CLI in qe_foundations/report.py</li>
    <li>Data quality findings in docs/DATA_QUALITY_FINDINGS.md</li>
    <li>Week 2 reflection in docs/WEEK2_REFLECTION.md</li>
</ul>
