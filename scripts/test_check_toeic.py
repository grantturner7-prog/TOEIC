"""Audit test for check_toeic.py: a valid synthetic set must pass, and every
injected defect must be caught. Fixtures are synthetic test data, not course content."""
import copy, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_toeic import check

L = ["A", "B", "C", "D"]

def opts(n, key_idx=None, long_key=False):
    o = {k: f"option{n}{k.lower()}" for k in L}
    if long_key and key_idx is not None:
        o[L[key_idx]] += "xxxxxxxx"
    return o

def base(i, part, typ, n):
    return {"id": f"{part}-{i:04d}", "part": part, "type": typ, "difficulty": n % 3 + 1,
            "topic": "office", "source": "original", "explanation": "Because.",
            "status": "draft", "review": {"blind_solve": None, "teacher": None}}

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

FM = {"single": 1, "double": 2, "triple": 3}

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

def mut(fn):
    s = good_reading(); fn(s); return s

def set_(d, k, v): d[k] = v

MUTATIONS = {
    "missing explanation field": lambda s: find(s, "p5").pop("explanation"),
    "empty explanation": lambda s: set_(find(s, "p5"), "explanation", "  "),
    "duplicate id": lambda s: set_(find(s, "p5", 1), "id", find(s, "p5", 0)["id"]),
    "answer not A-D": lambda s: set_(find(s, "p5"), "answer", "E"),
    "repeated option": lambda s: find(s, "p5")["options"].update(B=find(s, "p5")["options"]["A"]),
    "empty option": lambda s: find(s, "p5")["options"].update(C=""),
    "missing option D": lambda s: find(s, "p5")["options"].pop("D"),
    "p5 two blanks": lambda s: set_(find(s, "p5"), "stem", "A ____ and ____ here."),
    "p5 no blank": lambda s: set_(find(s, "p5"), "stem", "No blank here."),
    "type from wrong part": lambda s: set_(find(s, "p5"), "type", "TQ-7-1"),
    "unknown topic": lambda s: set_(find(s, "p5"), "topic", "sports"),
    "source not original": lambda s: set_(find(s, "p5"), "source", "book"),
    "mentions ETS": lambda s: set_(find(s, "p5"), "explanation", "Copied from an ETS test."),
    "difficulty out of range": lambda s: set_(find(s, "p5"), "difficulty", 5),
    "published without reviews": lambda s: set_(find(s, "p5"), "status", "published"),
    "duplicate stem": lambda s: set_(find(s, "p5", 1), "stem", find(s, "p5", 0)["stem"]),
    "only 29 p5 items": lambda s: s.remove(find(s, "p5")),
    "difficulty ladder skewed": lambda s: [x.update(difficulty=1) for x in s if x["part"] == "p5"],
    "answer spread: all A": lambda s: [x.update(answer="A") for x in s if x["part"] == "p5"],
    "key always longest": lambda s: [q["options"].update({q["answer"]: q["options"][q["answer"]] + "xxxxxxxxxx"}) for q in all_questions(s)],
    "p6 marker mismatch": lambda s: set_(find(s, "p6"), "text", "Notice: [1] a [2] b [3] c"),
    "p6 only 3 passages": lambda s: s.remove(find(s, "p6")),
    "p7 document count wrong": lambda s: set_(find(s, "p7", 10), "documents", [{"kind": "email", "text": "x"}]),
    "p7 multi set with 4 questions": lambda s: find(s, "p7", 10)["questions"].pop(),
    "p7 single with 5 questions": lambda s: find(s, "p7", 0)["questions"].extend([q7(99, k) for k in range(2)]),
    "p7 single total 28": lambda s: find(s, "p7", 0)["questions"].pop(),
    "p7 bad format": lambda s: set_(find(s, "p7", 0), "format", "quad"),
}

def main():
    failures = 0
    errs = check(good_reading(), "reading")
    print("valid set:", "PASS" if not errs else f"FAIL {errs[:3]}")
    failures += bool(errs)
    for name, fn in MUTATIONS.items():
        errs = check(mut(fn), "reading")
        ok = bool(errs)
        failures += not ok
        print(f"{'caught' if ok else 'MISSED':7} {name}" + (f"  -> {errs[0]}" if ok else ""))
    print(f"\n{len(MUTATIONS)} defects injected, {failures} problems")
    sys.exit(1 if failures else 0)

main()
