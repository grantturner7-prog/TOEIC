# TOEIC content standards

Every item sold must pass every gate below. Gates 1 to 6 run in `scripts/check_toeic.py`. Gates 7 to 9 are done by people or independent solvers and recorded in each item's `review` fields; the same script refuses `reviewed` or `published` status unless they are recorded. Gate 10 happens after launch.

## Item file format
A JSON file `{"items": [...]}` under `content/toeic/`. Fields shared by all items:

| Field | Rule |
|---|---|
| `id` | Unique across all files, `p5-0001` style, starting with its part |
| `part` | `p5`, `p6` or `p7` (Listening parts arrive with Phase 6) |
| `type` | A slot ID from `content/toeic/catalog.json` that belongs to this part |
| `difficulty` | Integer 1 (easier), 2 (medium), 3 (harder) |
| `topic` | One of: office, hr, finance, travel, manufacturing, retail, dining, health, housing, technology, marketing, events |
| `source` | Always `original` |
| `provenance` | `{"method": "human"}` or `{"method": "ai", "model": "...", "prompt_ref": "..."}`; AI-written items record the model and where the prompt is kept |
| `explanation` | Non-empty; says why the key is right and why the others are not |
| `status` | `draft`, `reviewed` or `published` |
| `review` | `{"blind_solve": null/"pass"/"fail", "blind_solvers": 0, "facts": null/"pass"/"fail", "teacher": null/"pass"/"fail"}`; all four keys present |

Part shapes:
- **p5:** `stem` with exactly one `____`, `options` A to D, `answer`.
- **p6:** `text` containing markers `[1]` to `[4]` once each, `questions` (one per marker: `blank` 1 to 4, `type`, `options` A to D, `answer`).
- **p7:** `format` (`single`, `double` or `triple`), `documents` (1, 2 or 3 matching the format; each `{kind, text}`, texts all different), `questions` (`stem`, `type`, `options` A to D, `answer`).

### Listening item shapes (Parts 1 to 4)
Shared by all Listening items: `timing` `{"audioSeconds": n}` (estimated from the script by `scripts/tts_manifest.py`), `audio` (null until the file exists, then its path), and a voice for every speaker: `{"accent": "US"|"UK"|"AU"|"CA", "gender": "M"|"W"}`.
- **p1:** `photo` `{brief}` (what the picture shows, written for the photographer or stock search), `speaker` voice, `options` A to D (the four spoken statements), `answer`.
- **p2:** `prompt` (the spoken question or statement), `speakers` `{prompt, response}` voices, `options` A to C (three spoken responses), `answer`.
- **p3:** `setting`, `script` (4 or more turns, 2 or 3 speakers; each `{speaker, accent, gender, text}`), optional `graphic` `{kind, rows}` (a small table of text cells), `questions` exactly 3 (`stem`, `type`, `options` A to D, `answer`).
- **p4:** as p3 with one speaker and 1 to 4 segments.

