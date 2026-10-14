# Phase 4 audit, Part 5

Date: 2026-10-14. Content and code: IELTS repo, branch `claude/toeic-phase3`.

## What was built
- `content/toeic/sets/p5-set-1.json`: 30 original items (10 per difficulty; 12 word-form, 9 function-word, 9 vocabulary; 12 workplace topics).
- `content/toeic/strategies/p5.json`: strategy card (Spot the clue / Choose and move on, 3 steps each), 3 principles, 3 Skills groups of 3 items. Status `awaiting-recording`.
- App: Part 5 page (`#/s/toeic/part/p5`), parts list on the TOEIC home, strategy pages gated by a feature the administrator can make premium. 7 strings added in both languages.
- Docs here: `docs/curriculum/toeic-part5.md`, teacher checklist `docs/review/p5-set-1-teacher.md`.

## Checks run
| Check | Result |
|---|---|
| `check_toeic.py --spec p5` | OK: 30 items (counts, ladder 10/10/10, key spread, no longest-key bias, no duplicates) |
| Blind solve, round 1 (3 independent solvers, no key) | 29 of 30 agreed; 5 items flagged as having a weak second answer; the key pattern A-B-C-D repeated and was predictable |
| Blind solve, round 2 after rewriting 5 items and shuffling keys | 30 of 30 agreed by all 3 solvers; 2 wording notes |
| Blind solve, round 3 on the 2 reworded items | 3 of 3 agree; both judged natural with one answer |
| `npm test` | 95 backend checks, all green; unit and string checks green |
| `e2e-toeic.cjs` | ok (part page, 30-item set played to the end, full-marks range shown as partial) |

## Defects found and how each was fixed
- Items 5, 7, 11, 18, 28: second answer arguable (collective-noun agreement, sit/seat, launches, however/otherwise, applies to/for). Rewritten.
- Predictable key order. Keys now shuffled with 8/8/7/7 spread.
- Item 16 and 18 wording tightened after round 2.
- Test expectations: a missing strategy file is 404 not 403; a student who already owns the product sees the page. Tests corrected.
- One commit was pushed with a failing check because the test output was piped through grep; fixed in the next commit. Lesson recorded: check the exit code, not the text.

## Open items carried forward
- **Teacher review and source-facts review are pending**; items stay `draft` until both are `pass`.
- Strategy card is a draft until the owner's recording arrives.
- "AI assistant (draft)" is recorded as provenance; no model name is written into repository files under this session's rules.

## Owner sign-off
Yes, 2026-10-14.
