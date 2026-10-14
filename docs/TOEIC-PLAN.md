# TOEIC project map (drafted 2026-10-14)

Goal: a strategy-first TOEIC Listening & Reading course for students in Taiwan, built on the engine we already have, and ready to sell. Speaking & Writing and international markets come after the first sales.

## Rules for the whole build
1. **One phase at a time, each ending in an audit.** A phase is finished only when its audit checklist is ticked and filed at `docs/audit/toeic/phase-N.md`. The next phase starts after the owner signs off.
2. **Small audits, never one big one.** Every phase produces at most a few files, each with a named check (script or checklist) so the audit takes minutes.
3. **Content stays data** (`content/toeic/...`), validated by a script, served only through the server's gate.
4. **Original content only.** No ETS or published TOEIC material, no paraphrased real items and no questions recalled by students after sitting the test. AI-written items record their model and prompt. We are not affiliated with or endorsed by ETS (see *Brand and claims* below).
5. **Standing owner rules carry over:** "students", positive wording, max three items per breakdown, no remarks about any group of people (factual advice about the test's format and timing is fine), no raw transcripts committed.
6. **Claims stay honest.** Scores are shown as estimated ranges, never a single precise number; we never promise a score or publish before-and-after claims without pilot evidence.
7. **Reading first, honestly.** The first release is sold as a TOEIC *Reading* course, not as a complete L&R course, until Listening ships.

## The test in one table (Listening & Reading)
| Section | Part | Questions | What it tests |
|---|---|---|---|
| Listening (45 min, 100 q) | 1 Photographs | 6 | Choose the sentence that describes a picture |
| | 2 Question–response | 25 | Choose the best reply to a spoken question |
| | 3 Conversations | 39 | Short conversations, three questions each |
| | 4 Talks | 30 | Short talks, three questions each |
| Reading (75 min, 100 q) | 5 Incomplete sentences | 30 | Grammar and vocabulary in one sentence |
| | 6 Text completion | 16 | Fill gaps in an email, notice or article |
| | 7 Reading comprehension | 54 | Single and multiple passages |

Scores: Listening 5–495, Reading 5–495, total 10–990. *Verify these counts against ETS's current public test description before Phase 1 is signed off.*

## Phases

### Phase 0: Decisions (docs only)
Deliverable: this plan, plus answers to the open questions at the end.
Audit: owner confirms scope, order and price approach.

### Phase 1: Curriculum map
Deliverables:
- `docs/curriculum/toeic-question-types.md`: every part and every question type inside it (for example Part 5 word form, part of speech, preposition, vocabulary; Part 7 detail, inference, vocabulary-in-context, sentence insertion), each with a recording-queue slot like the IELTS list.
- `docs/curriculum/toeic-reading.md` and `toeic-listening.md`: the two strategy pillars (Locate and Answer) applied to TOEIC, and the Skills that support them (kept separate, cross-linked).
- `content/toeic/catalog.json` with every part and status `placeholder`.
Audit:
- Every part and question type listed once, none missing.
- Strategy and Skills kept in separate sections.
- Each breakdown has at most three items.

### Phase 2: Content standards and checker
Deliverables:
- `docs/TOEIC-CONTENT-STANDARDS.md`: the gates for Part 5, 6 and 7 items and for full tests (counts per part, difficulty ladder, workplace topics, original-content rule, source facts, blind solve, teacher review, pilot).
- `scripts/check_toeic.py`: automated gate for counts, answer validity, option spread and duplicated stems.
Audit:
- Checker runs on a sample of deliberately broken items and catches each defect.
- The owner reads the standards once.

### Phase 3: Engine made exam-neutral
Deliverables:
- A `product line` field (ielts / toeic) in catalog, store and progress, so one codebase serves both.
- Score reporting as an **estimated range** per section (Listening and Reading each on the 5 to 495 scale), plus a part-level report, in place of band scores. Original items have no equating data, so the raw-to-range table is a rough estimate, clearly labelled, and is recalibrated after a pilot large enough to support it.
- Interface strings externalised from the start (Traditional Chinese zh-TW and English), so Phase 8 translates rather than retrofits.
- Short item formats: single-sentence multiple choice (Part 5), gap-in-text (Part 6), passage plus questions (Part 7).
Audit:
- All existing IELTS tests still pass (`npm test` and the e2e scripts).
- New unit tests for score ranges and each new item format.
- Check that no student-facing text is hard-coded outside the string files.

### Phase 4: Reading vertical slice
Deliverables, in this order:
1. Part 5: strategy card, Skills (grammar and vocabulary patterns), a first set of 30 original items, a drill player.
2. Part 6: strategy card and a first set of 16 items.
3. Part 7: strategy card (Locate, then Answer), single and multiple passages, a first set.
Audit, after each part separately:
- Checker has 0 errors.
- A blind solve (independent AI solver) agrees with the key.
- Teacher checklist filed.
- End-to-end test plays the part.

### Phase 5: Reading diagnostic and Reading plan
**Gate before this phase starts:** the audio method (open question 2) is decided.
Deliverables: a 20 to 30 minute Reading diagnostic that gives a coarse level and the weakest Reading parts (about 25 to 40 items cannot support fine-grained routing, and the product says so), and a Reading-only study plan. The full target-score picker (for example 600, 750, 850) waits until Listening exists, because a total-score target is meaningless without a Listening estimate.
Audit:
- Diagnostic items are tagged by part and skill.
- Routing is tested with sample students at low, middle and high levels.
- Screens describe results as Reading level and estimated range, never a total score.

### Phase 6: Listening
Deliverables: audio for Parts 1 to 4, strategy per part (read ahead during directions and gaps, listen for signals), the Listening Skills section, and a Listening extension to the diagnostic.
The audio method was decided before Phase 5 (recorded voices, multi-accent text-to-speech with teacher review, or a mix). Whatever is chosen, check commercial licensing and cover the accents the test uses. Audio is the largest cost and risk in the project, which is why Reading ships first.
Audit:
- Every item has a transcript and a timing.
- Audio files play on a phone, including inside LINE's browser.
- Teacher listens to a sample of each part.

### Phase 7: Full mock tests
Deliverables: first full 200-question tests, a 2 hour exam screen, part-by-part reports, and the full **target-score picker and path** (for example 600, 750, 850), now that both sections exist.
Audit:
- Checker `--spec full` shows 0 errors.
- Blind solve passes.
- Teacher sign-off per test.

### Phase 8: Taiwan interface and commerce
Mostly reuse from `docs/MONETISATION.md`: Traditional Chinese interface (strings already externalised in Phase 3), NT$ prices, ECPay (or NewebPay) with e-invoicing, LINE sign-in, consent and refund screens, a TOEIC subscription and mock packs, quote form for schools and companies. If payments or LINE work would delay launch, a soft launch with manual payment is an option.
Audit:
- Every student-facing screen is checked in zh-TW.
- A test purchase flows from payment to unlock.
- Premium files are confirmed unreachable without the entitlement.

### Phase 9: Pilot and launch
Deliverables: a pilot with at least 30 students, item analysis (the admin Items page already does this), fixes, then product status moves from `draft` to `published`. Thirty students is enough to flag bad items, not to support score claims or to calibrate score ranges; plan a larger sample for that.
Audit: pilot report filed, all flagged items resolved, and the content-standards gates ticked for everything on sale.

### After launch
Speaking & Writing course, then international markets.

## Brand and claims
- Show "Not affiliated with or endorsed by ETS. TOEIC is a registered trademark of ETS." on the site, store and ads.
- Use "TOEIC" only to name the test students prepare for. Avoid "official", "real exam" and "same as the test". No logo-like styling.
- Check the product name and domain do not rely on "TOEIC" without permission, and check the Taiwan distributor's (Chung Hsin, 忠欣) policy on prep providers.
- Check Taiwan advertising and consumer-protection rules before any exam-result claim.
- Cite or remove the figures in `docs/HANDOFF.md` (298,000 test-takers in 2013, 398,000 in 2017, 2025 average 583) before using them in marketing.
- Source the "about 2 hours" and "no penalty for wrong answers" statements to ETS before publishing them to students.

## Audit file template (`docs/audit/toeic/phase-N.md`)
- Phase and date
- What was built (file list)
- Checks run (command and result)
- Defects found and how each was fixed
- Open items carried forward
- Owner sign-off (yes or no, and date)

## Open questions for the owner
1. **Reading first, then Listening?** (Recommended: yes, because Listening needs audio production.)
2. **Audio:** recorded voices, text-to-speech, or a mix? **Must be decided before Phase 5.**
3. **Pricing:** same shape as IELTS (subscription plus mock packs), at the same NT$ level?
4. **Interface:** Traditional Chinese for the whole interface from the first release, with English strategy content and Chinese glosses on key terms?
5. **One app or two?** One student login and storefront for IELTS and TOEIC (recommended), or a separate site?
6. **Recordings:** will you record TOEIC strategy conversations as you did for IELTS? They remain the source of truth for strategy content.
7. **Teacher access:** is there a teacher who can run the review and sign-off steps for TOEIC?

## Owner answers (2026-10-14)
Owner accepted all recommendations.
1. Reading first, then Listening: **yes**.
2. Audio: **undecided** (either/or question with no single recommendation). Must be settled before Phase 6.
3. Pricing: same shape as IELTS, same NT$ level: **yes**, to be confirmed in Phase 8.
4. Traditional Chinese interface from the first release: **yes**.
5. One app and login for IELTS and TOEIC: **yes**.
6. Owner records TOEIC strategy conversations: **yes**.
7. Teacher for review and sign-off: **yes**, name to be recorded.

## Plan changes after the Phase 1 and 2 review (2026-10-14)
Three independent reviewers (test expert, curriculum and pedagogy, item-writing and code) checked Phases 1 and 2. The owner approved all fixes and five plan changes:
1. Phase 5 is now a Reading diagnostic and Reading plan; the full target-score path moves to Phase 7.
2. Scores are shown as estimated ranges, recalibrated after a larger pilot.
3. The audio decision is due before Phase 5.
4. zh-TW string externalisation starts in Phase 3.
5. The first release is positioned as a Reading course.
The brand, claims and original-content guardrails above were added at the same time.
