# Phase 3d audit: interface strings (Traditional Chinese and English)

Date: 2026-10-14. Code: IELTS repo, branch `claude/toeic-phase3`, commit 6f04baa.

## What was built
- `app/js/strings.js` (`t()`, language choice remembered, Chinese by default for Chinese browsers), `app/js/strings/en.js`, `app/js/strings/zh-TW.js` (70 keys including all 7 part names and all 21 question-type names).
- `scripts/check-strings.mjs`, now part of `npm test`.

## Checks run
| Check | Result |
|---|---|
| `node scripts/check-strings.mjs` | ok |
| Covered | both languages have identical keys, none empty, identical `{placeholders}`; Chinese text is Chinese; unknown key never blanks the screen; every `t('key')` in the TOEIC view exists (including keys built with a variable); **no hard-coded readable text between tags in the TOEIC view**; the detector itself is tested against English, Chinese, nested templates and plain JavaScript |
| End to end | Chinese results screen and Chinese default for a Chinese browser (see 3c) |

## Defects found and how each was fixed
- First detector was too crude (it flagged `=>` in code). It now reads only template literals, and has its own tests.
- It caught one key built by string concatenation in the view; changed to a template literal so it can be verified.

## Open items carried forward
- **The Chinese is a draft translation.** A native-speaking teacher must review all 70 strings before launch.
- Only the TOEIC view is covered. The rest of the app still has its own mixed English and Chinese text; moving it onto the string files is Phase 8 work.

## Owner sign-off
Pending (yes / no, date).
