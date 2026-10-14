# TOEIC content standards

Every item sold must pass every gate below. Gates 1 to 6 run in `scripts/check_toeic.py`. Gates 7 to 9 are recorded in each item's `review` fields and are checked by the same script before an item can be `published`.

## Item file format
A JSON file `{"items": [...]}` under `content/toeic/`. Fields shared by all items:

| Field | Rule |
|---|---|
| `id` | Unique across all files, e.g. `p5-0001` |
| `part` | `p5`, `p6` or `p7` (Listening parts arrive with Phase 6) |
| `type` | A slot ID from `content/toeic/catalog.json` that belongs to this part |
| `difficulty` | 1 (easier), 2 (medium), 3 (harder) |
| `topic` | One of: office, hr, finance, travel, manufacturing, retail, dining, health, housing, technology, marketing, events |
| `source` | Always `original` |
| `explanation` | Non-empty; says why the key is right and why the others are not |
| `status` | `draft`, `reviewed` or `published` |
| `review` | `{"blind_solve": null or "pass", "teacher": null or "pass"}` |

Part shapes:
- **p5:** `stem` with exactly one `____`, `options` A to D, `answer`.
- **p6:** `text` containing markers `[1]` to `[4]`, `questions` (one per marker: `blank`, `type`, `options` A to D, `answer`).
- **p7:** `format` (`single`, `double` or `triple`), `documents` (1, 2 or 3 matching the format; each `{kind, text}`), `questions` (`stem`, `type`, `options` A to D, `answer`).

## The gates
1. **Structure.** All fields present; ids unique; type belongs to the part; exactly options A to D, none empty, none repeated; the key is one of A to D.
2. **Single clear blank.** p5 has one blank; p6 markers match its questions one for one.
3. **Counts per set.** p5 set: 30 items. p6 set: 4 passages, 16 questions. p7 set: 29 single-passage questions and 25 multiple-passage questions (5 sets of 5). Reading section: all three together (100 questions). Passage questions: single 2 to 4 per passage; double and triple exactly 5.
4. **Difficulty ladder.** Values 1 to 3. A p5 set of 30 has at least 5 items at each level.
5. **Option spread.** In any file of 12 or more questions, each key letter A to D is between 10% and 40% of keys, and the key is the longest option in at most 50% of questions.
6. **Originality and no duplicates.**
   - `source` is `original`; no item text mentions ETS or "Educational Testing Service".
   - No two items share the same stem (or passage opening) after lower-casing and removing punctuation.
7. **Source facts.** Every name, company, price, time and date inside a passage is invented and consistent within the passage. Anything real (a city, a holiday) is correct.
8. **Blind solve.** An independent AI solver, given only the item, agrees with the key. Recorded as `review.blind_solve = "pass"`. A disagreement means the item is fixed or removed.
9. **Teacher review.** A teacher checks grammar, naturalness, one clearly best answer, and that no option is also correct. Recorded as `review.teacher = "pass"`.
10. **Pilot.** Once on sale, item analysis in the admin Items page flags items that are too easy, too hard or that strong students miss; flagged items are fixed within the pilot (Phase 9).

An item may be `published` only if gates 1 to 6 pass and both review fields are `pass`.

## Writing rules
- Workplace English: emails, notices, schedules, advertisements, meetings, chats.
- Original wording only. We are not affiliated with or endorsed by ETS.
- Students are called "students". Positive wording. No remarks about any group or about the test.
- Distractors are wrong for a teachable reason (form, meaning, collocation or context), and the explanation names it.
- Scores shown to students are indicative; we never promise a score.
