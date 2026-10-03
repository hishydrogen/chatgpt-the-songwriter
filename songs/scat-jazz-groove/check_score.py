"""Musical checks before the checkpoint-2 render; also validate the actual MIDI."""
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

from songwriter import instruments, voice

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("groove_score", HERE / "song.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)
song = score.compose()
allowed = {"Fmaj9": {0, 4, 5, 7, 9}, "F6/9": {0, 2, 5, 7, 9},
           "D7b9": {0, 2, 3, 6, 9}, "Gm9": {2, 5, 7, 9, 10},
           "C13": {0, 2, 4, 7, 9, 10}, "Am7": {0, 4, 7, 9}, "Bbm6": {1, 5, 7, 10}}
for bar, line in enumerate(score.HOOK):
    for pos, pitch, _, _ in line:
        symbol = score.chord_at(bar * 4 + pos)[1]
        assert score.N(pitch) % 12 in allowed[symbol], (bar, pos, pitch, symbol)

for t in song.tracks.values():
    inst = instruments.get_instrument(t.instrument)
    assert inst.available, inst.id
    assert t.notes and all(n.start >= 0 and n.dur > 0 and 0 < n.vel <= 127 for n in t.notes), t.name
    onsets = [(n.pitch, round(n.start, 6)) for n in t.notes]
    assert len(onsets) == len(set(onsets)), (t.name, "duplicate note-on")
    if inst.range and inst.engine != "voice":
        assert all(inst.range[0] <= n.pitch <= inst.range[1] for n in t.notes), (t.name, inst.range)
    if inst.engine == "voice":
        ns = [voice.VNote(song.seconds(n.start), song.seconds(n.start + n.dur),
                         n.pitch, n.lyric, n.vel, n.x) for n in t.notes]
        pieces = voice._plan(ns, voice.bank(inst.path), {**voice.DEFAULTS, **t.opts}, light=True)
        assert len(t.notes) == 147 and len(pieces) >= 147
        assert min(n.pitch for n in t.notes) >= 60 and max(n.pitch for n in t.notes) <= 70
        print(len(ns), "scat notes;", len({p.oto.alias for p in pieces}), "aliases", flush=True)

def signature(t, sec):
    b = sec["beat"]
    return [(round(n.start - b, 6), n.pitch, round(n.dur, 6), n.vel, n.lyric, n.x)
            for n in t.notes if b <= n.start < b + 32]

for i in range(0, 6, 2):
    alone, vocal = song.groove_sections[i:i + 2]
    for t in song.tracks.values():
        if t.instrument.startswith("voice."):
            continue
        assert signature(t, alone) == signature(t, vocal), (alone["version"], t.name, "different band takes")
vox = song.tracks[score.VOICE_LABEL]
vocal_sections = [s for s in song.groove_sections if s["role"] == "vocal"]
assert all(signature(vox, s) == signature(vox, vocal_sections[0]) for s in vocal_sections[1:])

# Exclude tiny onset offsets when finding the written chord. Every sustained
# pitched answer must belong to that chord; the chromatic bass is intentional.
for t in song.tracks.values():
    if not (t.name.startswith("Steinway") or t in [song.tracks[n] for n in
            ("trombone punctuation", "French horn inner voice", "muted trumpet answers", "tenor replies")]):
        continue
    for sec in song.groove_sections:
        for n in t.notes:
            if sec["beat"] <= n.start < sec["beat"] + 32:
                local = round(n.start - sec["beat"], 1)
                symbol = score.chord_at(local)[1]
                assert n.pitch % 12 in allowed[symbol], (t.name, local, n.pitch, symbol)

mf = song.full_midi()
lyric_count = 0
for mt, t in zip(mf.tracks[1:], song.tracks.values()):
    assert all(m.channel == t.channel for m in mt if hasattr(m, "channel")), t.name
    active = defaultdict(int)
    for msg in mt:
        if msg.type == "note_on" and msg.velocity:
            active[msg.note] += 1
        elif msg.type == "note_off" or msg.type == "note_on" and msg.velocity == 0:
            active[msg.note] -= 1
            assert active[msg.note] >= 0, (t.name, "unmatched note-off")
        lyric_count += msg.type == "lyrics"
    assert not any(active.values()), (t.name, "hanging MIDI notes")
assert lyric_count == 147
channels = [t.channel for t in song.tracks.values() if not t.instrument.startswith("drums.")]
assert len(channels) == len(set(channels)), "shared pitched controller channels"
drum_counts = [len(signature(song.tracks["DRSKit kick"], sec)) for sec in song.groove_sections[::2]]
assert len(set(drum_counts)) == 3, "versions must differ in rhythm"

result = {"status": "passed", "selected_instruments": score.SELECTED, "bpm": score.BPM,
          "swing": score.SWING, "tracks": len(song.tracks),
          "notes": sum(len(t.notes) for t in song.tracks.values()), "midi_lyrics": lyric_count,
          "identical_instrumental_repeats": True, "identical_vocal_performances": True,
          "sections": [{**s, "start_s": round(song.seconds(s["beat"]), 2),
                        "end_s": round(song.seconds(s["beat"] + 32), 2)} for s in song.groove_sections]}
(HERE / "score-check.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
