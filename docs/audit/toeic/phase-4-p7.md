# Phase 4 audit, Part 7

Date: 2026-10-14. Content and code: IELTS repo, branch `claude/toeic-phase3`.

## What was built
- `content/toeic/sets/p7-set-1.json`: 10 single passages (29 questions) and 5 multiple-passage sets, 2 double and 3 triple (25 questions). Document kinds: notice, advertisement, schedule, email, text-message chain, form, article, online chat. 54 questions: 27 detail and not-stated, 13 purpose, inference and writer's intent, 14 vocabulary, sentence insertion and cross-passage.
- `content/toeic/strategies/p7.json`: strategy card (Locate / Answer, where the pillars fit best), 3 principles, 3 Skills groups. Status `awaiting-recording`.
- App: Part 7 listed and playable; end-to-end test plays all 54 questions, checks a triple set shows three documents, and checks the results screen gives an estimated range.
- Docs here: `docs/curriculum/toeic-part7.md`, teacher checklist `docs/review/p7-set-1-teacher.md`.

## Checks run
| Check | Result |
|---|---|
| `check_toeic.py --spec p7` | OK: 29 single + 25 multiple; keys 14/14/13/13; longest-key and shortest-key bias inside limits after two rounds of option edits |
| `check_toeic.py --spec reading` on p5 + p6 + p7 together | OK: 100 questions, the full Reading section |
| Blind solve, round 1 (3 solvers, no key) | 54 of 54 agreed by all 3. Flags: the lamp emails did not say the order was grey; a chat timing meant the speaker would arrive after the 10:45 deadline; an interview weekday did not match a plausible year |
| Blind solve, round 2 on the 2 edited sets | 10 of 10 agreed by all 3; no inconsistencies found |
| `npm test` | all green (exit code checked) |
| `e2e-toeic.cjs` | ok |

## Defects found and how each was fixed
- Checker: key was the longest option in 54% of questions, then the shortest in 37%; options rewritten twice until both were under 35%.
- Passage consistency: lamp order made explicit (two grey lamps); chat times moved from 10:40 to 10:30 so "in five" lands before 10:45; weekday dropped from the interview date.
- Five negative-stem warnings (NOT questions) are intentional for the "not stated" type and are listed for the teacher.

## Open items carried forward
- Teacher review and source-facts review pending; items stay `draft`.
- Strategy card is a draft until the owner's recording arrives.
- Two inference-based answers for the teacher to confirm (p7-0006 q3, p7-0011 q2).
- Phase 4 is now complete for all three Reading parts. The full 100-question Reading set passes the checker, which is the first step towards Phase 7 mocks.

## Owner sign-off
Pending (yes / no, date).
