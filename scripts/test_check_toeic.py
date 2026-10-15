"""Audit test for check_toeic.py.

1. A valid synthetic Reading set must pass.
2. Every injected defect must be caught by the INTENDED gate (message must contain the
   expected text), under the spec that is meant to catch it.
3. Fuzz: setting any field of any item to a wrong-typed value must never crash the checker
   and must always produce at least one error.
Fixtures are synthetic test data, not course content.
"""
import copy, os, subprocess, sys, tempfile, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_toeic import check, check_files

L = ["A", "B", "C", "D"]
FM = {"single": 1, "double": 2, "triple": 3}


def opts(n, key_idx=None, extra=""):
    o = {k: f"option{n}{k.lower()}" for k in L}
    if key_idx is not None:
        o[L[key_idx]] += extra
    return o


def base(i, part, typ, n):
    return {"id": f"{part}-{i:04d}", "part": part, "type": typ, "difficulty": n % 3 + 1,
            "topic": "office", "source": "original", "provenance": {"method": "human"},
            "explanation": "Because.", "status": "draft",
            "review": {"blind_solve": None, "blind_solvers": 0, "facts": None, "teacher": None}}


def p5(n):
    it = base(n, "p5", f"TQ-5-{n % 3 + 1}", n)
    it.update(stem=f"Synthetic sentence {n} needs a ____ word.", options=opts(n), answer=L[n % 4])
    return it


def q6(n, b):
    return {"blank": b, "type": f"TQ-6-{b % 3 + 1}", "options": opts(n * 10 + b), "answer": L[(n + b) % 4]}


def p6(n):
    it = base(n, "p6", "TQ-6-1", n)
    it.update(text=f"Synthetic notice {n}: [1] a [2] b [3] c [4] d", questions=[q6(n, b) for b in (1, 2, 3, 4)])
    return it


def q7(n, k):
    return {"stem": f"Q{n}.{k}?", "type": f"TQ-7-{k % 3 + 1}", "options": opts(n * 10 + k), "answer": L[(n + k) % 4]}


def p7(n, fmt, nq):
    it = base(n, "p7", "TQ-7-1", n)
    it.update(format=fmt, documents=[{"kind": "email", "text": f"Synthetic document {n}-{d}"} for d in range(FM[fmt])],
              questions=[q7(n, k) for k in range(nq)])
    return it


V = {"accent": "US", "gender": "W"}
def lbase(i, part, typ, n):
    it = base(i, part, typ, n); it.update(timing={"audioSeconds": 30}, audio=None); return it

def p1(n):
    it = lbase(n, "p1", f"TQ-1-{n % 3 + 1}", n)
    it.update(photo={"brief": f"Synthetic photo {n} of an office"}, speaker={"accent": ["US", "UK", "AU", "CA"][n % 4], "gender": "M"}, options=opts(n), answer=L[n % 4]); return it

def p2(n):
    it = lbase(n, "p2", f"TQ-2-{n % 3 + 1}", n)
    o = {k: f"reply{n}{k.lower()}" for k in "ABC"}
    it.update(prompt=f"Synthetic question {n}?", speakers={"prompt": {"accent": "UK", "gender": "W"}, "response": {"accent": "US", "gender": "M"}}, options=o, answer="ABC"[n % 3]); return it

def seg(sp, text, acc="US"): return {"speaker": sp, "accent": acc, "gender": "M" if sp.startswith("Man") else "W", "text": text}
def q34(n, k, part):
    return {"stem": f"Q{n}.{k}?", "type": f"TQ-{part[1]}-{k % 3 + 1}", "options": opts(n * 10 + k), "answer": L[(n + k) % 4]}
