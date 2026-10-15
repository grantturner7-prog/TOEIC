# Phase 5 audit: Reading diagnostic and Reading plan

Date: 2026-10-14. Code: IELTS repo, branch `claude/toeic-phase3`.
Gate before this phase: audio method decided (a mix; recorded in `docs/TOEIC-PLAN.md`).

## What was built
- `content/toeic/diagnostic/reading.json`: a 34-question, roughly 25-minute diagnostic drawn by item id from the three practice sets (12 Part 5, 8 Part 6, 14 Part 7). The server assembles it, so only the listed items are sent and the sets stay behind their own gate.
- `app/js/toeic-diagnostic.js`: coarse level (foundation under 50%, developing under 75%, strong), parts ranked weakest first (a part needs at least 4 answered questions), weakest question types, and a study plan of at most three steps (weak parts first, Skills-first under 70%, then the rest in test order, Strategy-first).
- Diagnostic screen (`#/s/toeic/diagnostic`) with its own results view: level, parts weakest first, estimated Reading range marked partial, a note that no total is shown, and the plan with links to the part pages. 16 strings in both languages.
- Server: diagnostic file open to everyone; diagnostic attempts recorded under the `toeic` product line.

## Checks run
| Check | Result |
|---|---|
| `scripts/test-toeic-diagnostic.mjs`: three sample students (low, middle, high) | Low → foundation, plan Part 5, 6, 7 all Skills-first. Middle (weak on passages) → developing, Part 7 first Skills-first, then 5 and 6 Strategy-first. High → strong, all Strategy-first in test order. Never more than three steps; parts with too few answers unranked; Listening parts never in a Reading plan |
| Items tagged by part and type | Every diagnostic item carries `part` and a `TQ-` type (checked by the content checker on the source sets) |
| `npm test` | 98 backend checks green, unit and string checks green (exit code checked) |
| `e2e-toeic.cjs` | A student failing all of Part 5 and passing the rest sees "Developing", a plan starting with Part 5 Skills-first, an estimated range, the no-total note, and no total score; attempt saved with 22 of 34 |

## Defects found and how each was fixed
- I counted the diagnostic as 33 questions; it is 34. Test expectations corrected, content unchanged.

## Open items carried forward
- Level thresholds (50% and 75%) and the 70% Skills-first cut are first guesses, to be revisited after the pilot.
- The diagnostic reuses practice items, so a student who did the practice sets first will have seen some questions. A separate diagnostic item bank is a later improvement.
- The full target-score picker (600, 750, 850) waits for Phase 7, as planned.

## Owner sign-off
Yes, 2026-10-15.
