# Phase 3a audit: product line, gate and sample sets

Date: 2026-10-14. Code: `grantturner7-prog/IELTS`, branch `claude/toeic-phase3`, commit a6c0091.

## What was built
- `server/db.js`: `attempts.product_line` column (default `ielts`), added automatically to existing databases.
- `server/gate.js`: TOEIC set index and rule; products default to `productLine: "ielts"`; **default-deny for any file under `toeic/` that no rule opens**.
- `server/api.js`, `server/state.js`: attempts accept and return a product line; a set id only counts for its own line; premium sets need the product.
- `app/js/store.js`, `app/js/report.js`: IELTS screens and IELTS item analysis ask for IELTS attempts only.
- `content/toeic/`: `catalog.json` (copied from this project), `scoring.json`, `sets/index.json`, two sample sets (one free, one premium).

## Checks run
| Check | Result |
|---|---|
| `npm test` backend suite | 93 passed (77 existing + 16 new) |
| New checks cover | open catalog and scoring; set index; free set open; premium set closed to students and anonymous, open to teachers and owners; unknown set; an unlisted file under `toeic/` closed to students; admin access override; products default to IELTS; attempts tagged by line; unknown line refused; cross-line set ids refused; premium attempts need the product; an old database gains the column and old attempts stay IELTS |
| `python3 scripts/check_toeic.py` on both sample sets | OK: 9 items |

## Defects found and how each was fixed
- First draft of an access-override test expected a set without a `productId` to lock. That matches how IELTS passages already work (premium needs a product), so the test was changed, not the gate.

## Open items carried forward
- Real TOEIC products (prices, packs) are Phase 8; none added to the store yet.
- Teacher and admin screens do not show TOEIC attempts yet (they only ask for IELTS).
- Sample items record provenance as "AI assistant (draft sample)" without a model name, because the working rules for this session do not allow a model identifier in repository files. Fill in the real model name if the owner wants it recorded.

## Owner sign-off
Yes, 2026-10-14 (owner said "keep going").
