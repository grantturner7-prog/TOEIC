"""Phase 1 audit check: catalog counts, type slots and docs agree."""
import json, re, sys
cat = json.load(open("content/toeic/catalog.json"))
errs = []
total = 0
slots = set()
for s in cat["sections"]:
    n = sum(p["questions"] for p in s["parts"])
    if n != s["questions"]:
        errs.append(f"{s['id']}: parts sum {n} != {s['questions']}")
    total += n
    for p in s["parts"]:
        if len(p["types"]) > 3:
            errs.append(f"{p['id']}: more than 3 types")
        slots.update(p["types"])
if total != 200:
    errs.append(f"total {total} != 200")
doc = open("docs/curriculum/toeic-question-types.md").read()
doc_slots = set(re.findall(r"TQ-\d-\d", doc))
if doc_slots != slots:
    errs.append(f"slot mismatch: {sorted(doc_slots ^ slots)}")
for f in ("toeic-reading", "toeic-listening"):
    t = open(f"docs/curriculum/{f}.md").read()
    if "## Strategy" not in t or "## Skills" not in t:
        errs.append(f"{f}: Strategy/Skills sections missing")
print("\n".join(errs) or f"OK: {total} questions, {len(slots)} slots")
sys.exit(1 if errs else 0)
