# Pairing log -- roles and swap schedule

<!--
HOW TO USE: copy this file to  qe_foundations/docs/pairing_log.md.
Fill ONE row at the END of every 30-minute block (it takes one minute). The check
script counts the rows that are filled in; a 3-hour session has 5 driving blocks.
-->

## Roles card (keep it visible)

| | DRIVER | NAVIGATOR |
|---|---|---|
| Hands | the ONLY one on the keyboard | off the keyboard |
| Job | turn the navigator's direction into code; think aloud while typing | read the rule, decide the next step, predict the result, spot typos and edge cases |
| Says things like | "I'm writing the WHERE clause now..." | "Predict first: which run_ids do we expect?" |
| Never | silently type something nobody asked for | grab the mouse or dictate character by character |

**Swap** every 30 minutes, even in the middle of a rule. The outgoing driver commits and pushes
(your own Git name), the new driver runs `git pull`, then types.

## Pair

| | Name | Git user.name (as shown by `git log`) | Machine / repo owner |
|---|---|---|---|
| Partner A | Fahad | FahadH31 | Yes |
| Partner B | Divyan | Divyan03 | |

Branch: `https://github.com/FahadH31/qe-foundations/tree/feature/sql-validation`        Remote: https://github.com/FahadH31/qe-foundations

## Swap log (one row per block)

| Block | Clock time | Driver | Navigator | Goal of the block | Result (rules done, commit hash) | Predictions: right / wrong |
|---|---|---|---|---|---|---|
| 1 | 1-1:30| Fahad | Divyan | Complete rules R-01 to R-04  | Done, c595e58 | Right |
| 2 | 1:30-2:00 | Divyan | Fahad | Complete rules R-05 to R-08 | Done, ef36484 | Right |
| 3 | 2:00-2:30 | Fahad | Divyan | Complete rules  R-09 to R-12 and E-01, E-02 | Done, 65c4212 | Right |
| 4 | 2:30-3:00 | Divyan | Fahad | Complete block 4 - python runner | Done, 49c60c7 | N/A |
| 5 | 3:00-3:30 | Fahad | Divyan | Complete tests, checklist, report | Done | N/A |

## Disagreements and how we settled them
<!-- At least one honest example: what did you disagree about (query style, a rule's meaning, ...), and how did you decide? -->
At some points we had different understandings/perspectives on query style or approach. While I cannot remember a specific example in detail, we would discuss why we thought our approach would work and the potential flaws in each other's approaches. This allowed us both to build better understandings and spot flaws in both our own and each other's logic. Running the actual queries helped determine the correctness as well.

## Hints we used
<!-- Which hint levels, for which rules? (Using hints is fine -- hiding it is not.) -->
We didn't need hints for the rules, though we did some googling and referencing of notes for certain keywords that we needed help/refreshing with. 
We used the hints for the Python section that are listed there.  
