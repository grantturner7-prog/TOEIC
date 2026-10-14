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
