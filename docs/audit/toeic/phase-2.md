# Phase 2 audit: Content standards and checker

Date: 2026-10-14

## What was built
- `docs/TOEIC-CONTENT-STANDARDS.md` (item format, 10 gates, writing rules)
- `scripts/check_toeic.py` (gates 1 to 6, plus the published-needs-reviews rule)
- `scripts/test_check_toeic.py` (audit test: one valid set, 27 injected defects)

## Checks run
| Check | Result |
|---|---|
| `python3 scripts/test_check_toeic.py` | Valid 100-question Reading set passes; 27 of 27 injected defects caught |
| `python3 scripts/check_toeic_catalog.py` (Phase 1 check still passes) | OK: 200 questions, 21 slots |

Defects covered: missing or empty fields, duplicate id, bad key, repeated or empty or missing option, wrong number of blanks, wrong type for the part, unknown topic, non-original source, ETS mention, difficulty out of range, published without reviews, duplicate stem, wrong counts per set (p5, p6, p7 single and multiple), skewed difficulty ladder, skewed key letters, key-is-longest bias, p6 marker mismatch, p7 document and question count errors, bad p7 format.

## Defects found and how each was fixed
- First test run missed "key always longest". The test only lengthened keys in p5 (about 30% of questions), below the 50% limit. The checker was correct; the test now applies the defect to every question, and it is caught.

## Open items carried forward
- Gates 7 to 10 (source facts, blind solve, teacher review, pilot) are recorded by people and tools outside the script; the script only checks that the review fields say `pass` before `published`.
- The checker does not yet cover Listening parts (Phase 6) or whole 200-question tests (`--spec full`, Phase 7).
- Test fixtures are synthetic and live only in the test script; no course content exists yet.
- The owner has not yet read the standards once, as the plan's audit requires.

## Owner sign-off
Pending (yes / no, date).

## Corrections after independent review (2026-10-14)
The reviewer ran about 110 mutated inputs and confirmed the problems below. Fixed:
- Malformed input (wrong types, null, bad JSON, missing file, `{}`, `[]`) now gives a clean error, never a traceback.
- p6 markers must be [1] to [4] once each; blanks must be integers 1 to 4.
- p7 documents, kinds and question stems must be non-empty; identical documents and repeated stems in one set are errors.
- Item-level `type` is checked for p6 and p7; ids must look like `p5-0001` and start with their part; difficulty must be a real integer.
- Option values must be non-empty text; repeats compared after normalising case, punctuation and spacing; "all/none/both of the above" options are errors.
- ETS-mention check scans text values only, after Unicode and spacing normalisation (catches "Educational  Testing", E.T.S., no-break spaces).
- Review fields validated; `reviewed` and `published` now need facts, blind solve and teacher = pass and at least 3 solvers. Gate 7 now has a field (`review.facts`).
- Provenance field added (human, or AI with model and prompt reference).
- Duplicate detection uses full text with spacing and punctuation normalised.
- Option spread now runs per file; thresholds tightened (longest or shortest key at most 35%, difficulty 8 to 12 per level, relaxed rules for 12 to 23 questions).
- Negative stems and odd passage lengths give warnings.
- Standards document rewritten to match the code, including the rule against recalled or paraphrased real test items.
- Test rewritten: every injected defect must trip its intended gate (checked by message), set-size defects run under their spec, plus a fuzz pass and CLI robustness cases.

Re-check: `python3 scripts/test_check_toeic.py` -> 56 named defects, 710 fuzz corruptions, 4 CLI cases: 0 problems. The first corrections run found that `review: {}` passed on a draft; fixed by requiring all four review keys.

Still true: the checker cannot judge good English, a single best answer or plausible distractors; teacher review does. Listening items and `--spec full` are not covered yet. Reviewer's idea of a chi-square test for key spread, and similarity-based duplicate detection, are not built.

## Owner sign-off (corrections)
Pending (yes / no, date).