def p3(n):
    it = lbase(n, "p3", "TQ-3-1", n)
    words = " ".join(["word"] * 20)
    it.update(script=[seg("Man", f"Hello {n} {words}"), seg("Woman", words, "AU"), seg("Man", words), seg("Woman", words, "AU")], questions=[q34(n, k, "p3") for k in range(3)])
    if n == 0: it["script"].append(seg("Man 2", words, "CA"))
    if n < 2: it["graphic"] = {"kind": "table", "rows": [["Room", "Time"], ["A", "9:00"]]}
    return it
def p4(n):
    it = lbase(n, "p4", "TQ-4-1", n)
    words = " ".join(["word"] * 40)
    it.update(script=[seg("Woman", f"Talk {n} {words}", "UK"), seg("Woman", words, "UK")], questions=[q34(n, k, "p4") for k in range(3)])
    if n < 2: it["graphic"] = {"kind": "schedule", "rows": [["Day", "Event"], ["Mon", "Opening"]]}
    return it

def good_listening():
    return [p1(n) for n in range(6)] + [p2(n) for n in range(25)] + [p3(n) for n in range(13)] + [p4(n) for n in range(10)]

def good_reading():
    items = [p5(n) for n in range(30)]
    items += [p6(n) for n in range(4)]
    items += [p7(n, "single", 3) for n in range(9)] + [p7(9, "single", 2)]
    items += [p7(10 + n, "double" if n % 2 else "triple", 5) for n in range(5)]
    return items


def find(items, part, idx=0):
    return [x for x in items if x["part"] == part][idx]


def all_questions(items):
    out = []
    for x in items:
        out += [x] if x["part"] == "p5" else x["questions"]
    return out


def set_(d, k, v):
    d[k] = v


def pub(it):
    it["status"] = "published"


