# TOEIC handoff notes (carried over from the planning conversation, 2026-10-14)

## Decisions made
- Target market: **Taiwan first**, international after it sells well.
- Approach: **hybrid**. Strategy stays the spine (Locate and Answer pillars, signals and keywords), with a real English-teaching "Skills" track alongside, heaviest for Parts 5 and 6 (grammar and vocabulary). Skills and Strategy stay in separate, cross-linked sections.
- First product: **Listening & Reading**, released Reading first and sold as a Reading course until Listening ships. Speaking & Writing is a later phase.
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

## Review outcome (2026-10-14)
Three reviewers checked Phases 1 and 2; fixes and five plan changes are in `docs/TOEIC-PLAN.md` ("Plan changes after the Phase 1 and 2 review"). Key learnings: the test has no separate preview pause (students read ahead in directions and gaps); Parts 3, 4 and 7 have speaker/writer-intent questions; Locate and Answer fits Part 7 best and Part 5 is a quick routine; scaled scores need estimated ranges.

## Where the project map lives
- `docs/TOEIC-PLAN.md` in this repo (copied from `grantturner7-prog/IELTS`, branch `claude/laughing-bardeen-s1pwhk`). Ten phases (0–9).

## Owner questions
Answered yes (2026-10-14): Reading first, pricing shape like IELTS, Traditional Chinese interface, one app and login, owner records strategy conversations, a teacher is available (name to be recorded).
**Still open:** audio method (recorded voices, text-to-speech or a mix). Must be decided before Phase 5.

## Loose ends
- The IELTS repo still has branch `claude/laughing-bardeen-s1pwhk` holding a copy of the plan. Delete it only if the owner says so.
- Verify the part and question counts against ETS's current public description before Phase 1 sign-off.
