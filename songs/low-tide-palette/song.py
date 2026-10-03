"""Checkpoint 1: an original late-1960s blues-rock instrumental palette.

The reference is Come Together, supplied as the 2019 remix. No reference audio,
melody or bass riff is used here. Nine candidates repeat the same four-bar musical
material. A fifth bar leaves space between candidates. Titles are working titles.
"""
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from songwriter.song import Song  # noqa: E402

BPM = 86
STEP = 20
PHRASE = 16
SEGMENTS = [
    ("drums A: close and damped", "drums", "close"),
    ("drums B: vintage mic and tape", "drums", "vintage"),
    ("bass A: rounded short-scale", "bass", "bass.babyblue"),
    ("bass B: firm finger bass", "bass", "bass.darkblack"),
    ("keys A: mellow Rhodes", "keys", "epiano.rhodes"),
    ("keys B: woody Wurlitzer", "keys", "epiano.wurlitzer"),
    ("lead A: rounded clean guitar", "lead", "guitar.black_twang"),
    ("lead B: guitar on the amp edge", "lead", "guitar.emily_di"),
    ("lead C: electric piano melody", "lead", "epiano.rhodes"),
]

# Entirely new notes and phrasing: Em7 | Em7 | Am7 | B7.
# Each event is relative to the beginning of the same four-bar audition phrase.
BASS = [
    ("E2", .125, .46, 96), ("B1", 1.25, .30, 86), ("D2", 2.25, .40, 92),
    ("G2", 3.25, .23, 82), ("E2", 3.75, .16, 85),
    ("E2", 4.0, .50, 98), ("G2", 5.5, .30, 84), ("B2", 6.25, .30, 89),
    ("D2", 7.0, .35, 86), ("E2", 7.5, .35, 92),
    ("A1", 8.125, .48, 97), ("E2", 9.5, .28, 88), ("G2", 10.25, .25, 83),
    ("C2", 11.0, .30, 87), ("A1", 11.75, .17, 84),
    ("B1", 12.0, .45, 98), ("F#2", 13.25, .30, 88), ("A2", 14.25, .25, 84),
    ("D#2", 15.0, .30, 90), ("B1", 15.5, .25, 87),
]
LEAD = [
    ("B3", .5, .35, 88), ("D4", 1.5, .28, 96), ("E4", 2.25, .5, 100), ("G4", 3.25, .30, 87),
    ("F#4", 4.25, .25, 89), ("E4", 4.75, .75, 97), ("B3", 6.25, .25, 86),
    ("D4", 7.0, .28, 91), ("E4", 7.5, .35, 98),
    ("G4", 8.75, .40, 94), ("A4", 9.5, .35, 97), ("C5", 10.25, .35, 101), ("B4", 11.0, .40, 94),
    ("A4", 12.5, .25, 90), ("F#4", 13.25, .40, 94), ("D#4", 14.0, .45, 91), ("B3", 15.0, .45, 89),
]
VOICINGS = [[55, 59, 62, 64], [55, 59, 62, 66], [55, 60, 64, 69], [57, 63, 66, 71]]
# The F# in the second Em7 voicing is a ninth, not a conflicting semitone.


def timing(rng, beat, bias_ms=0, spread_ms=4):
    return beat + rng.gauss(bias_ms, spread_ms) * BPM / 60000


def put_bass(t, start):
    rng = random.Random(469)
    for p, b, d, v in BASS:
        t.note(p, start + timing(rng, b, 1, 5), d, v)
    t.cc(21, 0, start).cc(113, 0, start).cc(114, 0, start)


def put_keys(t, start):
    rng = random.Random(669)
    for bar, chord in enumerate(VOICINGS):
        for pos, dur, vel in ((.5, .85, 61), (2.5, .55, 55)):
            beat = start + bar * 4 + timing(rng, pos, 3, 5)
            t.notes_at(chord, beat, dur, vel, strum=.016)
            t.sustain(beat, beat + dur - .03)


