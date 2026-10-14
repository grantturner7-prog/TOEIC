# TOEIC handoff notes (carried over from the planning conversation, 2026-10-14)

## Decisions made
- Target market: **Taiwan first**, international after it sells well.
- Approach: **hybrid**. Strategy stays the spine (Locate and Answer pillars, signals and keywords), with a real English-teaching "Skills" track alongside, heaviest for Parts 5 and 6 (grammar and vocabulary). Skills and Strategy stay in separate, cross-linked sections.
- First release: **Listening & Reading only**. Speaking & Writing is a later phase.
- Build order: **Reading first, then Listening** (Listening needs audio, the biggest cost and risk).
- Every phase ends in a small audit at `docs/audit/toeic/phase-N.md`; the owner signs off before the next phase.
- Architecture to reuse from the IELTS project: `content/` JSON, server gate, teacher/student/admin roles, a `check_*.py` content gate. Add a `toeic` product line next to `ielts`.
- Original content only (no ETS or published TOEIC material). Same standing rules as IELTS: "students", positive wording, max three items per breakdown, no raw transcripts committed.

## About the test (from memory; verify against ETS's public description)
- Two separate tests. **L&R**: 200 multiple-choice questions, about 2 hours, scaled 10–990. **S&W**: 11 speaking and 8 writing tasks, scored 0–200 each (later phase).
- Workplace English (emails, notices, meetings, schedules), not academic. No bands; students aim for targets such as 600, 750 or 850.
- Parts: 1 Photographs, 2 Question–response, 3 Conversations, 4 Talks, 5 Incomplete sentences, 6 Text completion, 7 Reading comprehension.
- Why more English teaching than IELTS: Parts 5/6 test grammar and vocabulary directly; Parts 2/3 distractors rely on similar sounds; many test-takers are lower level.

## Taiwan market (rough)
- About 298,000 test-takers in 2013 and about 398,000 in 2017 (TOEIC Taiwan newsletters). No current published figure found; likely low-to-mid hundreds of thousands per year (a guess).
- 2025 Taiwan average score reported as 583 (record high).
- Get a real figure from the Taiwan distributor, Chung Hsin (忠欣), before pricing or market-size decisions.
- Implications: cheap repeatable practice, score tracking across attempts, possible group or teacher sales (universities and employers buy in bulk).

## Where the project map lives
- `docs/TOEIC-PLAN.md` in this repo (copied from `grantturner7-prog/IELTS`, branch `claude/laughing-bardeen-s1pwhk`). Ten phases (0–9).

## Open owner questions (also at the end of the plan)
1. Reading first, then Listening?
2. Audio: recorded voices or text-to-speech?
3. Pricing shape and NT$ level (same as IELTS?)
4. Traditional Chinese for the whole interface from the first release?
5. One app and login for IELTS and TOEIC, or a separate site?
6. Will the owner record TOEIC strategy conversations as for IELTS?
7. Is there a teacher for review and sign-off?

## Loose ends
- The IELTS repo still has branch `claude/laughing-bardeen-s1pwhk` holding a copy of the plan. Delete it only if the owner says so.
- Verify the part and question counts against ETS's current public description before Phase 1 sign-off.