## The gates
1. **Structure.** All fields present with the right types; ids unique; item type and every question type belong to the part; options are exactly A to D, each non-empty text, none repeated (compared after lower-casing and removing punctuation and spacing); the key is one of A to D; no "all/none/both of the above" options. Malformed input produces a clear error, never a crash.
2. **Single clear blank.** p5 has one blank; p6 markers `[1]`-`[4]` appear once each and match its four questions one for one. p7 stems and document texts are non-empty.
3. **Counts per set.** p1 set: 6 items. p2 set: 25 items, 6 to 11 at each difficulty. p3 set: 13 conversations / 39 questions, at least 2 with a graphic and at least 1 with three speakers. p4 set: 10 talks / 30 questions, at least 2 with a graphic. Listening section: all four together (100 questions) using at least 3 of the 4 accents. p5 set: 30 items. p6 set: 4 passages, 16 questions. p7 set: 29 single-passage questions and 25 multiple-passage questions (5 sets of 5). Reading section: all three together (100 questions). Passage questions: single 2 to 4 per passage; double and triple exactly 5.
4. **Difficulty ladder.** A p5 set of 30 has 8 to 12 items at each level.
5. **Option spread, per file.** Four-option and three-option questions are judged separately. In a file of 24 or more four-option questions each key letter A to D is 10% to 40% of the keys (three-option: 20% to 50%). In a file of 12 to 23 questions each letter is used at least once and none is above 50%. In any file of 12 or more, the key is the longest option in at most 35% of questions and the shortest in at most 35%.
6. **Originality and no duplicates.**
   - `source` is `original`; no text in an item mentions ETS or "Educational Testing Service" (any spacing, punctuation or Unicode variant).
   - No two items have the same stem (p5), passage text (p6) or document texts (p7) after normalising case, punctuation and spacing. A p7 question stem may not repeat inside one passage set.
   - **Not original, and so not allowed:** real test items, paraphrased real items, questions recalled by students after sitting the test, and "recalled test" banks. Teachers writing items are told this in their brief.
7. **Source facts** (`review.facts`). Every name, company, price, time and date inside a passage is invented and consistent within the passage. Anything real (a city, a holiday) is correct.
8. **Blind solve** (`review.blind_solve`, `review.blind_solvers`). At least three independent solver runs, given only the item, all agree with the key. A disagreement means the item is fixed or removed.
9. **Teacher review** (`review.teacher`). A teacher checks grammar, naturalness, one clearly best answer, no option that is also correct, options of similar form and length, no clue in the stem that gives the key away (for example an "a/an" before the blank), and distractors that are plausible but wrong for a teachable reason.
10. **Pilot.** Once on sale, item analysis in the admin Items page flags items that are too easy, too hard or that strong students miss; flagged items are fixed within the pilot (Phase 9).

An item may be `reviewed` or `published` only if gates 1 to 6 pass and `facts`, `blind_solve` and `teacher` are all `pass` with at least 3 solvers. A Listening item is `published` only when its `audio` file exists.

## Listening-only gates
- **Script review (teacher).** The teacher reads each script aloud, or listens to the produced audio, and confirms it sounds like natural speech, that the trap words are audible, and that the accent assignment is reasonable.
- **Blind solve from the transcript.** Until audio exists, solvers work from the transcript; once audio exists, one solver run uses the audio alone.
- **Timing.** `audioSeconds` is estimated at 2.6 words a second plus the pauses in `docs/AUDIO-PRODUCTION.md`; the produced file is checked to be within 20% of it.
- **Photo (Part 1).** A photo matching `photo.brief` is sourced with a licence that allows commercial use, and the teacher confirms the key statement describes it and no distractor does.

## Warnings (printed, never fail the run)
- Negative stems (NOT, EXCEPT): kept only where the question type needs them (for example "not stated").
- Passage length outside an indicative range (p6 text 30 to 200 words, p7 document 20 to 400 words). The ranges are rough guides and should be revisited once real items exist.

## Writing rules
- Workplace English: emails, notices, schedules, advertisements, meetings, text-message chains and chats.
- Original wording only. We are not affiliated with or endorsed by ETS. "TOEIC" is used only to name the test students are preparing for.
- Students are called "students". Positive wording. No remarks about any group of people. Factual advice about the test (format, timing) is allowed.
- Distractors are wrong for a teachable reason (form, meaning, collocation or context), and the explanation names it.
- Scores shown to students are indicative ranges; we never promise a score.

## Known limits of the checker
- It cannot judge whether an item is good English, has one best answer, or has plausible distractors. Gates 7 to 9 do that.
- Sentence-insertion and cross-passage items get the same structural checks as other items; their specific quality (a real discourse clue, evidence in both documents) is judged at teacher review.
- Whole 200-question tests (`--spec full`, Phase 7) are not covered yet. Listening items are checked structurally; whether a distractor is a real sound-alike is judged by the teacher.
