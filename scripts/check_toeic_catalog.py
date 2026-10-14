"""Phase 1 audit check: catalog counts, type slots and curriculum docs agree.
Run from any directory."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda p: open(os.path.join(ROOT, p), encoding="utf-8").read()
cat = json.loads(rd("content/toeic/catalog.json"))
errs, total, slots, expected = [], 0, set(), {"listening": 100, "reading": 100}
for s in cat["sections"]:
    n = sum(p["questions"] for p in s["parts"])
    if n != s["questions"] or n != expected[s["id"]]:
        errs.append(f"{s['id']}: parts sum {n}, declared {s['questions']}, expected {expected[s['id']]}")
    total += n
    for p in s["parts"]:
        if not 1 <= len(p["types"]) <= 3:
            errs.append(f"{p['id']}: needs 1 to 3 types, has {len(p['types'])}")
        if any(not t.startswith(f"TQ-{p['id'][1]}-") for t in p["types"]):
            errs.append(f"{p['id']}: type slot does not belong to this part")
        if p["status"] != "placeholder" and p["status"] not in ("draft", "published"):
            errs.append(f"{p['id']}: bad status {p['status']}")
        slots.update(p["types"])
        if p["id"] == "p6" and p["texts"] * p["blanksPerText"] != p["questions"]:
            errs.append("p6: texts x blanks must equal questions")
        if p["id"] == "p7" and p["singleQuestions"] + p["multipleQuestions"] != p["questions"]:
            errs.append("p7: 29 + 25 must equal 54")
if total != 200:
    errs.append(f"total {total} != 200")
doc = rd("docs/curriculum/toeic-question-types.md")
rows = set(re.findall(r"^\| (TQ-\d-\d) \|", doc, re.M))
if rows != slots:
    errs.append(f"question-types slot mismatch: {sorted(rows ^ slots)}")
for f in ("toeic-reading", "toeic-listening"):
    t = rd(f"docs/curriculum/{f}.md")
    for h in ("## Strategy", "## Skills"):
        if h not in t:
            errs.append(f"{f}: missing section {h}")
    mentioned = set(re.findall(r"TQ-\d-\d", t))
    ids = {x for x in mentioned}
    # Skills tables name ranges like 'TQ-5-1 to TQ-5-3'; every part's first and last slot must appear
    part_nums = "567" if f.endswith("reading") else "1234"
    for n in part_nums:
        for k in (1, 3):
            if f"TQ-{n}-{k}" not in ids:
                errs.append(f"{f}: Skills table does not link TQ-{n}-{k}")
print("\n".join(errs) or f"OK: {total} questions, {len(slots)} slots")
sys.exit(1 if errs else 0)
