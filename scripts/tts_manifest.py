"""Timing and text-to-speech manifest for TOEIC Listening sets.

Usage:
  python3 scripts/tts_manifest.py --timing SET.json [SET.json ...]      # write timing.audioSeconds into each item (in place)
  python3 scripts/tts_manifest.py --manifest OUT.json SET.json [...]    # one manifest line per spoken segment, for the TTS service

The pause model is indicative and documented in docs/AUDIO-PRODUCTION.md. Check it against ETS's published sample test before production.
"""
import argparse, json, sys

WORDS_PER_SECOND = 2.6
PAUSE = {"p1": {"between": 1.0, "answer": 5.0}, "p2": {"between": 1.0, "answer": 5.0}, "p3": {"question": 8.0}, "p4": {"question": 8.0}}
NARRATOR = {"accent": "US", "gender": "W"}
LETTERS = "ABCD"


def secs(text):
    return len(str(text).split()) / WORDS_PER_SECOND


def segments(set_id, it):
    """Spoken segments of one item, in order, each with the voice and the pause that follows it."""
    i, part, out = it["id"], it["part"], []
    add = lambda seq, voice, text, pause, role: out.append({"set": set_id, "item": i, "seq": seq, "voice": {"accent": voice["accent"], "gender": voice["gender"]}, "text": text, "pauseAfterSeconds": pause, "role": role})
    if part == "p1":
        add(0, NARRATOR, f"Number {int(i.split('-')[1])}. Look at the picture.", 1.5, "direction")
        letters = sorted(it["options"])
        for n, L in enumerate(letters, 1):
            add(n, it["speaker"], f"{L}. {it['options'][L]}", PAUSE["p1"]["answer"] if n == len(letters) else PAUSE["p1"]["between"], "option")
    elif part == "p2":
        add(0, NARRATOR, f"Number {int(i.split('-')[1])}.", 1.0, "direction")
        add(1, it["speakers"]["prompt"], it["prompt"], 1.0, "prompt")
        letters = sorted(it["options"])
        for n, L in enumerate(letters, 2):
            add(n, it["speakers"]["response"], f"{L}. {it['options'][L]}", PAUSE["p2"]["answer"] if n == len(letters) + 1 else PAUSE["p2"]["between"], "option")
    else:
        seq = 0
        for seg in it["script"]:
            add(seq, seg, seg["text"], 0.6, "script"); seq += 1
        for n, q in enumerate(it["questions"], 1):
            add(seq, NARRATOR, f"Question {n}. {q['stem']}", PAUSE[part]["question"], "question"); seq += 1
    return out


def audio_seconds(set_id, it):
    return round(sum(secs(s["text"]) + s["pauseAfterSeconds"] for s in segments(set_id, it)), 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timing", action="store_true", help="write timing.audioSeconds into each set file")
    ap.add_argument("--manifest", help="write the TTS manifest to this JSON file")
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    manifest, total = [], 0.0
    for f in a.files:
        d = json.load(open(f, encoding="utf-8"))
        for it in d["items"]:
            if it.get("part") not in ("p1", "p2", "p3", "p4"):
                continue
            t = audio_seconds(d["id"], it); total += t
            if a.timing:
                it["timing"] = {**(it.get("timing") or {}), "audioSeconds": t}
            manifest += segments(d["id"], it)
        if a.timing:
            json.dump(d, open(f, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    if a.manifest:
        json.dump({"wordsPerSecond": WORDS_PER_SECOND, "pauses": PAUSE, "narrator": NARRATOR, "segments": manifest}, open(a.manifest, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"{len(manifest)} segments, about {total/60:.1f} minutes of audio")


if __name__ == "__main__":
    main()
