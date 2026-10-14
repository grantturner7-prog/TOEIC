# Phase 3b audit: scoring and report logic

Date: 2026-10-14. Code: IELTS repo, branch `claude/toeic-phase3`, commit eab5203.

## What was built
- `app/js/toeic-report.js` (pure, shared by browser and tests): `flattenSet` (all three item formats to one question list), `resultFor`, `summarizeSet`, `partReport`, `estimateRange`, `sectionRange`.
- `content/toeic/scoring.json`: **uncalibrated** placeholder (straight line from 5 to 495; range half-width 60 / 90 / 120 points for 100 / 50 / 30 or more questions; no range below 30 questions).
- `scripts/test-toeic-report.mjs`, now part of `npm test`.

## Checks run
| Check | Result |
|---|---|
| `node scripts/test-toeic-report.mjs` | ok |
| Covered | p5, p6 and p7 flatten correctly (blank numbers, documents kept with every question, multiple-passage sets); right, wrong and blank answers; part report; no range under 30 questions; ranges always `low < high`, multiples of 5, inside 5 to 495 and non-decreasing as correct answers rise, for six set sizes; Reading and Listening kept separate; unknown section or missing table gives no range |
| `npm test` | all green |

## Defects found and how each was fixed
- Two expected values in the first test run were my arithmetic slips (15 of 30 gives 130 to 370; 70 of 100 gives 285 to 410). The module followed the stated formula; the test was corrected.

## Open items carried forward
- The conversion is a straight line, not ETS's real curve, and must be recalibrated with a large pilot before any score range is advertised.
- Item analysis for TOEIC (separate from IELTS) is not built yet; TOEIC attempts are excluded from the IELTS one.

## Owner sign-off
Yes, 2026-10-14 (owner said "keep going").
