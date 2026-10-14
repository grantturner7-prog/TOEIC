"""Content gate for TOEIC Reading items (Phase 2).

Usage: python3 scripts/check_toeic.py [--spec none|p5|p6|p7|reading] FILE.json [FILE.json ...]
Exit code 1 if any error is found. See docs/TOEIC-CONTENT-STANDARDS.md.
"""
import argparse, json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LETTERS = ["A", "B", "C", "D"]
TOPICS = {"office", "hr", "finance", "travel", "manufacturing", "retail",
          "dining", "health", "housing", "technology", "marketing", "events"}
STATUSES = {"draft", "reviewed", "published"}
PARTS = {"p5", "p6", "p7"}
FORMATS = {"single": 1, "double": 2, "triple": 3}


def catalog_types():
    cat = json.load(open(os.path.join(ROOT, "content/toeic/catalog.json")))
    return {p["id"]: set(p["types"]) for s in cat["sections"] for p in s["parts"]}


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()


def check_options(where, q, types_for_part, errs):
    opts = q.get("options")
    if not isinstance(opts, dict) or sorted(opts) != LETTERS:
        errs.append(f"{where}: options must be exactly A, B, C, D")
        return
    vals = [str(opts[k]).strip() for k in LETTERS]
    if any(not v for v in vals):
        errs.append(f"{where}: empty option")
    if len({v.lower() for v in vals}) != 4:
        errs.append(f"{where}: repeated option text")
    if q.get("answer") not in LETTERS:
        errs.append(f"{where}: answer must be one of A-D")
    if q.get("type") not in types_for_part:
        errs.append(f"{where}: type {q.get('type')!r} not valid for this part")


def check_common(it, errs, seen_ids):
    i = it.get("id", "<no id>")
    for f in ("id", "part", "type", "difficulty", "topic", "source", "explanation", "status", "review"):
        if f not in it:
            errs.append(f"{i}: missing field {f}")
    if i in seen_ids:
        errs.append(f"{i}: duplicate id")
    seen_ids.add(i)
    if it.get("part") not in PARTS:
        errs.append(f"{i}: part must be one of {sorted(PARTS)}")
    if it.get("difficulty") not in (1, 2, 3):
        errs.append(f"{i}: difficulty must be 1, 2 or 3")
    if it.get("topic") not in TOPICS:
        errs.append(f"{i}: topic {it.get('topic')!r} not in allowed list")
    if it.get("source") != "original":
        errs.append(f"{i}: source must be 'original'")
    if not str(it.get("explanation", "")).strip():
        errs.append(f"{i}: empty explanation")
    if it.get("status") not in STATUSES:
        errs.append(f"{i}: status must be one of {sorted(STATUSES)}")
    blob = json.dumps(it).lower()
    if re.search(r"\bets\b|educational testing", blob):
        errs.append(f"{i}: mentions ETS (originality rule)")
    rev = it.get("review") or {}
    if it.get("status") == "published" and not (rev.get("blind_solve") == "pass" and rev.get("teacher") == "pass"):
        errs.append(f"{i}: published without blind_solve and teacher = pass")


def check_item(it, types, errs):
    i = it.get("id", "<no id>")
    part = it.get("part")
    tp = types.get(part, set())
    qs = []   # (where, question dict) for every keyed question
    key = None
    if part == "p5":
        stem = it.get("stem", "")
        if stem.count("____") != 1:
            errs.append(f"{i}: p5 stem must contain exactly one ____")
        check_options(i, it, tp, errs)
        qs.append(it)
        key = norm(stem)
    elif part == "p6":
        text = it.get("text", "")
        markers = sorted(re.findall(r"\[(\d+)\]", text))
        questions = it.get("questions", [])
        if markers != sorted(str(q.get("blank")) for q in questions) or len(markers) != 4:
            errs.append(f"{i}: p6 needs markers [1]-[4] in text matching 4 questions")
        for q in questions:
            check_options(f"{i}#{q.get('blank')}", q, tp, errs)
            qs.append(q)
        key = norm(text)[:80]
    elif part == "p7":
        fmt = it.get("format")
        docs = it.get("documents", [])
        if fmt not in FORMATS or len(docs) != FORMATS[fmt]:
            errs.append(f"{i}: p7 format must be single/double/triple with 1/2/3 documents")
        questions = it.get("questions", [])
        n = len(questions)
        if fmt == "single" and not 2 <= n <= 4:
            errs.append(f"{i}: single passage needs 2-4 questions, has {n}")
        if fmt in ("double", "triple") and n != 5:
            errs.append(f"{i}: multiple-passage set needs exactly 5 questions, has {n}")
        for k, q in enumerate(questions, 1):
            check_options(f"{i}#{k}", q, tp, errs)
            qs.append(q)
        key = norm(docs[0].get("text", ""))[:80] if docs else None
    return qs, key


