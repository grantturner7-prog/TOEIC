# Phase 6a audit: Listening scripts (audio pending)

Date: 2026-10-15. Content and code: IELTS repo, branch `claude/toeic-phase3`. Standards and tools: this repo.

## What was built
- Checker extended to Listening: Part 2's three options, speakers with accent and gender, scripts, graphics, timing, "no publishing without audio"; 28 Listening defect checks and 1,510 fuzz corruptions pass. Standards document gained the Listening item shapes and gates.
- `content/toeic/sets/p1-set-1.json` (6 photographs with photo briefs), `p2-set-1.json` (25 question-response), `p3-set-1.json` (13 conversations, 39 questions, 3 with a graphic, 1 with three speakers), `p4-set-1.json` (10 talks, 30 questions, 2 with a graphic): 100 questions, the full Listening section, in US, UK, AU and CA voices.
- Strategy cards for Parts 1 to 4 (Catch/Answer for 1 and 2, Locate/Answer for 3 and 4), live in the app; sets listed as "Audio coming soon" and not playable until audio exists.
- `scripts/tts_manifest.py` (timing estimate and a 316-segment voice-by-voice manifest in `audio/manifest-listening-set-1.json`, about 47 minutes of audio) and `docs/AUDIO-PRODUCTION.md`.
- Teacher checklists for the four sets in `docs/review/`.

## Checks run
| Check | Result |
|---|---|
| `check_toeic.py --spec listening` on the four sets | OK: 54 items, 100 questions, accents covered, key spread and length bias inside limits |
| Blind solve from transcripts, three independent solvers per part, on the final text | Part 1: 6/6 by all three (two rounds). Part 2: 25/25 by all three. Part 3: 39/39 by all three (two rounds). Part 4: 30/30 by all three (two rounds, after two talks were rewritten in new settings) |
| Critic review (item-writing expert) on every batch | All items "keep" on the final text |
| `npm test`, `e2e-toeic.cjs` | 100 backend checks, browser test green |

## Defects found and how each was fixed
- Writing workflow: my item-numbering mismatch made every batch after the first look like a total solver failure, so items were rewritten twice on false grounds and the run cost about 11.9 million tokens (217 agents). The solver numbers from that run were discarded and the blind solve was redone from the assembled files. Lesson recorded: compare on the label the solver saw, and test the comparison on one batch first.
- Part 2 keys were the longest option in 88% of items; all 25 items' responses rebalanced to similar lengths, then re-solved.
- Part 3: a graphic question answerable without the graphic (the man named the product range) reworked; a soup "sold out at lunch" contradiction, a holiday date that made a deadline exception pointless, four stilted lines, repeated character names, and a near-tie distractor fixed.
- Part 4: two near-duplicate settings (two dental clinics, two factory tours) replaced by a car-service greeting and a hotel-kitchen safety briefing; a key that was literally false, two stems that assumed facts, a pronoun shift, a weekday that matched no calendar, a half-leaking graphic question, repeated names and an all-A item fixed.
- Spelling normalised to US across all four sets (printed TOEIC material uses US spelling); the voices still carry four accents.

## Open items carried forward
- **Audio and photos are not produced** (Phase 6b): produce from the manifest, check lengths against the timings, source Part 1 photos to the briefs, then set `audio` on each item.
- Teacher script review pending on all four sets; items stay `draft`.
- Part 2 set-level variety rework done (7 items changed, 3 new scenarios; the first attempt stopped on a session rate limit and was rerun) and re-solved 25/25 by all three solvers. Remaining style notes for the teacher: p2-0022's indirect key is the weakest in the set, and a few distractors open with "Yes" to a wh- question as an intended trap.
- Items p3-0004 and p4-0004 were re-solved after their graphic clue was reworked: 6/6 by all three solvers, and both graphic questions now need the graphic (one remaining elimination route in p3-0004 was closed by neutralising the shelf line).
- Timing total is about 47 minutes against the test's 45; indicative only, to be checked against ETS's sample test pauses.
- Strategy cards are drafts until the owner's recordings arrive.

## Owner sign-off
Pending (yes / no, date).
