# Phase 3c audit: short item formats in the app

Date: 2026-10-14. Code: IELTS repo, branch `claude/toeic-phase3`, commit 6f04baa.

## What was built
- `app/js/views/toeic.js`: set list (`#/s/toeic`) and player (`#/s/toeic/set/<id>`) for Part 5 (one sentence), Part 6 (text with numbered blanks) and Part 7 (documents plus questions); results screen with part report and estimated range; attempt saved with product line `toeic`.
- Routes added in `app/js/main.js`; content helpers in `app/js/content.js`. No navigation entry yet, so IELTS students do not see it.
- `scripts/e2e-toeic.cjs` (Playwright, real browser).

## Checks run
| Check | Result |
|---|---|
| `sh scripts/run-e2e.sh scripts/e2e-toeic.cjs` | ok |
| Covered | list; intro; progress text; all three formats render; Next disabled until an answer; skip; results `10 of 12`; part rows; too-few-questions hint instead of a range; estimate note always shown; review shows the skipped question and key; attempt saved as `toeic` with correct totals; switch to Chinese and back without reload; IELTS progress page does not list the TOEIC attempt; premium set locked and its file returns 403; unknown set; Chinese browser starts in Chinese; no sideways scroll at 390 px wide |
| Existing IELTS browser tests (`e2e`, `e2e-store`, `e2e-mcq`, `e2e-types`, `e2e-exam`, `e2e-locate`, `e2e-extra`, `e2e-evidence`, `e2e-motion`, `e2e-theme`) | all report no errors |
| `e2e-video` | Fails with a click timeout. It fails the same way on the original branch, so it is not caused by this work. |

## Defects found and how each was fixed
- Two e2e expectations were wrong (Part 6 had 3 correct, and the page text has no spaces between cells). The app was right; the test was corrected.

## Open items carried forward
- Single-question flow only: no timer, no immediate feedback, no mock exam screen (Phase 7).
- The static demo build (`app/js/demo-engine.js`) does not know about TOEIC.
- `e2e-video` is broken independently of this work and should be looked at separately.

## Owner sign-off
Pending (yes / no, date).