def set_checks(items, all_qs, errs):
    # option spread / longest-option bias
    if len(all_qs) >= 12:
        keys = [q.get("answer") for q in all_qs if q.get("answer") in LETTERS]
        cnt = Counter(keys)
        for L in LETTERS:
            share = cnt[L] / len(keys)
            if not 0.10 <= share <= 0.40:
                errs.append(f"spread: key {L} is {share:.0%} of keys (allowed 10%-40%)")
        longest = 0
        for q in all_qs:
            o = q.get("options") or {}
            if q.get("answer") in o:
                lens = {k: len(str(v)) for k, v in o.items()}
                if lens[q["answer"]] == max(lens.values()) and list(lens.values()).count(max(lens.values())) == 1:
                    longest += 1
        if longest / len(all_qs) > 0.50:
            errs.append(f"spread: key is the longest option in {longest/len(all_qs):.0%} of questions (max 50%)")


def spec_checks(spec, items, errs):
    by = {p: [x for x in items if x.get("part") == p] for p in PARTS}
    def need_p5():
        if len(by["p5"]) != 30:
            errs.append(f"spec: p5 needs 30 items, has {len(by['p5'])}")
        lad = Counter(x.get("difficulty") for x in by["p5"])
        for d in (1, 2, 3):
            if lad[d] < 5:
                errs.append(f"spec: p5 difficulty {d} has {lad[d]} items (needs at least 5)")
    def need_p6():
        q = sum(len(x.get("questions", [])) for x in by["p6"])
        if len(by["p6"]) != 4 or q != 16:
            errs.append(f"spec: p6 needs 4 passages / 16 questions, has {len(by['p6'])} / {q}")
    def need_p7():
        single = sum(len(x.get("questions", [])) for x in by["p7"] if x.get("format") == "single")
        multi = [x for x in by["p7"] if x.get("format") in ("double", "triple")]
        mq = sum(len(x.get("questions", [])) for x in multi)
        if single != 29:
            errs.append(f"spec: p7 single-passage questions must be 29, has {single}")
        if len(multi) != 5 or mq != 25:
            errs.append(f"spec: p7 needs 5 multiple-passage sets / 25 questions, has {len(multi)} / {mq}")
    if spec in ("p5", "reading"): need_p5()
    if spec in ("p6", "reading"): need_p6()
    if spec in ("p7", "reading"): need_p7()


def check(items, spec="none"):
    errs, seen_ids, all_qs, keys = [], set(), [], Counter()
    types = catalog_types()
    for it in items:
        check_common(it, errs, seen_ids)
        qs, key = check_item(it, types, errs)
        all_qs.extend(qs)
        if key:
            keys[key] += 1
    for k, n in keys.items():
        if n > 1:
            errs.append(f"duplicate stem/passage: {k[:50]!r} appears {n} times")
    set_checks(items, all_qs, errs)
    if spec != "none":
        spec_checks(spec, items, errs)
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="none", choices=["none", "p5", "p6", "p7", "reading"])
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    items = []
    for f in a.files:
        items += json.load(open(f))["items"]
    errs = check(items, a.spec)
    print("\n".join(errs) if errs else f"OK: {len(items)} items, spec={a.spec}")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