# name: (mutation, spec, expected text in an error message)
M = {
    "missing explanation field": (lambda s: find(s, "p5").pop("explanation"), "none", "missing field explanation"),
    "empty explanation": (lambda s: set_(find(s, "p5"), "explanation", "  "), "none", "explanation must be"),
    "missing provenance": (lambda s: find(s, "p5").pop("provenance"), "none", "missing field provenance"),
    "ai provenance without model": (lambda s: set_(find(s, "p5"), "provenance", {"method": "ai"}), "none", "ai provenance needs"),
    "duplicate id": (lambda s: set_(find(s, "p5", 1), "id", find(s, "p5", 0)["id"]), "none", "duplicate id"),
    "id wrong prefix": (lambda s: set_(find(s, "p5"), "id", "p7-9999"), "none", "id must look like"),
    "answer not A-D": (lambda s: set_(find(s, "p5"), "answer", "E"), "none", "answer must be"),
    "repeated option": (lambda s: find(s, "p5")["options"].update(B=find(s, "p5")["options"]["A"]), "none", "repeated option"),
    "repeated option (hyphen/spacing)": (lambda s: find(s, "p5")["options"].update(A="on time", B="on-time"), "none", "repeated option"),
    "empty option": (lambda s: find(s, "p5")["options"].update(C=""), "none", "non-empty text"),
    "non-text option": (lambda s: find(s, "p5")["options"].update(C=5), "none", "non-empty text"),
    "missing option D": (lambda s: find(s, "p5")["options"].pop("D"), "none", "exactly A, B, C, D"),
    "none of the above option": (lambda s: find(s, "p5")["options"].update(D="None of the above"), "none", "of the above"),
    "p5 two blanks": (lambda s: set_(find(s, "p5"), "stem", "A ____ and ____ here."), "none", "exactly one ____"),
    "p5 no blank": (lambda s: set_(find(s, "p5"), "stem", "No blank here."), "none", "exactly one ____"),
    "type from wrong part": (lambda s: set_(find(s, "p5"), "type", "TQ-7-1"), "none", "not valid"),
    "p6 item type from wrong part": (lambda s: set_(find(s, "p6"), "type", "TQ-5-1"), "none", "item type"),
    "p6 item type missing": (lambda s: find(s, "p6").pop("type"), "none", "item type"),
    "p7 item type from wrong part": (lambda s: set_(find(s, "p7"), "type", "TQ-5-1"), "none", "item type"),
    "unknown topic": (lambda s: set_(find(s, "p5"), "topic", "sports"), "none", "topic"),
    "source not original": (lambda s: set_(find(s, "p5"), "source", "book"), "none", "source must be"),
    "mentions ETS": (lambda s: set_(find(s, "p5"), "explanation", "Copied from an ETS test."), "none", "mentions ETS"),
    "mentions Educational  Testing (two spaces)": (lambda s: set_(find(s, "p5"), "explanation", "From Educational  Testing Service."), "none", "mentions ETS"),
    "mentions E.T.S.": (lambda s: set_(find(s, "p5"), "explanation", "From E.T.S. materials."), "none", "mentions ETS"),
    "mentions ETS with no-break space": (lambda s: set_(find(s, "p5"), "explanation", "Educational Testing"), "none", "mentions ETS"),
    "difficulty out of range": (lambda s: set_(find(s, "p5"), "difficulty", 5), "none", "difficulty"),
    "difficulty is True": (lambda s: set_(find(s, "p5"), "difficulty", True), "none", "difficulty"),
    "review value invalid": (lambda s: find(s, "p5")["review"].update(teacher="maybe"), "none", "review.teacher"),
    "published without reviews": (lambda s: pub(find(s, "p5")), "none", "needs blind_solve"),
    "published with only 1 solver": (lambda s: (pub(find(s, "p5")), find(s, "p5")["review"].update(blind_solve="pass", facts="pass", teacher="pass", blind_solvers=1)), "none", "needs blind_solve"),
    "reviewed with null reviews": (lambda s: set_(find(s, "p5"), "status", "reviewed"), "none", "needs blind_solve"),
    "duplicate p5 stem": (lambda s: set_(find(s, "p5", 1), "stem", find(s, "p5", 0)["stem"]), "none", "duplicate p5"),
    "duplicate p5 stem (extra spaces/punct)": (lambda s: set_(find(s, "p5", 1), "stem", find(s, "p5", 0)["stem"].replace(" ", "  ").replace(".", "!")), "none", "duplicate p5"),
    "duplicate p6 passage": (lambda s: set_(find(s, "p6", 1), "text", find(s, "p6", 0)["text"]), "none", "duplicate p6"),
    "duplicate p7 documents": (lambda s: set_(find(s, "p7", 1), "documents", copy.deepcopy(find(s, "p7", 0)["documents"])), "none", "duplicate p7"),
    "only 29 p5 items": (lambda s: s.remove(find(s, "p5")), "reading", "p5 needs 30"),
    "difficulty ladder skewed": (lambda s: [x.update(difficulty=1) for x in s if x["part"] == "p5"], "reading", "difficulty 2 has 0"),
    "difficulty ladder 5/5/20": (lambda s: [x.update(difficulty=3 if x["id"] > "p5-0009" else (1 if x["id"] < "p5-0005" else 2)) for x in s if x["part"] == "p5"], "reading", "needs 8 to 12"),
    "answer spread: all A": (lambda s: [q.update(answer="A") for q in all_questions(s)], "none", "spread: key"),
    "key always longest": (lambda s: [q["options"].update({q["answer"]: q["options"][q["answer"]] + "xxxxxxxxxx"}) for q in all_questions(s)], "none", "longest option"),
    "key longest in 40% of questions": (lambda s: [q["options"].update({q["answer"]: q["options"][q["answer"]] + "xxxxxxxxxx"}) for i, q in enumerate(all_questions(s)) if i % 5 < 2], "none", "longest option"),
    "key always shortest": (lambda s: [q["options"].update({k: v + "xxxxxxxxxx" for k, v in q["options"].items() if k != q["answer"]}) for q in all_questions(s)], "none", "shortest option"),
    "p6 marker mismatch": (lambda s: set_(find(s, "p6"), "text", "Notice: [1] a [2] b [3] c"), "none", "markers [1]-[4]"),
    "p6 repeated markers [1][1][2][2]": (lambda s: (set_(find(s, "p6"), "text", "n [1] a [1] b [2] c [2] d"), [q.update(blank=b) for q, b in zip(find(s, "p6")["questions"], (1, 1, 2, 2))]), "none", "markers [1]-[4]"),
    "p6 markers 5-8": (lambda s: (set_(find(s, "p6"), "text", "n [5] a [6] b [7] c [8] d"), [q.update(blank=b) for q, b in zip(find(s, "p6")["questions"], (5, 6, 7, 8))]), "none", "markers [1]-[4]"),
    "p6 only 3 passages": (lambda s: s.remove(find(s, "p6")), "reading", "p6 needs 4 passages"),
    "p7 document count wrong": (lambda s: set_(find(s, "p7", 10), "documents", [{"kind": "email", "text": "x"}]), "none", "1/2/3 documents"),
    "p7 document with empty text": (lambda s: find(s, "p7", 0)["documents"][0].update(text="  "), "none", "kind and text"),
    "p7 question with empty stem": (lambda s: find(s, "p7", 0)["questions"][0].update(stem=""), "none", "stem must be"),
    "p7 repeated stem in one set": (lambda s: find(s, "p7", 0)["questions"][1].update(stem=find(s, "p7", 0)["questions"][0]["stem"]), "none", "repeated question stem"),
    "p7 question wrong type": (lambda s: find(s, "p7", 0)["questions"][0].update(type="TQ-5-1"), "none", "not valid"),
    "p7 multi set with 4 questions": (lambda s: find(s, "p7", 10)["questions"].pop(), "none", "exactly 5 questions"),
    "p7 single with 5 questions": (lambda s: find(s, "p7", 0)["questions"].extend([q7(99, k) for k in range(2)]), "none", "needs 2-4 questions"),
    "p7 single total 28": (lambda s: find(s, "p7", 0)["questions"].pop(), "reading", "must be 29"),
    "p7 only 4 multiple-passage sets": (lambda s: s.remove(find(s, "p7", 10)), "reading", "5 multiple-passage sets"),
    "p7 bad format": (lambda s: set_(find(s, "p7", 0), "format", "quad"), "none", "single/double/triple"),
}


