# Phase 1 audit: Curriculum map

Date: 2026-10-14

## What was built
- `docs/curriculum/toeic-question-types.md` (7 parts, 21 type slots)
- `docs/curriculum/toeic-reading.md`
- `docs/curriculum/toeic-listening.md`
- `content/toeic/catalog.json` (all parts `placeholder`)
- `scripts/check_toeic_catalog.py` (audit script)

## Checks run
| Check | Result |
|---|---|
| `python3 scripts/check_toeic_catalog.py` (counts sum to 200, 100 per section, slots match docs, Strategy and Skills sections present, at most 3 types per part) | OK: 200 questions, 21 slots |
| Part and question counts verified against ETS public score guide (Listening 6/25/39/30, Reading 30/16/54) | Matches |

## Defects found and how each was fixed
- Plan example listed four Part 5 types and four Part 7 types; the three-item rule needed grouping. Merged into three types each (word and verb form together; sentence insertion and cross-passage grouped under Part 7).

## Open items carried forward
- Type taxonomy is our own teaching grouping, not an ETS classification. Teacher should confirm it before Phase 4 content is written.
- Open question 2 (audio method) is still undecided; needed before Phase 6.
- Question-type names are English only; zh-TW glosses come in Phase 8.

## Owner sign-off
Yes, 2026-10-14.

## Corrections after independent review (2026-10-14)
Three reviewers (TOEIC test expert, curriculum and pedagogy, item-writing and code) checked this phase. Fixed:
- Speaker-intent and writer-intent questions added (Parts 3, 4 and 7); Parts 3 and 4 regrouped as topic and purpose / detail and graphics / intent, implication and next step.
- Part 1 types are now one or more people / objects and scenery / mixed scenes; sound-alike choices became a distractor strategy taught inside every type.
- "Preview time" reworded: the test has no separate pause; students read ahead during directions and gaps. Exact lengths still to be checked against the ETS sample test.
- Locate and Answer adapted per part (Part 2 Catch/Answer, Part 5 a quick routine, Part 6 sentence insertion Locate step). IELTS comparison removed.
- Skills added: Chinese-speaker challenges, accents and reductions, number discrimination, distractor patterns, paraphrase, vocabulary review loop, test stamina, suffix patterns and fixed phrases.
- Timing guidance now notes there is no section break; part 6 recorded as 4 texts of 4 blanks; text-message chains listed under Part 7.
- `check_toeic_catalog.py` now runs from any directory, requires 1 to 3 types per part, checks 29 + 25 = 54 and 4 x 4 = 16, and checks the Skills tables link every part.

Re-check: `python3 scripts/check_toeic_catalog.py` -> OK: 200 questions, 21 slots.
Open: the part and timing facts were checked against one ETS search summary plus the test expert's knowledge (ets.org pages could not be opened by the reviewer). Spot-check the ETS sample test PDF for direction and gap lengths before publishing numbers.

## Owner sign-off (corrections)
Pending (yes / no, date).
