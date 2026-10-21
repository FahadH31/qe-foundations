# Ingestion module - design notes (Week 2, Day 2)

Answer in your own words, 2-4 sentences each. Replace every line that starts with

## 1. Exceptions or assertions?
In `validate_record` I raise exceptions for a negative duration, but in
`IngestionReport.check_invariants` I use `assert`. Why is each the right tool there?

<p>
Answer: In this project, exceptions are used to handle potential issues caused by external data, files, records, etc. They check that the input to the code is correct/as expected from the code, so that if it is not, the program can exit gracefully and provide the necessary information. Assertions here are used to make sure there are no errors in my own code - logic bugs or otherwise that could lead to silent incorrect results or larger issues. Basically, checking external input for correctness vs. checking my own code for correctness.    
</p>

## 2. Stop or collect?
Why is a malformed JSON file a `SourceError` that stops loading, while a record with
a bad status is a `RecordValidationError` that is collected? Who benefits from this split?

<p>
Answer: A malformed JSON file is a SourceError that stops loading because it means the entire file is unusable. A bad status is a 'RecordValidationError' that is collected because it is a single broken field/row, and the rest of the file can still be used and may have many valid entries. In terms of who benefits from this split, it is the tester/QA analyst that runs tests to see the correctness of the system. The specific bad cases are identified and presented to the QEA so that the source of the issue can be identified, rather than the entire file being disregarded and not providing a clear detailed reason as to why it failed. 
</p> 

## 3. What did the context managers buy you?
Name two things that `open_source` / `LoadSession` do for the caller that you would otherwise
have to remember to do at every call site.

<p>
Answer: The open_source() method handles the opening/closing of the file properly with exception handling, rather than having to write that code repeatedly at every call site. LoadSession automatically tracks elapsed time and outcome of loading a file for bookkeeping purposes.
</p>

## 4. Your hardest bad-input case
Which sample file or record took you longest to handle, and what was the cause?

<p>
Answer: Probably the XML parsing in reader.py, where I needed to find the testcase tags at any depth and find attributes and child elements. It took more research and checking of self-study notes as we didn't cover XML stuff live in class. Took more thought and time to implement. 
</p>