def corrupt_variants():
    """Yield (label, items) where one field of one item (or nested object) holds a wrong value."""
    bad_values = [None, [], {}, 5, "", ["x"], {"x": 1}]
    good = good_reading() + good_listening()
    picks = [find(good, "p5"), find(good, "p6"), find(good, "p7"), find(good, "p7", 10), find(good, "p1"), find(good, "p2"), find(good, "p3"), find(good, "p4")]
    for pick in picks:
        targets = [("item", pick)]
        if "questions" in pick:
            targets.append(("question", pick["questions"][0]))
            targets.append(("question options", pick["questions"][0]["options"]))
        if "documents" in pick:
            targets.append(("document", pick["documents"][0]))
        if "script" in pick:
            targets.append(("segment", pick["script"][0]))
        if "photo" in pick:
            targets.append(("photo", pick["photo"]))
        if "speakers" in pick:
            targets.append(("speakers", pick["speakers"]))
        if "timing" in pick:
            targets.append(("timing", pick["timing"]))
        targets.append(("review", pick["review"]))
        targets.append(("options", pick["options"]) if "options" in pick else ("provenance", pick["provenance"]))
        for where, obj in targets:
            for key in list(obj):
                for bad in bad_values:
                    if obj[key] == bad and type(obj[key]) is type(bad):
                        continue
                    if key == "blind_solvers" and bad == 5:
                        continue  # a valid value
                    if key == "audioSeconds" and bad == 5:
                        continue  # a valid value
                    if key == "graphic" and bad is None:
                        continue  # no graphic is allowed
                    items = copy.deepcopy(good)
                    # locate same object in the copy by path
                    idx = good.index(pick)
                    cp = items[idx]
                    cobj = {"item": cp, "question": cp.get("questions", [None])[0], "document": (cp.get("documents") or [None])[0],
                            "review": cp["review"], "options": cp.get("options"), "provenance": cp["provenance"],
                            "question options": (cp.get("questions", [{}])[0] or {}).get("options"),
                            "segment": (cp.get("script") or [None])[0], "photo": cp.get("photo"), "speakers": cp.get("speakers"), "timing": cp.get("timing")}[where]
                    cobj[key] = bad
                    yield f"{pick['id']} {where}.{key} = {bad!r}", items
    for bad in (None, 5, "x", [], ["x"], {}):
        items = copy.deepcopy(good)
        items[0] = bad
        yield f"item replaced by {bad!r}", items
        items = copy.deepcopy(good)
        items[len(items) - 1]["questions"] = [bad] * 5
        yield f"p7 questions replaced by [{bad!r}]*5", items


