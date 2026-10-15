"""Content gate for TOEIC items: Reading (Phase 2) and Listening scripts (Phase 6).

Usage: python3 scripts/check_toeic.py [--spec none|p1|p2|p3|p4|p5|p6|p7|reading|listening] FILE.json [FILE.json ...]
Exit code 1 if any error is found; warnings never fail the run.
See docs/TOEIC-CONTENT-STANDARDS.md.
"""
import argparse, json, os, re, sys, unicodedata
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LETTERS = ["A", "B", "C", "D"]
TOPICS = {"office", "hr", "finance", "travel", "manufacturing", "retail",
          "dining", "health", "housing", "technology", "marketing", "events"}
STATUSES = {"draft", "reviewed", "published"}
LETTERS3 = ["A", "B", "C"]  # Part 2 has three spoken responses
READING = {"p5", "p6", "p7"}
LISTENING = {"p1", "p2", "p3", "p4"}
PARTS = READING | LISTENING
ACCENTS = {"US", "UK", "AU", "CA"}
GENDERS = {"M", "W"}
FORMATS = {"single": 1, "double": 2, "triple": 3}
REVIEW_VALUES = {None, "pass", "fail"}
MIN_SOLVERS = 3
ETS_RE = re.compile(r"\be\.?\s?t\.?\s?s\b|educational\s+testing")
NONE_OF_ABOVE_RE = re.compile(r"\b(all|none|neither|both)\b.{0,12}\b(above|these|them)\b|\ball of the above\b|\bnone of the above\b")
NEGATIVE_STEM_RE = re.compile(r"\b(not|except)\b")


def catalog_types():
    cat = json.load(open(os.path.join(ROOT, "content/toeic/catalog.json")))
    return {p["id"]: set(p["types"]) for s in cat["sections"] for p in s["parts"]}


def norm(s):
    s = unicodedata.normalize("NFKC", str(s)).lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return " ".join(s.split())