def put_lead(t, start):
    rng = random.Random(869)
    for p, b, d, v in LEAD:
        t.note(p, start + timing(rng, b, 3, 6), d, v)
    if t.instrument.startswith("guitar."):
        # A small, human bend on two held notes, far from a modern dive or sweep.
        for b in (4.75, 11.0):
            t.bend(0, start + b).bend(480, start + b + .12).bend(0, start + b + .30)
        t.cc(70, 12, start)


def drum_tracks(song, prefix, mode):
    result = {v: song.track(f"{prefix} | {v}", "drums.virtuosity") for v in ("kick", "snare", "hats", "toms")}
    controls = {71: 127, 76: 58, 81: 57, 86: 58, 101: 127, 102: 18, 103: 127,
                104: 15, 105: 26, 106: 24, 107: 0, 109: 0, 111: 18}
    if mode == "vintage":
        controls.update({71: 112, 105: 42, 109: 8, 111: 96})
    for voice, t in result.items():
        for cc, value in controls.items():
            t.cc(cc, value, 0)
        if voice == "hats" and mode == "close":
            # The hats have no close microphone. Give their dedicated overhead
            # stem enough level to clear the loudness meter's absolute gate.
            t.cc(105, 100, 0).cc(111, 0, 0)
    return result


def put_drums(kit, start):
    rng = random.Random(969)
    kicks = [(0, 2.5), (0, 2.25, 3.5), (.25, 2.5), (0, 2.25)]
    for bar in range(4):
        b0 = start + bar * 4
        for pos in kicks[bar]:
            kit["kick"].hit("kick", b0 + timing(rng, pos, 0, 3), 98 if pos < 1 else 89)
        for pos in (1, 3):
            kit["snare"].hit("snare", b0 + timing(rng, pos, 9, 4), 95 if pos == 1 else 91)
        kit["snare"].hit("snare", b0 + timing(rng, 2.75, 5, 5), 40)
        # Sparse closed hats: enough motion, with the low toms carrying the reply.
        for pos, vel in ((0, 57), (.5, 37), (1, 52), (2, 57), (2.5, 39), (3, 49)):
            kit["hats"].hit("hh_closed", b0 + timing(rng, pos, 2, 3), vel)
        if bar in (1, 3):
            for pos, hit, vel in ((3.25, "tom_high", 72), (3.625, "tom_low", 78)):
                kit["toms"].hit(hit, b0 + timing(rng, pos, 6, 4), vel)


def bass_strip():
    return {"gain": -2, "eq": [("hpf", 38), ("bell", 100, 1.2, .8), ("bell", 330, -2.5, 1),
                                ("lpf", 2600, 1)],
            "comp": {"threshold": -22, "ratio": 2.8, "attack": 22, "release": 155},
            "tape": {"drive_db": 3, "bump_db": .4}, "mono": True}


def keys_strip(gain=-5):
    return {"gain": gain, "eq": [("hpf", 130), ("bell", 330, -3.5, 1.1), ("lpf", 6400, 1)],
            "tape": {"drive_db": 2.5, "bump_db": 0}, "mono": True, "pan": .22,
            "sends": {"small_plate": -22}}


def lead_strip(instrument, gain=1):
    cfg = {"gain": gain, "eq": [("hpf", 155), ("bell", 380, -3, 1), ("lpf", 6200, 1)],
           "comp": {"threshold": -23, "ratio": 2.2, "attack": 18, "release": 130},
           "tape": {"drive_db": 3, "bump_db": 0}, "mono": True, "pan": -.20,
           "sends": {"small_plate": -18}}
    if instrument == "guitar.emily_di":
        cfg["amp"] = [{"type": "amp", "PreGain": -1, "Distortion": 20, "Drive": .22,
                       "model": 0, "t_model": 8, "c_model": 9, "Presence": 3}]
    elif instrument == "guitar.black_twang":
        cfg["tube"] = {"drive": 1.3, "bass": 4, "mids": 6, "treble": 4}
    return cfg


