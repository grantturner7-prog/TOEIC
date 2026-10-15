# Audio production for TOEIC Listening (Phase 6)

Decision (2026-10-14): a mix. Text-to-speech, reviewed by the teacher, for practice sets; recorded voices for mock tests.

## From script to file
1. Scripts live in the IELTS repo under `content/toeic/sets/p1-set-1.json` to `p4-set-1.json`, checked by `scripts/check_toeic.py --spec listening`.
2. `python3 scripts/tts_manifest.py --manifest manifest.json <set files>` writes one line per spoken segment: set, item, sequence, voice (accent and gender), text, pause after. Feed these to the text-to-speech service, one voice per accent and gender (8 voices in all, plus the narrator).
3. Join each item's segments into one file with the pauses below, export mono MP3 at 64 kbps (or AAC), and save it as `media/toeic/<set>/<item>.mp3`. Set the item's `audio` field to that path.
4. Check the file length is within 20% of `timing.audioSeconds`; `python3 scripts/tts_manifest.py --timing` recomputes the estimate after any script edit.
5. Teacher listens to a sample of each part (gate: script review), then the set can move from `audio: "pending"` to playable.

## Pause model (indicative; verify against the ETS sample test before production)
| Part | Spoken order | Pauses |
|---|---|---|
| 1 | "Number N. Look at the picture." then statements A to D | 1.5 s after the direction, 1 s between statements, 5 s to answer |
| 2 | "Number N." then the prompt, then responses A to C | 1 s after the direction and the prompt, 1 s between responses, 5 s to answer |
| 3 and 4 | the conversation or talk, then "Question N." with each stem | 0.6 s between turns, 8 s after each question |
Speech rate assumed: 2.6 words a second.

## Voices
- Accents: US, UK, AU, CA (the four the test uses), each in M and W. The narrator is US W.
- A listening set must use at least three accents (checked by the content checker).
- Licensing: confirm the text-to-speech service allows commercial use of the output in a paid course before producing anything that will be sold. Record the service, voice names and licence terms in `docs/audit/toeic/phase-6b.md`.

## Photos (Part 1)
Each Part 1 item carries `photo.brief`. Source a photo that matches it with a licence allowing commercial use, or take one. The teacher confirms the key statement describes the photo and no distractor does. Store as `media/toeic/p1-set-1/<item>.jpg` and set `photo.file`.

## Not produced here
This environment cannot produce audio or photos. Phase 6a delivers scripts, timings, the manifest and the player state "audio coming soon"; Phase 6b (after production) wires the files in and runs the phone and LINE-browser playback checks.
