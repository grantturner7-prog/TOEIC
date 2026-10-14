# Phase 4 audit, Part 6

Date: 2026-10-14. Content and code: IELTS repo, branch `claude/toeic-phase3`.

## What was built
- `content/toeic/sets/p6-set-1.json`: 4 original texts (email, notice, advertisement, memo), 16 questions (5 grammar in context, 7 vocabulary and linking, 4 sentence insertion), difficulties 1, 2, 2, 3.
- `content/toeic/strategies/p6.json`: strategy card (Find the clue / Choose and check), 3 principles, 3 Skills groups. Status `awaiting-recording`.
- App: Part 6 listed on the TOEIC home and part page; end-to-end test plays the set to the end.
- Docs here: `docs/curriculum/toeic-part6.md`, teacher checklist `docs/review/p6-set-1-teacher.md`.

## Checks run
| Check | Result |
|---|---|
| `check_toeic.py --spec p6` | OK: 4 texts / 16 questions; keys 4 per letter; longest-key and shortest-key bias inside limits after two rounds of distractor edits |
| Blind solve, round 1 (3 solvers, no key) | 16 of 16 agreed by all 3; flags: one awkward purpose clause, "lose out" as a real phrase, one inserted sentence only loosely tied to its text |
| Blind solve, round 2 on the 3 edited texts | 12 of 12 agreed by all 3; two minor style notes passed to the teacher |
| `npm test` | all green (exit code checked) |
| `e2e-toeic.cjs` | ok |

## Defects found and how each was fixed
- Checker: key was the longest option in 38% of questions (sentence-insertion keys were longer than their distractors); distractor sentences lengthened. Then the key was the shortest in 38%; one blank changed to "to put" so the shortest distractor is shorter than the key, and one modal distractor shortened.
- Text 1 blank 3: purpose clause did not follow from emptying the bins; rewritten around storing the paper.
- Text 3 blank 4: "lose" replaced by "forget" because "lose out" is idiomatic.
- Text 2 blank 2: inserted sentence changed to one about the water supply so the link is real.

## Open items carried forward
- Teacher review and source-facts review pending; items stay `draft`.
- Strategy card is a draft until the owner's recording arrives.
- Two style notes for the teacher (see the checklist).

## Owner sign-off
Yes, 2026-10-14.
