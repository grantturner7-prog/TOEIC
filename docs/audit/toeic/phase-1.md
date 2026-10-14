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