ML = {
    "p1 missing photo brief": (lambda s: find(s, "p1").pop("photo"), "none", "photo.brief"),
    "p1 bad accent": (lambda s: find(s, "p1")["speaker"].update(accent="IE"), "none", "accent"),
    "p1 three options only": (lambda s: find(s, "p1")["options"].pop("D"), "none", "exactly A, B, C, D"),
    "p2 four options": (lambda s: find(s, "p2")["options"].update(D="extra"), "none", "exactly A, B, C"),
    "p2 answer D": (lambda s: set_(find(s, "p2"), "answer", "D"), "none", "answer must be one of A-C"),
    "p2 missing prompt": (lambda s: set_(find(s, "p2"), "prompt", ""), "none", "spoken prompt"),
    "p2 missing response voice": (lambda s: find(s, "p2")["speakers"].pop("response"), "none", "response: needs accent"),
    "p3 one speaker": (lambda s: [x.update(speaker="Man") for x in find(s, "p3", 1)["script"]], "none", "2 speakers"),
    "p3 two questions": (lambda s: find(s, "p3")["questions"].pop(), "none", "exactly 3 questions"),
    "p3 segment without text": (lambda s: find(s, "p3")["script"][0].update(text=" "), "none", "needs speaker and text"),
    "p3 graphic without rows": (lambda s: set_(find(s, "p3"), "graphic", {"kind": "table", "rows": []}), "none", "graphic"),
    "p4 two speakers": (lambda s: find(s, "p4")["script"][1].update(speaker="Man"), "none", "exactly one speaker"),
    "p4 wrong type for part": (lambda s: find(s, "p4")["questions"][0].update(type="TQ-3-1"), "none", "not valid"),
    "listening timing missing": (lambda s: find(s, "p1").pop("timing"), "none", "timing.audioSeconds"),
    "listening timing zero": (lambda s: set_(find(s, "p1"), "timing", {"audioSeconds": 0}), "none", "timing.audioSeconds"),
    "listening audio wrong type": (lambda s: set_(find(s, "p1"), "audio", 5), "none", "audio must be null"),
    "published without audio": (lambda s: (pub(find(s, "p1")), find(s, "p1")["review"].update(blind_solve="pass", facts="pass", teacher="pass", blind_solvers=3)), "none", "without its audio"),
    "duplicate p2 prompt": (lambda s: set_(find(s, "p2", 1), "prompt", find(s, "p2", 0)["prompt"]), "none", "duplicate p2"),
    "duplicate p4 script": (lambda s: set_(find(s, "p4", 1), "script", copy.deepcopy(find(s, "p4", 0)["script"])), "none", "duplicate p4"),
    "p2 keys all A": (lambda s: [x.update(answer="A") for x in s if x["part"] == "p2"], "none", "3-option keys"),
    "only 5 p1 items": (lambda s: s.remove(find(s, "p1")), "listening", "p1 needs 6"),
    "p2 ladder skewed": (lambda s: [x.update(difficulty=1) for x in s if x["part"] == "p2"], "listening", "needs 6 to 11"),
    "12 p3 conversations": (lambda s: s.remove(find(s, "p3", 5)), "listening", "p3 needs 13"),
    "no three-speaker p3": (lambda s: find(s, "p3", 0)["script"].pop(), "listening", "three-speaker"),
    "only one p3 graphic": (lambda s: find(s, "p3", 1).pop("graphic"), "listening", "graphic"),
    "9 p4 talks": (lambda s: s.remove(find(s, "p4", 9)), "listening", "p4 needs 10"),
    "only one p4 graphic": (lambda s: find(s, "p4", 1).pop("graphic"), "listening", "graphic"),
    "only two accents": (lambda s: [v.update(accent="US") for x in s for v in ([x.get("speaker")] + list((x.get("speakers") or {}).values()) + list(x.get("script") or [])) if isinstance(v, dict) and v.get("accent") == "AU"] and [v.update(accent="UK") for x in s for v in ([x.get("speaker")] + list(x.get("script") or [])) if isinstance(v, dict) and v.get("accent") == "CA"], "listening", "at least 3 of the 4 accents"),
}