def is_text(v):
    return isinstance(v, str) and v.strip() != ""


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def strings(obj):
    """Every string value (not key) anywhere inside obj."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from strings(v)


def check_question(where, q, part_types, errs, warns, stem_required, letters=LETTERS):
    if not isinstance(q, dict):
        errs.append(f"{where}: question must be an object")
        return False
    if stem_required and not is_text(q.get("stem")):
        errs.append(f"{where}: stem must be non-empty text")
    if not (isinstance(q.get("type"), str) and q["type"] in part_types):
        errs.append(f"{where}: type {q.get('type')!r} not valid for this part")
    opts = q.get("options")
    ok = isinstance(opts, dict) and sorted(opts) == letters
    if not ok:
        errs.append(f"{where}: options must be exactly {', '.join(letters)}")
    else:
        if not all(is_text(opts[k]) for k in letters):
            errs.append(f"{where}: every option must be non-empty text")
        else:
            if len({norm(opts[k]) for k in letters}) != len(letters):
                errs.append(f"{where}: repeated option text")
            if any(NONE_OF_ABOVE_RE.search(opts[k].lower()) for k in letters):
                errs.append(f"{where}: 'all/none/both of the above' style option is not allowed")
    if not (isinstance(q.get("answer"), str) and q["answer"] in letters):
        errs.append(f"{where}: answer must be one of {letters[0]}-{letters[-1]}")
    if is_text(q.get("stem")) and NEGATIVE_STEM_RE.search(q["stem"].lower()):
        warns.append(f"{where}: negative stem (NOT/EXCEPT); keep only if the type needs it")
    return True


def check_voice(where, v, errs):
    if not isinstance(v, dict) or not (isinstance(v.get("accent"), str) and v["accent"] in ACCENTS) or not (isinstance(v.get("gender"), str) and v["gender"] in GENDERS):
        errs.append(f"{where}: needs accent (US, UK, AU or CA) and gender (M or W)")


def check_item(it, types, ids, errs, warns):
    """Validate one item; return (list of question dicts, duplicate key or None)."""
    if not isinstance(it, dict):
        errs.append(f"item {it!r:.40}: must be an object")
        return [], None
    i = it["id"] if is_text(it.get("id")) else "<bad id>"
    part = it.get("part") if isinstance(it.get("part"), str) else None
    for f in ("id", "part", "type", "difficulty", "topic", "source", "provenance",
              "explanation", "status", "review"):
        if f not in it:
            errs.append(f"{i}: missing field {f}")
    if not is_text(it.get("id")):
        errs.append(f"{i}: id must be non-empty text")
    else:
        if it["id"] in ids:
            errs.append(f"{i}: duplicate id")
        ids.add(it["id"])
        if not re.fullmatch(r"p[1-7]-\d{4}", it["id"]) or (part and not it["id"].startswith(part + "-")):
            errs.append(f"{i}: id must look like p5-0001 (p1 to p7) and start with its part")
    if part not in PARTS:
        errs.append(f"{i}: part must be one of {sorted(PARTS)}")
    part_types = types.get(part, set())
    if not is_int(it.get("difficulty")) or it["difficulty"] not in (1, 2, 3):
        errs.append(f"{i}: difficulty must be the integer 1, 2 or 3")
    if not (isinstance(it.get("topic"), str) and it["topic"] in TOPICS):
        errs.append(f"{i}: topic {it.get('topic')!r} not in allowed list")
    if it.get("source") != "original":
        errs.append(f"{i}: source must be 'original'")
    prov = it.get("provenance")
    if not isinstance(prov, dict) or prov.get("method") not in ("human", "ai"):
        errs.append(f"{i}: provenance.method must be 'human' or 'ai'")
    elif prov["method"] == "ai" and not (is_text(prov.get("model")) and is_text(prov.get("prompt_ref"))):
        errs.append(f"{i}: ai provenance needs model and prompt_ref")
    if not is_text(it.get("explanation")):
        errs.append(f"{i}: explanation must be non-empty text")
    status = it.get("status")
    if not (isinstance(status, str) and status in STATUSES):
        errs.append(f"{i}: status must be one of {sorted(STATUSES)}")
    rev = it.get("review")
    if not isinstance(rev, dict):
        errs.append(f"{i}: review must be an object")
        rev = {}
    else:
        for k in ("blind_solve", "blind_solvers", "facts", "teacher"):
            if k not in rev:
                errs.append(f"{i}: review.{k} is missing")
        for k in ("blind_solve", "facts", "teacher"):
            v = rev.get(k)
            if not (v is None or (isinstance(v, str) and v in ("pass", "fail"))):
                errs.append(f"{i}: review.{k} must be null, 'pass' or 'fail'")
        if not is_int(rev.get("blind_solvers", 0)) or rev.get("blind_solvers", 0) < 0:
            errs.append(f"{i}: review.blind_solvers must be a non-negative integer")
    if status in ("reviewed", "published"):
        ok = (rev.get("blind_solve") == "pass" and rev.get("facts") == "pass"
              and rev.get("teacher") == "pass" and is_int(rev.get("blind_solvers"))
              and rev.get("blind_solvers") >= MIN_SOLVERS)
        if not ok:
            errs.append(f"{i}: {status} needs blind_solve, facts and teacher = pass and "
                        f"blind_solvers >= {MIN_SOLVERS}")
    if any(ETS_RE.search(unicodedata.normalize("NFKC", " ".join(s.lower().split())))
           for s in strings({k: v for k, v in it.items() if k != "id"})):
        errs.append(f"{i}: mentions ETS (originality rule)")
    if not (isinstance(it.get("type"), str) and it["type"] in part_types) and part in PARTS:
        errs.append(f"{i}: item type {it.get('type')!r} not valid for {part}")

    qs, key = [], None
    if part in LISTENING:
        tm = it.get("timing")
        if not isinstance(tm, dict) or not isinstance(tm.get("audioSeconds"), (int, float)) or isinstance(tm.get("audioSeconds"), bool) or not tm.get("audioSeconds", 0) > 0:
            errs.append(f"{i}: timing.audioSeconds must be a positive number")
        if not (it.get("audio") is None or is_text(it.get("audio"))):
            errs.append(f"{i}: audio must be null (not produced yet) or the audio file path")
        if status == "published" and not is_text(it.get("audio")):
            errs.append(f"{i}: a Listening item cannot be published without its audio file")
    if part == "p1":
        photo = it.get("photo")
        if not isinstance(photo, dict) or not is_text(photo.get("brief")):
            errs.append(f"{i}: p1 needs photo.brief (what the picture shows, for the photographer)")
        check_voice(i, it.get("speaker"), errs)
        if check_question(i, {**it, "stem": "x"}, part_types, errs, warns, False):
            qs.append(it)
        key = norm(photo.get("brief")) if isinstance(photo, dict) and is_text(photo.get("brief")) else None
    elif part == "p2":
        if not is_text(it.get("prompt")):
            errs.append(f"{i}: p2 needs the spoken prompt (question or statement)")
        sp = it.get("speakers")
        if not isinstance(sp, dict):
            errs.append(f"{i}: p2 needs speakers.prompt and speakers.response")
        else:
            check_voice(f"{i} prompt", sp.get("prompt"), errs); check_voice(f"{i} response", sp.get("response"), errs)
        if check_question(i, {**it, "stem": "x"}, part_types, errs, warns, False, LETTERS3):
            qs.append(it)
        key = norm(it["prompt"]) if is_text(it.get("prompt")) else None
    elif part in ("p3", "p4"):
        script, questions = it.get("script"), it.get("questions")
        words = 0
        if not isinstance(script, list) or not script:
            errs.append(f"{i}: {part} needs a script (list of spoken segments)")
            script = []
        speakers = set()
        for k, seg in enumerate(script, 1):
            if not isinstance(seg, dict) or not is_text(seg.get("speaker")) or not is_text(seg.get("text")):
                errs.append(f"{i}: script segment {k} needs speaker and text")
                continue
            check_voice(f"{i} segment {k}", seg, errs)
            speakers.add(seg["speaker"]); words += len(seg["text"].split())
        if part == "p3" and script and (len(script) < 4 or len(speakers) < 2):
            errs.append(f"{i}: a p3 conversation needs at least 4 turns and 2 speakers")
        if part == "p4" and script and len(speakers) != 1:
            errs.append(f"{i}: a p4 talk has exactly one speaker")
        if script and not 60 <= words <= 200:
            warns.append(f"{i}: script is {words} words (indicative range 60-200)")
        g = it.get("graphic")
        if g is not None and (not isinstance(g, dict) or not is_text(g.get("kind")) or not isinstance(g.get("rows"), list) or not g["rows"]
                              or not all(isinstance(r, list) and r and all(is_text(c) for c in r) for r in g["rows"])):
            errs.append(f"{i}: graphic, when present, needs kind and non-empty rows of text cells")
        if not isinstance(questions, list):
            errs.append(f"{i}: {part} needs a questions list"); questions = []
        if len(questions) != 3:
            errs.append(f"{i}: {part} needs exactly 3 questions, has {len(questions)}")
        stems = []
        for k, q in enumerate(questions, 1):
            if check_question(f"{i}#{k}", q, part_types, errs, warns, True):
                qs.append(q)
                if is_text(q.get("stem")):
                    stems.append(norm(q["stem"]))
        if len(set(stems)) != len(stems):
            errs.append(f"{i}: repeated question stem inside one {part} set")
        key = norm(" ".join(seg["text"] for seg in script if isinstance(seg, dict) and is_text(seg.get("text")))) or None
    elif part == "p5":
        stem = it.get("stem")
        if not is_text(stem) or stem.count("____") != 1:
            errs.append(f"{i}: p5 stem must be text with exactly one ____")
        if check_question(i, {**it, "stem": stem if is_text(stem) else ""}, part_types, errs, warns, False):
            qs.append(it)
        key = norm(stem) if is_text(stem) else None
    elif part == "p6":
        text, questions = it.get("text"), it.get("questions")
        if not is_text(text) or not isinstance(questions, list):
            errs.append(f"{i}: p6 needs text and a questions list")
            text, questions = "", []
        else:
            nwords = len(text.split())
            if not 30 <= nwords <= 200:
                warns.append(f"{i}: p6 text is {nwords} words (indicative range 30-200)")
        blanks = [q.get("blank") for q in questions if isinstance(q, dict)]
        markers = sorted(int(m) for m in re.findall(r"\[(\d+)\]", text))
        if markers != [1, 2, 3, 4] or sorted(b for b in blanks if is_int(b)) != [1, 2, 3, 4] or len(blanks) != 4:
            errs.append(f"{i}: p6 needs markers [1]-[4] once each in the text, matching 4 questions with blank 1-4")
        for k, q in enumerate(questions, 1):
            if check_question(f"{i}#{k}", q, part_types, errs, warns, False):
                qs.append(q)
        key = norm(text) if text else None
    elif part == "p7":
        fmt, docs, questions = it.get("format"), it.get("documents"), it.get("questions")
        if not isinstance(docs, list) or not isinstance(questions, list):
            errs.append(f"{i}: p7 needs documents and questions lists")
            docs, questions = [], []
        if not (isinstance(fmt, str) and fmt in FORMATS) or len(docs) != FORMATS.get(fmt, -1):
            errs.append(f"{i}: p7 format must be single/double/triple with 1/2/3 documents")
        for k, d in enumerate(docs, 1):
            if not isinstance(d, dict) or not is_text(d.get("kind")) or not is_text(d.get("text")):
                errs.append(f"{i}: document {k} needs non-empty kind and text")
            else:
                nwords = len(d["text"].split())
                if not 20 <= nwords <= 400:
                    warns.append(f"{i}: document {k} is {nwords} words (indicative range 20-400)")
        texts = [norm(d["text"]) for d in docs if isinstance(d, dict) and is_text(d.get("text"))]
        if len(set(texts)) != len(texts):
            errs.append(f"{i}: two documents have the same text")
        n = len(questions)
        if fmt == "single" and not 2 <= n <= 4:
            errs.append(f"{i}: single passage needs 2-4 questions, has {n}")
        if fmt in ("double", "triple") and n != 5:
            errs.append(f"{i}: multiple-passage set needs exactly 5 questions, has {n}")
        stems = []
        for k, q in enumerate(questions, 1):
            if check_question(f"{i}#{k}", q, part_types, errs, warns, True):
                qs.append(q)
                if is_text(q.get("stem")):
                    stems.append(norm(q["stem"]))
        if len(set(stems)) != len(stems):
            errs.append(f"{i}: repeated question stem inside one passage set")
        key = " | ".join(texts) if texts else None
    return qs, (part, key) if key else None


def spread_checks(name, qs, errs):
    """Key letter spread and key-length bias for one file; four-option and three-option questions are judged separately."""
    for letters in (LETTERS, LETTERS3):
        _spread(name, [q for q in qs if isinstance(q.get("options"), dict) and sorted(q["options"]) == letters], letters, errs)


def _spread(name, qs, letters, errs):
    valid = [q for q in qs if q.get("answer") in letters and all(is_text(v) for v in q["options"].values())]
    n, k = len(valid), len(letters)
    if n < 12:
        return
    cnt = Counter(q["answer"] for q in valid)
    lo, hi = (0.10, 0.40) if k == 4 else (0.20, 0.50)
    for L in letters:
        share = cnt[L] / n
        if n >= 24 and not lo <= share <= hi:
            errs.append(f"{name}: spread: key {L} is {share:.0%} of {k}-option keys (allowed {lo:.0%}-{hi:.0%})")
        if n < 24 and (cnt[L] == 0 or share > (0.50 if k == 4 else 0.60)):
            errs.append(f"{name}: spread: key {L} is {cnt[L]} of {n} {k}-option keys (each letter at least once, none dominant)")
    longest = shortest = 0
    for q in valid:
        lens = {k: len(v.strip()) for k, v in q["options"].items()}
        mx, mn = max(lens.values()), min(lens.values())
        if lens[q["answer"]] == mx and list(lens.values()).count(mx) == 1:
            longest += 1
        if lens[q["answer"]] == mn and list(lens.values()).count(mn) == 1:
            shortest += 1
    if longest / n > 0.35:
        errs.append(f"{name}: spread: key is the longest option in {longest/n:.0%} of questions (max 35%)")
    if shortest / n > 0.35:
        errs.append(f"{name}: spread: key is the shortest option in {shortest/n:.0%} of questions (max 35%)")


def strings_voices(it):
    """Accents used by one Listening item."""
    out = []
    for v in ([it.get("speaker")] + list((it.get("speakers") or {}).values()) + list(it.get("script") or [])):
        if isinstance(v, dict) and isinstance(v.get("accent"), str) and v["accent"] in ACCENTS:
            out.append(v["accent"])
    return out


def spec_checks(spec, items, errs):
    ok = [x for x in items if isinstance(x, dict)]
    by = {p: [x for x in ok if x.get("part") == p] for p in PARTS}
    qlen = lambda x: len(x["questions"]) if isinstance(x.get("questions"), list) else 0
    if spec in ("p1", "listening") and len(by["p1"]) != 6:
        errs.append(f"spec: p1 needs 6 items, has {len(by['p1'])}")
    if spec in ("p2", "listening"):
        if len(by["p2"]) != 25:
            errs.append(f"spec: p2 needs 25 items, has {len(by['p2'])}")
        lad = Counter(x.get("difficulty") for x in by["p2"])
        for d in (1, 2, 3):
            if not 6 <= lad[d] <= 11:
                errs.append(f"spec: p2 difficulty {d} has {lad[d]} items (needs 6 to 11)")
    if spec in ("p3", "listening"):
        q = sum(qlen(x) for x in by["p3"])
        if len(by["p3"]) != 13 or q != 39:
            errs.append(f"spec: p3 needs 13 conversations / 39 questions, has {len(by['p3'])} / {q}")
        if sum(1 for x in by["p3"] if x.get("graphic")) < 2:
            errs.append("spec: p3 needs at least 2 conversations with a graphic")
        if sum(1 for x in by["p3"] if isinstance(x.get("script"), list) and len({s.get("speaker") for s in x["script"] if isinstance(s, dict)}) >= 3) < 1:
            errs.append("spec: p3 needs at least 1 three-speaker conversation")
    if spec in ("p4", "listening"):
        q = sum(qlen(x) for x in by["p4"])
        if len(by["p4"]) != 10 or q != 30:
            errs.append(f"spec: p4 needs 10 talks / 30 questions, has {len(by['p4'])} / {q}")
        if sum(1 for x in by["p4"] if x.get("graphic")) < 2:
            errs.append("spec: p4 needs at least 2 talks with a graphic")
    if spec == "listening":
        acc = Counter()
        for x in ok:
            if x.get("part") in LISTENING:
                for v in strings_voices(x):
                    acc[v] += 1
        if len(acc) < 3:
            errs.append(f"spec: a Listening set needs at least 3 of the 4 accents, has {sorted(acc)}")
    if spec in ("p5", "reading"):
        if len(by["p5"]) != 30:
            errs.append(f"spec: p5 needs 30 items, has {len(by['p5'])}")
        lad = Counter(x.get("difficulty") for x in by["p5"])
        for d in (1, 2, 3):
            if not 8 <= lad[d] <= 12:
                errs.append(f"spec: p5 difficulty {d} has {lad[d]} items (needs 8 to 12)")
    if spec in ("p6", "reading"):
        q = sum(qlen(x) for x in by["p6"])
        if len(by["p6"]) != 4 or q != 16:
            errs.append(f"spec: p6 needs 4 passages / 16 questions, has {len(by['p6'])} / {q}")
    if spec in ("p7", "reading"):
        single = sum(qlen(x) for x in by["p7"] if x.get("format") == "single")
        multi = [x for x in by["p7"] if x.get("format") in ("double", "triple")]
        mq = sum(qlen(x) for x in multi)
        if single != 29:
            errs.append(f"spec: p7 single-passage questions must be 29, has {single}")
        if len(multi) != 5 or mq != 25:
            errs.append(f"spec: p7 needs 5 multiple-passage sets / 25 questions, has {len(multi)} / {mq}")


def check_files(files, spec="none"):
    """files: dict of name -> list of items. Returns (errors, warnings)."""
    errs, warns, ids, dupes = [], [], set(), Counter()
    types = catalog_types()
    all_items = []
    for name, items in files.items():
        file_qs = []
        if not isinstance(items, list):
            errs.append(f"{name}: 'items' must be a list")
            continue
        for it in items:
            qs, key = check_item(it, types, ids, errs, warns)
            file_qs.extend(q for q in qs if isinstance(q, dict))
            if key:
                dupes[key] += 1
            all_items.append(it)
        spread_checks(name, file_qs, errs)
    for (part, k), n in dupes.items():
        if n > 1:
            errs.append(f"duplicate {part} content appears {n} times: {k[:50]!r}")
    if spec != "none":
        spec_checks(spec, all_items, errs)
    return errs, warns


def check(items, spec="none"):
    """Convenience for one in-memory file; returns errors only."""
    return check_files({"<memory>": items}, spec)[0]


def load(path):
    try:
        data = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as e:
        return None, f"{path}: cannot read JSON ({e})"
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        return None, f"{path}: top level must be an object with an 'items' list"
    return data["items"], None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="none", choices=["none", "p1", "p2", "p3", "p4", "p5", "p6", "p7", "reading", "listening"])
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    files, load_errs = {}, []
    for f in a.files:
        items, err = load(f)
        if err:
            load_errs.append(err)
        else:
            files[f] = items
    errs, warns = check_files(files, a.spec)
    errs = load_errs + errs
    for w in warns:
        print("warning:", w)
    count = sum(len(v) for v in files.values())
    print("\n".join(errs) if errs else f"OK: {count} items, spec={a.spec}")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
