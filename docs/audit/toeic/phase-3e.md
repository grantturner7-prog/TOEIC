# Phase 3e audit: own-branded TOEIC app on the shared engine

Date: 2026-10-15. Code: IELTS repo, branch `claude/toeic-phase3`, commit 51170fd.

## What was built
- Server: `productLine` per request (`PRODUCT_LINE` env, or hostname in `TOEIC_HOSTS`), returned by `/api/config`.
- App shell: when the product line is `toeic`, the brand mark and name, login title and tagline, student home (`#/s/toeic`), menu (Home, Diagnostic, Progress), ETS disclaimer, and document title are TOEIC; IELTS home redirects to the TOEIC home; the IELTS subscription line is hidden until TOEIC products exist.
- `#/s/toeic/progress`: TOEIC attempts and the latest diagnostic level; no total score.
- Demo engine understands TOEIC content and the product line; the single-file build takes `--line toeic` and handles default imports.
- 11 strings in both languages.

## Checks run
| Check | Result |
|---|---|
| `npm test` | 100 backend checks (new: product line by hostname) |
| `e2e-toeic.cjs` (IELTS brand) | ok |
| `PRODUCT_LINE=toeic e2e-toeic-brand.cjs` | ok: TOEIC login screen and title, student lands on the TOEIC home, menu is TOEIC only, IELTS home redirects, progress page before and after an attempt, Chinese brand and menu |
| Single-file builds opened by `file://` in Chromium | both brands run with no page errors; TOEIC build titled "TOEIC Reading", lands on `#/s/toeic` |

## Defects found and how each was fixed
- A test tried to set the Host header through fetch, which the runtime forbids; the host rule is now tested directly.
- The language toggle showed the current language in the unselected style; it now uses the app's segmented control.
- Two shell commands run in parallel shared one working directory, so a commit silently did not happen; redone with absolute paths.

## Open items carried forward
- Set and diagnostic titles come from content and stay English in Chinese mode (Phase 8).
- No TOEIC products in the store yet (Phase 8); the store page is not linked from the TOEIC brand.
- Deployment: the TOEIC hostname and the shared cookie domain (for one login across two hostnames) are decided at Phase 8.

## Owner sign-off
Pending (yes / no, date).

## Follow-up (2026-10-15): section layout
At the owner's request the TOEIC app now mirrors the IELTS layout: menu Home, Reading, Listening (Speaking and Writing are not shown because the app is unpublished and they do not exist yet). Home holds the diagnostic, a card per section and a progress summary; each section page lists its parts (strategy and Skills) and its practice sets; sets and part pages go back to their section. Checks: `npm test` (100), `e2e-toeic.cjs`, `PRODUCT_LINE=toeic e2e-toeic-brand.cjs` (menu entries, highlighting, section contents, back links, Chinese menu) all green. Found and fixed: switching language inside a practice set left the menu in English.
Open: the app is named "TOEIC Reading" while Listening is now in the menu; rename when the owner decides the product name.