def main():
    problems = 0
    errs = check(good_reading(), "reading")
    print("valid set:", "PASS" if not errs else f"FAIL {errs[:3]}")
    problems += bool(errs)
    errs = check(good_listening(), "listening")
    print("valid listening set:", "PASS" if not errs else f"FAIL {errs[:3]}")
    problems += bool(errs)
    for name, (fn, spec, expect) in ML.items():
        s = good_listening(); fn(s); errs = check(s, spec)
        hit = [e for e in errs if expect in e]
        status = "caught" if hit else ("WRONG GATE" if errs else "MISSED")
        problems += not hit
        print(f"{status:10} listening: {name}" + (f"  -> {hit[0]}" if hit else (f"  -> {errs[0]}" if errs else "")))

    for name, (fn, spec, expect) in M.items():
        s = good_reading()
        fn(s)
        errs = check(s, spec)
        hit = [e for e in errs if expect in e]
        status = "caught" if hit else ("WRONG GATE" if errs else "MISSED")
        problems += not hit
        print(f"{status:10} {name}" + (f"  -> {hit[0]}" if hit else (f"  -> {errs[0]}" if errs else "")))

    crashes = unflagged = n = 0
    for label, items in corrupt_variants():
        n += 1
        try:
            errs = check(items, "none")
        except Exception as e:  # noqa
            crashes += 1
            print(f"CRASH      {label}: {type(e).__name__}: {e}")
            continue
        if not errs:
            unflagged += 1
            print(f"UNFLAGGED  {label}")
    problems += crashes + unflagged
    print(f"fuzz: {n} corruptions, {crashes} crashes, {unflagged} not flagged")

    # CLI robustness: bad inputs give a clean message and exit 1, never a traceback.
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_toeic.py")
    with tempfile.TemporaryDirectory() as d:
        cases = {"missing file": os.path.join(d, "nope.json"), "bad json": None, "empty object": None, "empty list": None}
        for label, path in cases.items():
            if path is None:
                path = os.path.join(d, label.replace(" ", "_") + ".json")
                open(path, "w").write({"bad json": "{not json", "empty object": "{}", "empty list": "[]"}[label])
            r = subprocess.run([sys.executable, script, path], capture_output=True, text=True)
            ok = r.returncode == 1 and "Traceback" not in r.stderr
            problems += not ok
            print(f"{'clean' if ok else 'BAD CLI':10} CLI {label}")

    print(f"\n{len(M)} reading + {len(ML)} listening named defects, {n} fuzz corruptions, 4 CLI cases: {problems} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