def add_kit_mix(tracks, prefix, mode):
    c = {
        "kick": {"gain": -3, "eq": [("hpf", 33), ("bell", 80, 1, 1), ("bell", 280, -3, 1),
                                    ("lpf", 4200, 1)]},
        "snare": {"gain": -5.3, "eq": [("hpf", 100), ("bell", 230, 2, 1), ("bell", 750, -2, 1.1),
                                      ("hshelf", 4600, -3.5), ("lpf", 7200, 1)]},
        "hats": {"gain": -16, "eq": [("hpf", 450), ("lpf", 8500, 1)], "pan": -.13},
        "toms": {"gain": -7, "eq": [("hpf", 55), ("bell", 420, -2, 1), ("lpf", 5700, 1)], "pan": -.10},
    }
    for v, cfg in c.items():
        cfg.update({"mono": True, "tape": {"drive_db": 3 if mode == "close" else 5, "bump_db": .2}})
        if v in ("snare", "toms"):
            cfg["sends"] = {"tight_room": -30 if mode == "close" else -23}
        tracks[f"{prefix} | {v}"] = cfg


def compose():
    s = Song("Low Tide - Checkpoint 1", bpm=BPM, key="Em")
    bed_kit = drum_tracks(s, "bed drums", "close")
    bed_bass = s.track("bed bass", "bass.babyblue")
    bed_keys = s.track("bed keys", "epiano.rhodes")
    bed_lead = s.track("bed guitar", "guitar.black_twang")
    tracks = {"bed bass": bass_strip(), "bed keys": keys_strip(-9),
              "bed guitar": lead_strip("guitar.black_twang", -11)}
    add_kit_mix(tracks, "bed drums", "close")
    for i, (label, category, instrument) in enumerate(SEGMENTS):
        b0 = i * STEP
        s.marker(b0, label)
        if category != "drums":
            put_drums(bed_kit, b0)
        if category != "bass":
            put_bass(bed_bass, b0)
        if category != "keys":
            put_keys(bed_keys, b0)
        if category != "lead":
            put_lead(bed_lead, b0)
        if category == "drums":
            kit = drum_tracks(s, label, instrument)
            put_drums(kit, b0)
            add_kit_mix(tracks, label, instrument)
        else:
            t = s.track(label, instrument)
            if category == "bass":
                put_bass(t, b0)
                tracks[label] = bass_strip()
            elif category == "keys":
                put_keys(t, b0)
                tracks[label] = keys_strip(-3)
            else:
                put_lead(t, b0)
                tracks[label] = lead_strip(instrument)
    trims_file = Path(__file__).with_name("loudness_trims.json")
    trims = json.loads(trims_file.read_text()) if trims_file.exists() else {}
    for label, _, _ in SEGMENTS:
        trim = trims.get(label, 0)
        for name, cfg in tracks.items():
            if name == label or name.startswith(label + " |"):
                cfg["gain"] += trim
    s.length_beats = len(SEGMENTS) * STEP
    s.mix = {"tracks": tracks,
             "fx": {"tight_room": {"type": "reverb", "kind": "room", "decay": .32, "predelay": 3,
                                   "hpf": 220, "lpf": 5000, "width_pct": 55},
                    "small_plate": {"type": "reverb", "kind": "plate", "decay": .85, "predelay": 22,
                                    "hpf": 250, "lpf": 4300, "width_pct": 60}},
             "master": {"glue": {"threshold": -19, "ratio": 1.6, "attack": 30, "release": 180},
                        "target_lufs": -14, "ceiling": -1, "mono_below": 150}}
    for t in s.tracks.values():
        inst_range = (28, 67) if t.instrument.startswith("bass.") else (0, 127)
        assert all(inst_range[0] <= n.pitch <= inst_range[1] for n in t.notes), t.name
        assert all(n.start + n.dur < s.end_beat for n in t.notes), t.name
    return s


if __name__ == "__main__":
    s = compose()
    for beat, label in s.markers:
        print(f"{s.seconds(beat):6.2f}s  {label}")
